
from mediaman.core.clients.abstract import abstract


class AbstractMulticlient(abstract.AbstractClient):

    def __init__(self, clients):
        self.clients = clients
