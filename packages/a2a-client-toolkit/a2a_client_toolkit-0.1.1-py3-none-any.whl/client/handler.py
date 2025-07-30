import abc

import a2a.types as a2a


class EventContext(abc.ABC):
    @abc.abstractmethod
    def user_id(self) -> str:
        pass


class A2AEventHandler(abc.ABC):
    @abc.abstractmethod
    async def handle_event(self, context: EventContext, event: a2a.SendStreamingMessageSuccessResponse) -> None:
        pass

    @abc.abstractmethod
    async def handle_error(self, context: EventContext, error: a2a.JSONRPCErrorResponse) -> None:
        pass
