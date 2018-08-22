
import abc


class AbstractReceiptFile(abc.ABC):

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()
