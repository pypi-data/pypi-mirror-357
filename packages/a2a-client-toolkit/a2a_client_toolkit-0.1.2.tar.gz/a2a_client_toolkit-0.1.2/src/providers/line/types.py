from pydantic import BaseModel

from client.handler import EventContext
from providers.line.sender import LineMessageSender


class LineUserID(BaseModel):
    raw: str

    def general(self) -> str:
        return f"line:{self.raw}"


class LineEventContext(BaseModel, EventContext):
    model_config = {"arbitrary_types_allowed": True}

    line_user_id: LineUserID
    sender: LineMessageSender

    def user_id(self) -> str:
        return self.line_user_id.general()
