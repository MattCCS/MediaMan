
from mediaman.core.clients.abstract import abstract


class AbstractMiddleware(abstract.AbstractClient):

    def __init__(self, service):
        self.service = service

    def name(self):
        return self.service.__class__.__name__

    def nickname(self):
        return self.service.nickname()

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.service)})"
