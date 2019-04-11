
import pathlib

from mediaman.core.clients.single import abstract


class SingleClient(abstract.AbstractSingleClient):

    def list_files(self):
        return list(self.index.list_files())

    def has(self, root, file_id):
        path = pathlib.Path(file_id)
        if path.exists():
            return self.index.has_file(path)
        rel_path = root / path
        if rel_path.exists():
            return self.index.has_file(rel_path)
        # elif validation.is_valid_uuid(file_id):
        #     return self.index.has_uuid(file_id)
        # elif validation.is_valid_sha256(file_id):
        #     return self.index.has_hash(file_id)
        raise FileNotFoundError()

    def search_by_name(self, file_name):
        return list(self.index.search_by_name(file_name))

    def fuzzy_search_by_name(self, file_name):
        return list(self.index.fuzzy_search_by_name(file_name))

    def upload(self, file_path):
        return self.index.upload(file_path)

    def download(self, file_path):
        path = pathlib.Path(file_path)
        identifier = path.name
        return [self.index.download(identifier)]

    def capacity(self):
        return self.index.capacity()
