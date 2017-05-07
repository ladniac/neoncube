from asyncio import ensure_future
from asyncio.base_futures import InvalidStateError

from http_client import client as http_client


class Communicator:
    def __init__(self, loop):
        self.on = False
        self.task = None
        self.loop = loop

    @property
    def exception(self):
        exception = None
        if self.on and hasattr(self.task, 'exception'):
            try:
                exception = self.task.exception()
            except InvalidStateError:
                pass
        return exception

    def start(self):
        self.task = ensure_future(self.client())
        self.on = True

    def stop(self):
        self.task.cancel()
        self.on = False

    def client(self):
        raise NotImplementedError

    def check_if_should_recover(self):
        return False


class HttpCommunicator(Communicator):
    EXCEPTIONS_TO_RECOVER_FROM = []
    client = http_client

    def check_if_should_recover(self):
        return self.exception in self.EXCEPTIONS_TO_RECOVER_FROM
