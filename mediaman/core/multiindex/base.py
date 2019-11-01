
from functools import partial
from typing import List

from mediaman.core import hashing
from mediaman.core import logtools
from mediaman.core import models
from mediaman.core import validation
from mediaman.core.multiindex import abstract
from mediaman.core.utils import paths
from mediaman.services.abstract import models as abstractmodels

logger = logtools.new_logger("mediaman.core.multiindex.base")


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
