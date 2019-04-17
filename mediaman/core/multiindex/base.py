
from functools import partial
from typing import List

from mediaman.core.multiindex import abstract
from mediaman.services.abstract import models


class BaseMultiIndex(abstract.AbstractMultiIndex):

    def has(self, root, *file_ids) -> List[models.AbstractResultFile]:
        func = partial(self.client.has, root)
        yield from map(func, file_ids)

    def search_by_name(self, *file_names) -> List[models.AbstractResultFileList]:
        # TODO: resolve paths + hash files here!
        yield from map(self.client.search_by_name, file_names)

    def fuzzy_search_by_name(self, *file_names) -> List[models.AbstractResultFileList]:
        # TODO: resolve paths + hash files here!
        yield from map(self.client.fuzzy_search_by_name, file_names)

    def upload(self, *requests) -> List[models.AbstractReceiptFile]:
        # TODO: resolve paths + hash files here!
        yield from map(self.client.upload, requests)

    def download(self, *requests) -> List[models.AbstractReceiptFile]:
        # TODO: resolve paths + hash files here!
        yield from map(self.client.download, requests)
