import os

import linebot.v3.messaging as line_messaging  # type: ignore[reportMissingImports]
import uvicorn
from dotenv import load_dotenv

from client.worker import A2AClientWorker
from providers.line.file import LocalFileStore
from providers.line.handler import DefaultLineEventHandler
from providers.line.server import LineServer, LineServerConfig
from providers.line.user_state import InMemoryUserStateStore

if __name__ == "__main__":
    load_dotenv()

    config = LineServerConfig(
        line_messaging_config=line_messaging.Configuration(
            access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN"),
        ),
        line_channel_secret=os.getenv("LINE_CHANNEL_SECRET") or "",
    )

    user_state_store = InMemoryUserStateStore()
    file_store = LocalFileStore(base_uri=f"{os.getenv('HOST') or ''}/files", directory="public/files")

    event_handler = DefaultLineEventHandler(
        config=config.line_messaging_config,
        file_store=file_store,
        user_state_store=user_state_store,
    )

    worker = A2AClientWorker(
        a2a_agent_card_url=os.getenv("A2A_AGENT_CARD_URL") or "",
        event_handler=event_handler,
    )

    server = LineServer(config, worker, user_state_store)

    uvicorn.run(server.build(), host="0.0.0.0", port=8000)
