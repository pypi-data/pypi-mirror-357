import base64
import json
from collections.abc import AsyncGenerator
from uuid import uuid4

import a2a.types as a2a
import linebot.v3.messaging as line  # type: ignore[reportMissingImports]

from a2a_client_toolkit.handler import A2AEventHandler, EventContext
from a2a_client_toolkit.providers.line.file import FileStore, FileUploadRequest
from a2a_client_toolkit.providers.line.types import LineEventContext
from a2a_client_toolkit.providers.line.user_state import UserState, UserStateStore


class DefaultLineEventHandler(A2AEventHandler):
    def __init__(self, config: line.Configuration, file_store: FileStore, user_state_store: UserStateStore) -> None:
        self.config = config
        self.file_store = file_store
        self.user_state_store = user_state_store

    async def handle_event(self, context: EventContext, event: a2a.SendStreamingMessageSuccessResponse) -> None:
        if not isinstance(context, LineEventContext):
            raise ValueError("context is not LineEventContext")

        await self.user_state_store.set(
            context.user_id(),
            UserState(
                task_id=_get_task_id(event),
                context_id=_get_context_id(event),
            ),
        )

        await context.sender.stream(self.generate_messages(event))

    async def generate_messages(self, event: a2a.SendStreamingMessageSuccessResponse) -> AsyncGenerator[line.Message]:
        result = event.result
        if result.kind == "message":
            for part in result.parts:
                yield await self._part_to_line_message(part)
        if result.kind == "artifact-update":
            for part in result.artifact.parts:
                yield await self._part_to_line_message(part)
        if result.kind == "status-update":
            for part in result.status.message.parts if result.status.message else []:
                yield await self._part_to_line_message(part)
        if result.kind == "task":
            pass

    async def _part_to_line_message(self, part: a2a.Part) -> line.Message:
        quick_reply = line.QuickReply(
            items=[
                line.QuickReplyItem(
                    type="action",
                    action=line.PostbackAction(
                        data='{"action": "complete_task"}',
                        displayText="タスクを完了",
                        label="タスクを完了",
                        inputOption=None,
                        fillInText=None,
                    ),
                    imageUrl=None,
                ),
            ],
        )

        if part.root.kind == "file":
            file = part.root.file

            mime_type = file.mimeType
            if not mime_type:
                raise ValueError("mimeType is not set")

            file_type = mime_type.split("/")[0]
            file_extension = mime_type.split("/")[1]

            file_name = uuid4().hex
            file_name = f"{file_name}.{file_extension}"

            file_uri = None
            if isinstance(file, a2a.FileWithBytes):
                file_upload_response = await self.file_store.upload(
                    FileUploadRequest(path=file_name, bytes=base64.b64decode(file.bytes)),
                )
                file_uri = file_upload_response.uri
            else:  # FileWithUrl
                file_uri = file.uri

            if file_type == "image":
                return line.ImageMessage(originalContentUrl=file_uri, previewImageUrl=file_uri, quickReply=quick_reply)
            if file_type == "video":
                return line.VideoMessage(
                    originalContentUrl=file_uri,
                    previewImageUrl="https://3b2c-2404-7a81-b240-3200-1427-bd98-14b6-3aa3.ngrok-free.app/files/preview.png",
                    quickReply=quick_reply,
                    trackingId=None,
                )

            # TODO(@ryunosuke): support other file types
            return line.TextMessage(text=f"ファイルを送信しました。\n{file_uri}", quickReply=quick_reply, quoteToken=None)

        if part.root.kind == "data":
            return line.TextMessage(text=json.dumps(part.root.data, indent=2), quickReply=quick_reply, quoteToken=None)

        # TextPart
        return line.TextMessage(text=part.root.text, quickReply=quick_reply, quoteToken=None)

    async def handle_error(self, context: EventContext, error: a2a.JSONRPCErrorResponse) -> None:
        raise Exception(error.error.message or "Unknown error")


def _get_task_id(update: a2a.SendStreamingMessageSuccessResponse) -> str | None:
    if isinstance(update.result, a2a.Task):
        return update.result.id
    return update.result.taskId


def _get_context_id(update: a2a.SendStreamingMessageSuccessResponse) -> str | None:
    return update.result.contextId
