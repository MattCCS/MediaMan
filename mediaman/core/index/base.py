
from mediaman.core.index import abstract


class BaseIndex(abstract.AbstractIndex):

    def stats(self):
        return self.stats.capacity()

    def capacity(self):
        return self.service.capacity()
