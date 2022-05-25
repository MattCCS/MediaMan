
from mediaman.core import validation
from mediaman.core.clients.single import abstract


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

    def search_by_hash(self, hash):
        return list(self.index.search_by_hash(hash))

    def upload(self, request):
        return self.index.upload(request)

    def download(self, root, file_id):
        return self.index.download(root, file_id)

    def stream(self, root, file_id):
        return self.index.stream(root, file_id)

    def stream_range(self, root, file_id, offset, length):
        return self.index.stream_range(root, file_id, offset, length)

    def stats(self):
        # TODO: define a real object, not a dict
        files = self.list_files()
        return {"file_count": len(files)}

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

    def tag(self, requests=None, add=None, remove=None, set=None):
        return self.index.tag(requests=requests, add=add, remove=remove, set=set)

    def migrate_to_v2(self):
        return self.index.migrate_to_v2()
