import base64
import json
import logging

import a2a.types as a2a
from slack_sdk.web.async_client import AsyncWebClient

from a2a_client_toolkit.handler import A2AEventHandler, EventContext
from a2a_client_toolkit.providers.slack.slack import SlackMessage, SlackResponse
from a2a_client_toolkit.providers.slack.types import SlackEventContext

logger = logging.getLogger(__name__)


class DefaultSlackEventHandler(A2AEventHandler):
    def __init__(
        self,
        slack_client: AsyncWebClient,
    ) -> None:
        self.slack_client = slack_client

    async def handle_event(self, context: EventContext, event: a2a.SendStreamingMessageSuccessResponse) -> None:
        if not isinstance(context, SlackEventContext):
            raise ValueError("context is not SlackEventContext")

        logger.info("Received streaming message success event: %s", event)

        result = event.result
        messages: list[SlackMessage] = []
        if result.kind == "message":
            for part in result.parts:
                messages.append(await self._part_to_slack_message(context, part))
        if result.kind == "artifact-update":
            for part in result.artifact.parts:
                messages.append(await self._part_to_slack_message(context, part))
        if result.kind == "status-update":
            for part in result.status.message.parts if result.status.message else []:
                messages.append(await self._part_to_slack_message(context, part))
        if result.kind == "task":
            pass

        await self._send_messages(channel_id=context.channel_id, thread_ts=context.thread_ts, messages=messages)

    async def _send_messages(self, channel_id: str, thread_ts: str, messages: list[SlackMessage]) -> None:
        """Send messages to Slack channel using Slack Web API"""
        for message in messages:
            try:
                raw_response = await self.slack_client.chat_postMessage(  # type: ignore[reportUnknownMemberType]
                    thread_ts=thread_ts,
                    channel=channel_id,
                    text=message.text or "",
                    blocks=message.blocks or [],
                )

                # Convert AsyncSlackResponse to dict, then parse using Pydantic schema
                response = SlackResponse.model_validate(raw_response.data)  # type: ignore[reportUnknownMemberType]

                if not response.ok:
                    error_msg = response.error or "Unknown error"
                    logger.error("Failed to send message to Slack: %s", error_msg)
                else:
                    logger.info("Message sent successfully to channel %s", response.channel)

            except Exception:
                logger.exception("Failed to send message to Slack")

    async def _part_to_slack_message(self, context: SlackEventContext, part: a2a.Part) -> SlackMessage:
        if part.root.kind == "file":
            file = part.root.file

            if isinstance(file, a2a.FileWithUri):
                if file.mimeType and file.mimeType.startswith("image/"):
                    return SlackMessage(
                        blocks=[
                            {
                                "type": "image",
                                "image_url": file.uri,
                                "alt_text": file.name or "image",
                            },
                        ],
                    )
                return SlackMessage(
                    blocks=[
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": file.uri,
                            },
                        },
                    ],
                )

            try:
                decoded_bytes = base64.b64decode(file.bytes)

                # Upload file to Slack
                await self.slack_client.files_upload_v2(  # type: ignore[reportUnknownMemberType]
                    channel=context.channel_id,
                    thread_ts=context.thread_ts,
                    content=decoded_bytes,
                    filename=file.name or "file",
                    title=file.name or "file",
                )

                return SlackMessage(text=f"ファイルをアップロードしました: {file.name or 'file'}")
            except Exception as e:
                logger.error("Failed to upload file to Slack: %s", e)
                return SlackMessage(text=f"ファイルをアップロードできませんでした: {file.name or 'file'}")

        if part.root.kind == "data":
            return SlackMessage(
                text=f"```\n{json.dumps(part.root.data, indent=2)}\n```",
            )

        # TextPart
        return SlackMessage(text=part.root.text)

    async def handle_error(self, context: EventContext, error: a2a.JSONRPCErrorResponse) -> None:
        if not isinstance(context, SlackEventContext):
            raise Exception(error.error.message or "Unknown error")

        error_message = error.error.message or "Unknown error"
        raw_response = await self.slack_client.chat_postMessage(  # type: ignore[reportUnknownMemberType]
            thread_ts=context.thread_ts,
            channel=context.channel_id,
            text=f"❌ エラーが発生しました: {error_message}",
        )

        # Parse response using Pydantic schema
        response = SlackResponse.model_validate(raw_response.data)  # type: ignore[reportUnknownMemberType]

        if not response.ok:
            print(f"Failed to send error message to Slack: {response.error}")
