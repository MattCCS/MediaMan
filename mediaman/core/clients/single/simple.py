
from mediaman.core.clients.single import abstract


class SimpleSingleClient(abstract.AbstractSingleClient):

    def list_files(self):
        return list(self.index.list_files())

    def has(self, file_id):
        raise NotImplementedError()  # TODO

    def search_by_name(self, file_name):
        return list(self.index.search_by_name(file_name))

    def fuzzy_search_by_name(self, file_name):
        return list(self.index.fuzzy_search_by_name(file_name))

    def upload(self, file_path):
        return self.index.upload(file_path)

    def download(self, root, file_path):
        return [self.index.download(root, file_path)]

    def capacity(self):
        return self.index.capacity()
