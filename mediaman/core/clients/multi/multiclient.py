
from typing import Iterator

from mediaman.core.models import Response
from mediaman.core.clients.multi import abstract
from mediaman.core.clients.multi import methods
from mediaman.services.abstract.models import AbstractResultFile


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
    """
    Class handling `mm all ...` commands.
    """

    def list_files(self) -> Iterator[Response]:
        return gen_all(methods.list_files(self.clients))

    def has(self, request) -> Iterator[Response]:
        return gen_all(methods.has(self.clients, request))

    def search_by_name(self, file_name) -> Iterator[Response]:
        return gen_all(methods.search_by_name(self.clients, file_name))

    def fuzzy_search_by_name(self, file_name) -> Iterator[Response]:
        return gen_all(methods.fuzzy_search_by_name(self.clients, file_name))

    def upload(self, request) -> Iterator[Response]:
        return gen_all(methods.upload(self.clients, request))

    def download(self, root, file_path):
        raise RuntimeError()  # `mm all get` isn't allowed

    def stream(self, root, file_path):
        raise RuntimeError()  # `mm all stream` isn't allowed

    def stream_range(self, root, file_path, offset, length):
        raise RuntimeError()  # `mm all streamrange` isn't allowed

    def stats(self) -> Iterator[Response]:
        return gen_all(methods.stats(self.clients))

    def capacity(self) -> Iterator[Response]:
        return gen_all(methods.capacity(self.clients))

    def refresh(self):
        raise RuntimeError()  # `mm all refresh` isn't allowed

    def remove(self, request):
        raise RuntimeError()  # `mm all remove` isn't allowed

    def refresh_global_hashes(self, request):
        raise NotImplementedError()

    def search_by_hash(self, hash) -> Iterator[Response]:
        return gen_all(methods.search_by_hash(self.clients, hash))

    def has_hash(self, hash) -> Iterator[Response]:
        return gen_all(methods.has_hash(self.clients, hash))

    def tag(self, *args, **kwargs) -> Iterator[Response]:
        return gen_all(methods.tag(self.clients, *args, **kwargs))

    def migrate_to_v2(self):
        raise RuntimeError()  # `mm all migrate_to_v2` isn't allowed
