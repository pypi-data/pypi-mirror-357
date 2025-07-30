"""Slack provider for A2A Client Toolkit"""

from .app import SlackApp, SlackAppConfig
from .handler import DefaultSlackEventHandler
from .slack import (
    SlackActionsBlock,
    SlackAppMentionEvent,
    SlackBlockElement,
    SlackButtonElement,
    SlackChatPostMessageResponse,
    SlackError,
    SlackEvent,
    SlackEventBase,
    SlackMessage,
    SlackMessageEvent,
    SlackResponse,
    SlackTextBlock,
    SlackWebAPIError,
)
from .types import SlackEventContext, SlackUserID

__all__ = [
    "DefaultSlackEventHandler",
    "SlackActionsBlock",
    "SlackApp",
    "SlackAppConfig",
    "SlackAppMentionEvent",
    "SlackBlockElement",
    "SlackButtonElement",
    "SlackChatPostMessageResponse",
    "SlackError",
    "SlackEvent",
    "SlackEventBase",
    "SlackEventContext",
    "SlackMessage",
    "SlackMessageEvent",
    "SlackResponse",
    "SlackTextBlock",
    "SlackUserID",
    "SlackWebAPIError",
]
