"""
Slack API types using Pydantic schemas
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SlackBlockElement(BaseModel):
    """Base class for Slack block elements"""

    type: str


class SlackButtonElement(SlackBlockElement):
    """Slack button element"""

    type: str = Field(default="button")
    text: dict[str, str] = Field(description="Button text")
    action_id: str = Field(description="Action ID for the button")
    style: str | None = Field(default=None, description="Button style (primary, danger, etc.)")


class SlackActionsBlock(BaseModel):
    """Slack actions block"""

    type: str = Field(default="actions")
    elements: list[SlackBlockElement] = Field(description="Action elements")


class SlackTextBlock(BaseModel):
    """Slack text block"""

    type: str = Field(default="section")
    text: dict[str, str] = Field(description="Text content")


class SlackMessage(BaseModel):
    """Slack message structure"""

    text: str | None = Field(default=None, description="Message text")
    blocks: list[dict[str, Any]] | None = Field(default=None, description="Message blocks")


class SlackChatPostMessageResponse(BaseModel):
    """Response from chat.postMessage API"""

    ok: bool = Field(description="Whether the request was successful")
    channel: str | None = Field(default=None, description="Channel ID")
    ts: str | None = Field(default=None, description="Message timestamp")
    message: dict[str, Any] | None = Field(default=None, description="Message object")
    error: str | None = Field(default=None, description="Error message if ok is False")


class SlackWebAPIError(BaseModel):
    """Slack Web API error response"""

    ok: bool = Field(default=False)
    error: str = Field(description="Error code")
    response_metadata: dict[str, Any] | None = Field(default=None, description="Response metadata")


# Slack Event Types
class SlackEventBase(BaseModel):
    """Base class for Slack events"""

    model_config = ConfigDict(extra="ignore")  # Ignore unknown fields

    type: str = Field(description="Event type")
    user: str = Field(description="User ID")
    channel: str = Field(description="Channel ID")
    ts: str = Field(description="Timestamp")


class SlackAppMentionEvent(SlackEventBase):
    """Slack app_mention event"""

    type: str = Field(default="app_mention")
    text: str = Field(description="Message text")
    team: str = Field(description="Team ID")
    event_ts: str = Field(description="Event timestamp")
    thread_ts: str | None = Field(default=None, description="Thread timestamp")
    # Additional fields that might be present
    subtype: str | None = Field(default=None, description="Message subtype")
    bot_id: str | None = Field(default=None, description="Bot ID")
    edited: dict[str, Any] | None = Field(default=None, description="Edit information")
    client_msg_id: str | None = Field(default=None, description="Client message ID")


class SlackMessageEvent(SlackEventBase):
    """Slack message event"""

    type: str = Field(default="message")
    text: str = Field(description="Message text")
    team: str = Field(description="Team ID")
    event_ts: str = Field(description="Event timestamp")
    thread_ts: str | None = Field(default=None, description="Thread timestamp")
    # Additional fields that might be present
    subtype: str | None = Field(default=None, description="Message subtype")
    bot_id: str | None = Field(default=None, description="Bot ID")
    edited: dict[str, Any] | None = Field(default=None, description="Edit information")
    client_msg_id: str | None = Field(default=None, description="Client message ID")


# Type aliases for better readability
SlackResponse = SlackChatPostMessageResponse
SlackError = SlackWebAPIError
SlackEvent = SlackAppMentionEvent | SlackMessageEvent
