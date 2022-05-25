
from functools import partial
from typing import List, Generator

from mediaman.core import hashing
from mediaman.core import logtools
from mediaman.core import models
from mediaman.core import validation
from mediaman.core.multiindex import abstract
from mediaman.core.utils import paths
from mediaman.services.abstract import models as abstractmodels

logger = logtools.new_logger(__name__)


def resolve_identifier(root, identifier) -> models.Request:
    if validation.is_valid_hash(identifier):
        return models.Request(hash=identifier)

    try:
        abs_path = paths.resolve_abs_path(root, identifier)
        return models.Request(path=abs_path)
    except OSError:
        logger.error(f"Identifier must be a hash or filepath.  Got '{identifier}'.")

    return None


class BaseMultiIndex(abstract.AbstractMultiIndex):

    def has(self, root, *file_paths) -> List[abstractmodels.AbstractResultFile]:
        abs_paths = list(paths.resolve_abs_paths(root, file_paths))
        requests = (
            models.Request(id=None, path=path)
            for path in abs_paths)
        yield from zip(abs_paths, map(self.client.has, requests))

    def search_by_name(self, *file_names) -> List[abstractmodels.AbstractResultFileList]:
        yield from zip(file_names, map(self.client.search_by_name, file_names))

    def fuzzy_search_by_name(self, *file_names) -> List[abstractmodels.AbstractResultFileList]:
        yield from zip(file_names, map(self.client.fuzzy_search_by_name, file_names))

    def upload(self, root, *file_paths) -> List[abstractmodels.AbstractReceiptFile]:
        abs_paths = list(paths.resolve_abs_paths(root, file_paths))
        requests = (
            models.Request(id=None, path=path)
            for path in abs_paths)
        yield from zip(abs_paths, map(self.client.upload, requests))

    def download(self, root, *identifiers) -> List[abstractmodels.AbstractReceiptFile]:
        local_download = partial(self.client.download, root)
        yield from map(local_download, identifiers)

    def stream(self, root, identifier) -> Generator[bytes, None, None]:
        return self.client.stream(root, identifier)

    def stream_range(self, root, identifier, offset, length) -> Generator[bytes, None, None]:
        return self.client.stream_range(root, identifier, offset, length)

    def remove(self, *identifiers) -> List[abstractmodels.AbstractReceiptFile]:
        for identifier in identifiers:
            # TODO: this should allow any valid hash, or ID
            if not validation.is_valid_hash(identifier):
                logger.error(f"May only pass hashes to `remove` method, got '{identifier}'.")
                return

        requests = (
            models.Request(id=None, path=None, hash=identifier)
            for identifier in identifiers)
        yield from map(self.client.remove, requests)

    def search_by_hash(self, *identifiers) -> List[abstractmodels.AbstractResultFile]:
        for identifier in identifiers:
            # TODO: this should allow any valid hash, or ID
            if not validation.is_valid_hash(identifier):
                logger.error(f"May only pass hashes to `search-by-hash` method, got '{identifier}'.")
                return

        yield from zip(identifiers, map(self.client.search_by_hash, identifiers))

    def tag(self, root, identifiers=None, add=None, remove=None, set=None) -> List[abstractmodels.AbstractResultFile]:
        requests = []

        for identifier in identifiers:
            if (request := resolve_identifier(root, identifier)):
                requests.append(request)

        return self.client.tag(requests=requests, add=add, remove=remove, set=set)

    def migrate_to_v2(self):
        return self.client.migrate_to_v2()
