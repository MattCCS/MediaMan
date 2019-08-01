
from mediaman.core.clients.multi import methods
from mediaman.core.clients.abstract import abstract


class AbstractMulticlient(abstract.AbstractClient):

    def __init__(self, clients):
        self.clients = clients
        # self.force_init()

    def force_init(self):
        return methods.force_init(self.clients)

    def name(self):
        return f"{self.__class__.__name__}({'/'.join(c.name() for c in self.clients)})"

    def nickname(self):
        return f"{self.__class__.__name__}({'/'.join(c.nickname() for c in self.clients)})"

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.clients)})"
