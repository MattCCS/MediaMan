
from mediaman.core.clients.multi import abstract
from mediaman.core.clients.multi import methods


def gen_all(gen):
    try:
        result = next(gen)
        yield result
        while True:
            result = gen.send(True)
            yield result
    except StopIteration:
        pass


class Multiclient(abstract.AbstractMulticlient):

    def list_files(self):
        return gen_all(methods.list_files(self.clients))

    def has(self, request):
        return gen_all(methods.has(self.clients, request))

    def search_by_name(self, file_name):
        return gen_all(methods.search_by_name(self.clients, file_name))

    def fuzzy_search_by_name(self, file_name):
        return gen_all(methods.fuzzy_search_by_name(self.clients, file_name))

    def upload(self, request):
        return gen_all(methods.upload(self.clients, request))

    def download(self, root, file_path):
        raise RuntimeError()  # `mm all get` isn't allowed

    def stream(self, root, file_path):
        raise RuntimeError()  # `mm all stream` isn't allowed

    def stream_range(self, root, file_path, offset, length):
        raise RuntimeError()  # `mm all streamrange` isn't allowed

    def stats(self):
        return gen_all(methods.stats(self.clients))

    def capacity(self):
        return gen_all(methods.capacity(self.clients))

    def refresh(self):
        raise RuntimeError()  # `mm all refresh` isn't allowed

    def remove(self, request):
        raise RuntimeError()  # `mm all remove` isn't allowed

    def refresh_global_hashes(self, request):
        raise NotImplementedError()

    def search_by_hash(self, hash):
        return gen_all(methods.search_by_hash(self.clients, hash))

    def tag(self, *args, **kwargs):
        return gen_all(methods.tag(self.clients, *args, **kwargs))
