
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


def human_bytes(n):
    """Return the given bytes as a human-friendly string"""

    step = 1024
    abbrevs = ['KB', 'MB', 'GB', 'TB']

    if n < step:
        return f"{n}B"

    for abbrev in abbrevs:
        n /= step
        if n < step:
            break

    return f"{n:.2f}{abbrev}"


class AbstractResultQuota(abc.ABC):

    @abc.abstractmethod
    def used(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def total(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"{type(self)}({self.used() / self.total():.0%} ({human_bytes(self.used())} / {human_bytes(self.total())}))"
