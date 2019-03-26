
from mediaman.core.clients.single import abstract


class SimpleSingleClient(abstract.AbstractSingleClient):

    def list_files(self):
        return list(self.index.list_files())

    def list_file(self, file_id):
        return self.index.list_file(file_id)

    def search_by_name(self, file_name):
        return list(self.index.search_by_name(file_name))

    def fuzzy_search_by_name(self, file_name):
        return list(self.index.fuzzy_search_by_name(file_name))

    def exists(self, file_id):
        return self.index.exists(file_id)

    def upload(self, file_path):
        return self.index.upload(file_path)

    def download(self, file_path):
        return [self.index.download(file_path)]

    def capacity(self):
        return self.index.capacity()
