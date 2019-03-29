
from mediaman.core.index import abstract


class BaseIndex(abstract.AbstractIndex):

    def capacity(self):
        return self.service.capacity()
