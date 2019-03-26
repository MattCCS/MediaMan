
import pathlib

from mediaman.core import index
from mediaman.core.clients.single import abstract


class SingleClient(abstract.AbstractSingleClient):

    def __init__(self, service):
        super().__init__(service)
        self.index = index.Index(self.service)

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
        path = pathlib.Path(file_path)
        identifier = path.name
        return [self.index.download(identifier)]

    def get_file_by_hash(self, file_hash):
        return self.index.get_file_by_hash(file_hash)

    def has_by_uuid(self, identifier):
        return self.index.has_by_uuid(identifier)

    def capacity(self):
        return self.service.capacity()
