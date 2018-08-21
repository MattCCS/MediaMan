
import abc


class AbstractResultFileList(abc.ABC):

    @abc.abstractmethod
    def results(self):
        raise NotImplementedError()
