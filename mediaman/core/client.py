
import pathlib

from mediaman.core import index


class Client:

    def __init__(self, service):
        self.service = service
        self.index = index.Index(self.service)

    def name(self):
        return self.service.__class__.__name__

    def get_file_by_hash(self, file_hash):
        return self.index.get_file_by_hash(file_hash)

    def list_files(self):
        return list(self.index.list_files())

    def list_file(self, file_id):
        return self.index.list_file(file_id)

    def has_by_uuid(self, identifier):
        return self.index.has_by_uuid(identifier)

    def search_by_name(self, file_name):
        return list(self.index.search_by_name(file_name))

    def exists(self, file_id):
        return self.index.exists(file_id)

    def upload(self, file_path):
        return self.index.upload(file_path)

    def download(self, file_path):
        path = pathlib.Path(file_path)
        identifier = path.name
        return [self.index.download(identifier)]

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.service)})"
