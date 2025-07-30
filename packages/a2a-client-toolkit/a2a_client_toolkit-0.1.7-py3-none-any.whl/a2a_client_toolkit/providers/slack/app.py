import logging
from typing import Any

import a2a.types as a2a
from pydantic import BaseModel
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp
from slack_bolt.context.say.async_say import AsyncSay

from a2a_client_toolkit.providers.slack.slack import SlackAppMentionEvent
from a2a_client_toolkit.providers.slack.types import SlackEventContext, SlackUserID
from a2a_client_toolkit.worker import A2AClientWorker

logger = logging.getLogger(__name__)


class SlackAppConfig(BaseModel):
    slack_bot_token: str
    slack_app_token: str


class SlackApp:
    def __init__(self, config: SlackAppConfig, worker: A2AClientWorker) -> None:
        self.config = config
        self.worker = worker

    async def _handle_app_mention_event(self, event: dict[str, Any], say: AsyncSay) -> None:
        logger.info("Received app_mention event: %s", event)

        # Convert dict to Pydantic model
        try:
            slack_event = SlackAppMentionEvent.model_validate(event)
        except Exception:
            logger.exception("Failed to parse Slack app_mention event")
            return

        user_id = slack_event.user
        channel = slack_event.channel
        thread_ts = slack_event.thread_ts or slack_event.ts

        if not user_id or not channel:
            return

        context = SlackEventContext(
            slack_user_id=SlackUserID(raw=user_id),
            thread_ts=thread_ts,
            channel_id=channel,
        )

        user_message = self._slack_message_to_a2a_message(thread_ts, slack_event)

        logger.info("Sending user message to A2A: %s", user_message)

        await self.worker.on_user_message(context=context, user_message=user_message)

    def _slack_message_to_a2a_message(self, thread_ts: str, event: SlackAppMentionEvent) -> a2a.Message:
        return a2a.Message(
            contextId=thread_ts,
            taskId=thread_ts,
            role=a2a.Role.user,
            parts=[
                a2a.Part(a2a.TextPart(text=event.text)),
            ],
            messageId=f"slack-message-{event.ts}",
        )

    async def run(self) -> None:
        app = AsyncApp(token=self.config.slack_bot_token)

        app.event("app_mention")(self._handle_app_mention_event)  # type: ignore[reportUnknownMemberType]

        socket_handler = AsyncSocketModeHandler(app, self.config.slack_app_token)
        logger.info("⚡️ Bolt app is running in Socket Mode!")
        await socket_handler.start_async()
