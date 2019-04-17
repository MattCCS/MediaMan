
import abc
from typing import List

from mediaman.services.abstract import models


class AbstractMultiIndex(abc.ABC):

    def __init__(self, client):
        self.client = client

    def list_files(self) -> models.AbstractResultFileList:
        return self.client.list_files()

    @abc.abstractmethod
    def has(self, root, *file_ids) -> List[models.AbstractResultFile]:
        raise NotImplementedError()

    @abc.abstractmethod
    def search_by_name(self, *file_names) -> List[models.AbstractResultFileList]:
        raise NotImplementedError()

    @abc.abstractmethod
    def fuzzy_search_by_name(self, *file_names) -> List[models.AbstractResultFileList]:
        raise NotImplementedError()

    @abc.abstractmethod
    def upload(self, *requests) -> List[models.AbstractReceiptFile]:
        raise NotImplementedError()

    @abc.abstractmethod
    def download(self, *requests) -> List[models.AbstractReceiptFile]:
        raise NotImplementedError()

    def capacity(self) -> models.AbstractResultQuota:
        return self.client.capacity()

    def refresh(self):
        return self.client.refresh()
