
class Request:

    def __init__(self, id=None, path=None):
        assert id and path
        self._id = id
        self._path = path

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


class MultiResponse:
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
        return f"{self.name()}({repr(self.client)}, {repr(self.response)}, {repr(self.exception)})"
