
import abc


class AbstractService(abc.ABC):

    @abc.abstractstaticmethod
    def hash_function(self):
        raise NotImplementedError()

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
    def get(self, file_id):
        raise NotImplementedError()
