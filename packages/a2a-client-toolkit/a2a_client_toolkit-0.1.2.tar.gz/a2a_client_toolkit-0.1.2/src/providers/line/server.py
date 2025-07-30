import json

import a2a.types as a2a
import linebot.v3 as line  # type: ignore[reportMissingImports]
import linebot.v3.messaging as line_messaging  # type: ignore[reportMissingImports]
import linebot.v3.webhooks as line_webhook  # type: ignore[reportMissingImports]
from fastapi import FastAPI, Request, Response
from linebot.v3.messaging import (  # type: ignore[reportMissingImports]
    TextMessage,
)
from pydantic import BaseModel, ConfigDict
from starlette.staticfiles import StaticFiles

from client.worker import A2AClientWorker  # type: ignore[reportMissingImports]
from providers.line.types import LineEventContext, LineUserID
from providers.line.user_state import UserState, UserStateStore

from .sender import ReplyAndPushLineMessageSender


class LineServerConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    line_messaging_config: line_messaging.Configuration
    line_channel_secret: str


class LineServer:
    def __init__(self, config: LineServerConfig, worker: A2AClientWorker, user_state_store: UserStateStore) -> None:
        self.line_messaging_config = config.line_messaging_config
        self.parser = line.WebhookParser(config.line_channel_secret)
        self.worker = worker
        self.user_state_store = user_state_store

    async def callback(self, request: Request) -> Response:
        # get X-Line-Signature header value
        signature = request.headers.get("X-Line-Signature", "")

        # get request body as text
        body = await request.body()
        body_str = body.decode()

        events: list[line.webhook.Event] = self.parser.parse(body_str, signature)  # type: ignore[reportUnknownReturnType]
        for event in events:
            if isinstance(event, line_webhook.MessageEvent):
                await self._handle_message(event)
            elif isinstance(event, line_webhook.PostbackEvent):
                await self._handle_postback(event)
            else:
                # TODO(@ryunosuke): handle other events
                raise ValueError(f"unsupported event: {event.type}")

        return Response(status_code=200)

    def _line_message_to_a2a_message(self, content: line_webhook.MessageContent) -> a2a.Message:
        if isinstance(content, line_webhook.TextMessageContent):
            return a2a.Message(
                role=a2a.Role.user,
                parts=[
                    a2a.Part(a2a.TextPart(text=content.text)),
                ],
                messageId=f"line-message-{content.id}",
            )
        # if isinstance(content, line.FileMessageContent):
        # if isinstance(content, line.ImageMessageContent):
        # if isinstance(content, line.VideoMessageContent):
        # if isinstance(content, line.AudioMessageContent):
        # if isinstance(content, line.LocationMessageContent):
        # if isinstance(content, line.StickerMessageContent):

        raise ValueError(f"unsupported message content: {content.type}")

    async def _handle_message(self, event: line_webhook.MessageEvent) -> None:
        if not event.source or not isinstance(event.source, line_webhook.UserSource) or not event.source.user_id:
            raise ValueError("only single user conversation is supported")

        line_user_id = LineUserID(raw=event.source.user_id)

        reply_token = event.reply_token
        if reply_token is None:
            raise ValueError("reply_token is not set")

        user_state = await self.user_state_store.get(line_user_id.general())

        user_message = self._line_message_to_a2a_message(event.message)
        user_message.taskId = user_state.task_id
        user_message.contextId = user_state.context_id

        sender = ReplyAndPushLineMessageSender(
            reply_token=reply_token,
            target_user_id=line_user_id.raw,
            configuration=self.line_messaging_config,
            reply_message_count=0,
        )

        await self.worker.on_user_message(
            context=LineEventContext(line_user_id=line_user_id, sender=sender),
            user_message=user_message,
        )

    async def _handle_postback(self, event: line_webhook.PostbackEvent) -> None:
        if not event.source or not isinstance(event.source, line_webhook.UserSource) or not event.source.user_id:
            raise ValueError("only single user conversation is supported")

        line_user_id = LineUserID(raw=event.source.user_id)
        postback_data = event.postback.data

        sender = ReplyAndPushLineMessageSender(
            reply_token=event.reply_token or "",
            target_user_id=line_user_id.raw,
            configuration=self.line_messaging_config,
            reply_message_count=5,
        )

        try:
            data = json.loads(postback_data)

            if data.get("action") == "complete_task":
                await self.user_state_store.set(line_user_id.general(), UserState(task_id=None, context_id=None))
                await sender.send([TextMessage(text="タスクを完了しました。新しいタスクを開始できます。", quickReply=None, quoteToken=None)])
            else:
                await sender.send([TextMessage(text="不明なアクションです。", quickReply=None, quoteToken=None)])

        except json.JSONDecodeError:
            await sender.send([TextMessage(text="不明なアクションです。", quickReply=None, quoteToken=None)])

    def build(self) -> FastAPI:
        app = FastAPI()
        app.post("/callback")(self.callback)
        app.mount("/files", StaticFiles(directory="public/files"), name="files")
        return app
