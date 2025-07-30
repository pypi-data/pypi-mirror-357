import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import a2a.types as a2a
import httpx
from a2a.client import A2AClient

from client.handler import A2AEventHandler, EventContext

logger = logging.getLogger(__name__)


class A2AClientWorker:
    def __init__(self, a2a_agent_card_url: str, event_handler: A2AEventHandler) -> None:
        self.executor = ThreadPoolExecutor(thread_name_prefix="a2a_client_worker")
        self.a2a_agent_card_url = a2a_agent_card_url
        self.event_handler = event_handler

    async def on_user_message(self, context: EventContext, user_message: a2a.Message) -> None:
        self.executor.submit(self._process_message, context, user_message)

    def _process_message(self, context: EventContext, user_message: a2a.Message) -> None:
        asyncio.run(self._process_message_async(context, user_message))

    async def _process_message_async(self, context: EventContext, user_message: a2a.Message) -> None:
        async with httpx.AsyncClient() as httpx_client:
            try:
                client = await A2AClient.get_client_from_agent_card_url(
                    httpx_client,
                    self.a2a_agent_card_url,
                )

                streaming_request = a2a.SendStreamingMessageRequest(
                    id=uuid4().hex,
                    params=a2a.MessageSendParams(
                        message=user_message,
                    ),
                )
                stream_response = client.send_message_streaming(streaming_request)
                async for event in stream_response:
                    print(event)

                    if isinstance(event.root, a2a.JSONRPCErrorResponse):
                        await self.event_handler.handle_error(context, event.root)
                    else:
                        await self.event_handler.handle_event(context, event.root)

            except Exception:
                logger.exception("Failed to process user message")
