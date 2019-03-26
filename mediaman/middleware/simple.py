
from mediaman.core.clients.single import simple


class SimpleMiddleware(simple.SimpleSingleClient):

    def __init__(self, service):
        super().__init__(service)
