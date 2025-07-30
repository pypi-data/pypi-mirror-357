from pydantic import BaseModel

from client.handler import EventContext


class SlackUserID(BaseModel):
    raw: str

    def general(self) -> str:
        return f"slack:{self.raw}"


class SlackEventContext(BaseModel, EventContext):
    slack_user_id: SlackUserID
    thread_ts: str
    channel_id: str

    def user_id(self) -> str:
        return self.slack_user_id.general()
