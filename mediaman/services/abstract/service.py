
import abc


class AbstractService(abc.ABC):

    @abc.abstractstaticmethod
    def hash_function(self):
        """Returns the hash function used by the service."""
        raise NotImplementedError()

    @abc.abstractmethod
    def authenticate(self):
        """Authenticates with the service, if necessary.  Returns None."""
        raise NotImplementedError()

    @abc.abstractmethod
    def list_files(self):
        """Returns an AbstractResultFileList instance."""
        raise NotImplementedError()

    @abc.abstractmethod
    def list_file(self, file_id):
        """Returns an AbstractResultFile instance."""
        raise NotImplementedError()

    @abc.abstractmethod
    def search_by_name(self, file_name):
        """Returns an AbstractResultFileList instance."""
        raise NotImplementedError()

    @abc.abstractmethod
    def exists(self, file_id):
        """Returns a boolean."""
        raise NotImplementedError()

    @abc.abstractmethod
    def upload(self, source_file_path, destination_file_name):
        """Returns an AbstractReceiptFile instance."""
        raise NotImplementedError()

    @abc.abstractmethod
    def download(self, source_file_name, destination_file_path):
        """Returns an AbstractReceiptFile instance."""
        raise NotImplementedError()
