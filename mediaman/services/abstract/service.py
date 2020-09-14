
import abc
import functools
from typing import Generator

from mediaman.services.abstract import models


def auth(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        self.authenticate()
        return func(self, *args, **kwargs)
    return wrapped


class AbstractService(abc.ABC):

    def __init__(self, config: models.BaseConfig):
        self._config = config

    def nickname(self):
        return self._config.nickname

    @abc.abstractmethod
    def authenticate(self) -> None:
        """Authenticate with the service, if necessary."""
        raise NotImplementedError()

    @abc.abstractmethod
    def list_files(self) -> models.AbstractResultFileList:
        """List all files stored with this service."""
        raise NotImplementedError()

    @abc.abstractmethod
    def list_file(self, file_id) -> models.AbstractResultFile:
        """List the file with the given file ID."""
        raise NotImplementedError()

    @abc.abstractmethod
    def search_by_name(self, file_name) -> models.AbstractResultFileList:
        """List all files with the given name."""
        raise NotImplementedError()

    @abc.abstractmethod
    def exists(self, file_id) -> bool:
        """Return whether a file with that ID exists."""
        raise NotImplementedError()

    @abc.abstractmethod
    def upload(self, request) -> models.AbstractReceiptFile:
        """Upload the file(s) described by the given request."""
        raise NotImplementedError()

    @abc.abstractmethod
    def download(self, request) -> models.AbstractReceiptFile:
        """Download the file(s) described by the given request."""
        raise NotImplementedError()

    @abc.abstractmethod
    def stream(self, request) -> Generator[bytes, None, None]:
        """Stream the file described by the given request."""
        raise NotImplementedError()

    @abc.abstractmethod
    def stream_range(self, request, offset, length) -> Generator[bytes, None, None]:
        """Stream the file described by the given request, within range."""
        raise NotImplementedError()

    @abc.abstractmethod
    def capacity(self) -> models.AbstractResultQuota:
        """Return quota information for this service."""
        raise NotImplementedError()

    @abc.abstractmethod
    def remove(self, file_id) -> models.AbstractReceiptFile:
        """Remove a file from the service."""
        raise NotImplementedError()

    def __repr__(self):
        return f"{self.__class__.__name__}(\"{self.nickname()}\")"
