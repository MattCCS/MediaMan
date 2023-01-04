
import functools

from mediaman.middleware import abstract


def init(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        self.init_metadata(force=False)
        return func(self, *args, **kwargs)
    return wrapped


class SimpleMiddleware(abstract.AbstractMiddleware):

    @init
    def list_files(self):
        return self.service.list_files()

    @init
    def has(self, file_id):
        return self.service.has(file_id)

    @init
    def search_by_name(self, file_name):
        return self.service.search_by_name(file_name)

    @init
    def fuzzy_search_by_name(self, file_name):
        return self.service.fuzzy_search_by_name(file_name)

    @init
    def upload(self, request):
        return self.service.upload(request)

    @init
    def download(self, root, request):
        return self.service.download(root, request)

    @init
    def stats(self):
        return self.service.stats()

    @init
    def capacity(self):
        return self.service.capacity()

    @init
    def refresh(self):
        return self.service.refresh()

    @init
    def remove(self, request):
        return self.service.remove(request)

    @init
    def refresh_global_hashes(self, request):
        return self.service.refresh_global_hashes(request)

    @init
    def tag(self, request, *args, **kwargs):
        return self.service.tag(request, *args, **kwargs)
