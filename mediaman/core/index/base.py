
from mediaman.core.index import abstract


class BaseIndex(abstract.AbstractIndex):

    def stats(self):
        raise NotImplementedError()

    def capacity(self):
        return self.service.capacity()
