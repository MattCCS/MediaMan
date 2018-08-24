
import abc


class AbstractReceiptFile(abc.ABC):

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()


class AbstractResultFile(abc.ABC):

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def name(self):
        raise NotImplementedError()


class AbstractResultFileList(abc.ABC):

    @abc.abstractmethod
    def results(self):
        raise NotImplementedError()
