
import abc


class AbstractFile(abc.ABC):

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def data(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def data_hash(self):
        raise NotImplementedError()

    def data_filename(self):
        return f"{self.id()}.data"

    @abc.abstractmethod
    def metadata(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def metadata_hash(self):
        raise NotImplementedError()

    def metadata_filename(self):
        return f"{self.id()}.metadata"

    @abc.abstractmethod
    def type(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def format(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def duration(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def tags(self):
        raise NotImplementedError()
