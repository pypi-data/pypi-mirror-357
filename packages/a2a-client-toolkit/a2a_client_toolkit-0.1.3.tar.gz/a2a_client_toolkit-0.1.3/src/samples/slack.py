import asyncio
import os

from dotenv import load_dotenv
from slack_sdk.web.async_client import AsyncWebClient

from client.worker import A2AClientWorker
from providers.slack.app import SlackApp, SlackAppConfig
from providers.slack.handler import DefaultSlackEventHandler

if __name__ == "__main__":
    load_dotenv()

    config = SlackAppConfig(
        slack_bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
        slack_app_token=os.getenv("SLACK_APP_TOKEN", ""),
    )

    # Initialize Slack Web API client
    slack_client = AsyncWebClient(token=config.slack_bot_token)
    event_handler = DefaultSlackEventHandler(slack_client=slack_client)

    worker = A2AClientWorker(
        a2a_agent_card_url=os.getenv("A2A_AGENT_CARD_URL") or "",
        event_handler=event_handler,
    )

    app = SlackApp(config, worker)
    asyncio.run(app.run())
