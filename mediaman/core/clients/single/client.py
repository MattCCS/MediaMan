
import pathlib

from mediaman.core import validation
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

    def has(self, request):
        hash = request.hash
        return self.index.has_hash(hash)

    def has_hash(self, hash):
        # TODO: validate valid hash?
        return self.index.has_hash(hash)

    def has_uuid(self, uuid):
        if validation.is_valid_uuid(uuid):
            return self.index.has_uuid(uuid)
        raise RuntimeError("invalid uuid")

    def has_name(self, name):
        return self.index.has_name(name)

    def search_by_name(self, file_name):
        return list(self.index.search_by_name(file_name))

    def fuzzy_search_by_name(self, file_name):
        return list(self.index.fuzzy_search_by_name(file_name))

    def upload(self, request):
        return self.index.upload(request)

    def download(self, root, file_id):
        return self.index.download(root, file_id)

    def capacity(self):
        return self.index.capacity()

    def refresh(self):
        return self.index.refresh()

    def remove(self, request):
        hash = request.hash
        assert validation.is_valid_hash(hash)
        return self.index.remove(request)

    def refresh_global_hashes(self, request):
        return self.index.refresh_global_hashes(request)
