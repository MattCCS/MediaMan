
import abc


class BaseConfig(abc.ABC):

    def __init__(self, config):
        self._config = config
        self.nickname = self._config["nickname"]
        self.type = self._config["type"]
        self.quota = self._config["quota"]
        self.destination = self._config["destination"]
        self.cost = self._config["cost"]
        self.extra = self._config["extra"]


class AbstractReceiptFile(abc.ABC):

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"ReceiptFile({self.id()})"


class AbstractDownloadReceiptFile(AbstractReceiptFile):

    @abc.abstractmethod
    def path(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"DownloadReceiptFile({self.id()}, {self.path()})"


class AbstractResultFile(abc.ABC):

    @abc.abstractmethod
    def id(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def name(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def size(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"{type(self)}({self.id()}, {self.name()}, {self.size()})"


class AbstractResultFileList(abc.ABC):

    @abc.abstractmethod
    def results(self):
        raise NotImplementedError()

    def __repr__(self):
        return f"{type(self)}({self.results()})"


def human_bytes(n):
    """Return the given bytes as a human-friendly string"""

    step = 1000
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
        """The amount currently used."""
        raise NotImplementedError()

    @abc.abstractmethod
    def quota(self):
        """The amount quota by the current quota (if any)."""
        raise NotImplementedError()

    @abc.abstractmethod
    def total(self):
        """The total capacity of the service."""
        raise NotImplementedError()

    def allowed(self):
        """The practical maximum allowed (by the total and quota)."""
        return min(self.quota(), self.total()) if (self.quota() is not None) else self.total()

    def available(self):
        """The practical maximum space left (allowed - used)."""
        return self.allowed() - self.used()

    def __repr__(self):
        return f"{type(self)}({self.used() / self.allowed():.0%} ({human_bytes(self.used())} / {human_bytes(self.allowed())}) (potentially {human_bytes(self.total())}))"
