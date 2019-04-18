
import pathlib

from mediaman.core.clients.single import abstract


def resolve_abs_path(root, file_id):
    path = pathlib.Path(file_id)
    if path.is_absolute():
        if path.exists():
            return path
        raise FileNotFoundError()

    rel_path = root / path
    if rel_path.exists():
        return rel_path

    return None


class SingleClient(abstract.AbstractSingleClient):

    def list_files(self):
        return list(self.index.list_files())

    def has(self, file_path):
        return self.index.has_file(file_path)

        # elif validation.is_valid_uuid(file_id):
        #     return self.index.has_uuid(file_id)
        # elif validation.is_valid_sha256(file_id):
        #     return self.index.has_hash(file_id)

    def search_by_name(self, file_name):
        return list(self.index.search_by_name(file_name))

    def fuzzy_search_by_name(self, file_name):
        return list(self.index.fuzzy_search_by_name(file_name))

    def upload(self, file_path):
        return self.index.upload(file_path)

    def download(self, file_id):
        return [self.index.download(file_id)]

    def capacity(self):
        return self.index.capacity()

    def refresh(self):
        return self.index.refresh()
