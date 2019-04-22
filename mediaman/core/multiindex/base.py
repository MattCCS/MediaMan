
from functools import partial
import pathlib
from typing import List

from mediaman.core.multiindex import abstract
from mediaman.services.abstract import models


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


class BaseMultiIndex(abstract.AbstractMultiIndex):

    def has(self, root, *file_ids) -> List[models.AbstractResultFile]:
        # TODO: resolve paths + hash files here!
        resolve = partial(resolve_abs_path, root)
        abs_paths = list(map(resolve, file_ids))
        yield from map(self.client.has, abs_paths)

    def search_by_name(self, *file_names) -> List[models.AbstractResultFileList]:
        yield from map(self.client.search_by_name, file_names)

    def fuzzy_search_by_name(self, *file_names) -> List[models.AbstractResultFileList]:
        yield from map(self.client.fuzzy_search_by_name, file_names)

    def upload(self, root, *requests) -> List[models.AbstractReceiptFile]:
        # TODO: resolve paths + hash files here!
        resolve = partial(resolve_abs_path, root)
        abs_paths = list(map(resolve, requests))  # TODO: fix this
        yield from map(self.client.upload, abs_paths)

    def download(self, *requests) -> List[models.AbstractReceiptFile]:
        # TODO: resolve paths + hash files here!
        yield from map(self.client.download, requests)
