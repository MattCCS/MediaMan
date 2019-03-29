import abc

from mediaman.services.abstract import models


class AbstractClient(abc.ABC):

    @abc.abstractmethod
    def name(self) -> str:
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
    def fuzzy_search_by_name(self, file_name) -> models.AbstractResultFileList:
        """List all files with a name similar to the given name."""
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
    def capacity(self) -> models.AbstractResultQuota:
        """Return the capacity stats of the service."""
        raise NotImplementedError()

    # @abc.abstractmethod
    # def get_file_by_hash(self, file_hash):
    #     raise NotImplementedError()

    # @abc.abstractmethod
    # def has_by_uuid(self, identifier):
    #     raise NotImplementedError()
