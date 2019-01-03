
import abc

from mediaman.services.abstract import models


class AbstractService(abc.ABC):

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
