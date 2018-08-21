
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
    def files(self):
        """Returns an AbstractResultFileList instance."""
        raise NotImplementedError()

    @abc.abstractmethod
    def exists(self, file_id):
        """Returns a boolean."""
        raise NotImplementedError()

    @abc.abstractmethod
    def put(self, source_file_path, destination_file_name):
        """Returns an AbstractReceiptFile instance."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get(self, file_id):
        """Returns an AbstractResultFile instance."""
        raise NotImplementedError()
