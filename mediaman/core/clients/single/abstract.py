
from mediaman.core.clients.abstract import abstract


class AbstractSingleClient(abstract.AbstractClient):

    def __init__(self, index):
        self.index = index
        # self.force_init()

    def force_init(self):
        self.index.force_init()

    def name(self):
        return self.index.name()

    def nickname(self):
        return self.index.nickname()

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.index)})"
