
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
