
import abc


class AbstractReceiptFile(abc.ABC):

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"ReceiptFile({self.id()})"


class AbstractResultFile(abc.ABC):

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def name(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"{type(self)}({self.id()}, {self.name()})"


class AbstractResultFileList(abc.ABC):

    @abc.abstractmethod
    def results(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"{type(self)}({self.results()})"
