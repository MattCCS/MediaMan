
from mediaman.core import hashing


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


class Request:

    def __init__(self, id=None, path=None, hash=None, cacheable=False):
        self._id = id
        self._path = path
        self._hash = hash
        self._cacheable = cacheable

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

    @property
    def hash(self):
        if self._hash is None:
            self._hash = hashing.hash(self._path)
        return self._hash

    @hash.setter
    def hash(self, value):
        self._hash = value

    def __repr__(self):
        # logging should not trigger a call to hash
        return f"Request({self.id}, {self.path}, {self._hash})"


class Response:
    def __init__(self, client, response, exception: Exception):
        self._client = client
        self._response = response
        self._exception = exception

    @property
    def client(self):
        return self._client

    @property
    def response(self):
        return self._response

    @property
    def exception(self):
        return self._exception

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.client)}, {repr(self.response)}, {repr(self.exception)})"


class MultiResultQuota:
    def __init__(self, used, allowed, total, is_partial: bool):
        self.used = used
        self.allowed = allowed
        self.total = total
        self.is_partial = is_partial

    def __repr__(self):
        at_least = 'at least ' if self.is_partial else ''
        return f"{type(self)}({self.used / self.allowed:.0%} ({at_least}{human_bytes(self.used)} / {at_least}{human_bytes(self.allowed)}) (potentially {at_least}{human_bytes(self.total)}))"
