
import abc


class AbstractService(abc.ABC):

    @abc.abstractmethod
    def authenticate(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def files(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def exists(self, file_id):
        raise NotImplementedError()

    @abc.abstractmethod
    def put(self, file_id, file_path):
        raise NotImplementedError()

    @abc.abstractmethod
    def data(self, file_id):
        raise NotImplementedError()

    @abc.abstractmethod
    def metadata(self, file_id):
        raise NotImplementedError()
