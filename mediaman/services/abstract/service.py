
import abc


class AbstractService(abc.ABC):

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
    def upload(self, request):
        """Returns an AbstractReceiptFile instance."""
        raise NotImplementedError()

    @abc.abstractmethod
    def download(self, request):
        """Returns an AbstractReceiptFile instance."""
        raise NotImplementedError()
