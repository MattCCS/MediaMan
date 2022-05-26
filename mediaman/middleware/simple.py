
import functools

from mediaman.middleware import abstract


class SimpleMiddleware(abstract.AbstractMiddleware):

    def list_files(self):
        return self.service.list_files()

    def has(self, file_id):
        return self.service.has(file_id)

    def search_by_name(self, file_name):
        return self.service.search_by_name(file_name)

    def fuzzy_search_by_name(self, file_name):
        return self.service.fuzzy_search_by_name(file_name)

    def upload(self, request):
        return self.service.upload(request)

    def download(self, root, request):
        return self.service.download(root, request)

    def stats(self):
        return self.service.stats()

    def capacity(self):
        return self.service.capacity()

    def refresh(self):
        return self.service.refresh()

    def remove(self, request):
        return self.service.remove(request)

    def refresh_global_hashes(self, request):
        return self.service.refresh_global_hashes(request)

    def tag(self, request, *args, **kwargs):
        return self.service.tag(request, *args, **kwargs)

    def migrate_to_v2(self):
        raise NotImplementedError()
