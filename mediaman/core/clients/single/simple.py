
from mediaman.core.clients.single import abstract


class SimpleSingleClient(abstract.AbstractSingleClient):

    def __init__(self, service):
        super().__init__(service)

    def list_files(self):
        return list(self.service.list_files())

    def list_file(self, file_id):
        return self.service.list_file(file_id)

    def search_by_name(self, file_name):
        return list(self.service.search_by_name(file_name))

    def fuzzy_search_by_name(self, file_name):
        return list(self.service.fuzzy_search_by_name(file_name))

    def exists(self, file_id):
        return self.service.exists(file_id)

    def upload(self, file_path):
        return self.service.upload(file_path)

    def download(self, file_path):
        return [self.service.download(file_path)]

    def get_file_by_hash(self, file_hash):
        return self.service.get_file_by_hash(file_hash)

    def has_by_uuid(self, identifier):
        return self.service.has_by_uuid(identifier)

    def capacity(self):
        return self.service.capacity()
