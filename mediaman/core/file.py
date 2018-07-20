

class File:

    def __init__(self, id):
        self.id = id

    def id(self):
        return self.id

    def data(self):
        raise NotImplementedError()

    def data_hash(self):
        raise NotImplementedError()

    def data_filename(self):
        return f"{self.id}.data"

    def metadata(self):
        raise NotImplementedError()

    def metadata_hash(self):
        raise NotImplementedError()

    def metadata_filename(self):
        return f"{self.id}.metadata"

    def type(self):
        raise NotImplementedError()

    def format(self):
        raise NotImplementedError()

    def duration(self):
        raise NotImplementedError()

    def tags(self):
        raise NotImplementedError()
