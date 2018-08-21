
from mediaman.core.models import resultfile


class LocalResultFile(resultfile.AbstractResultFile):

    def __init__(self, file_data):
        self.filename = file_data["name"]

        self.file_extension = file_data["suffix"]

        stat = file_data["stat"]
        self.size = stat.st_size,
        self.accessedDate = stat.st_atime,
        self.modifiedDate = stat.st_mtime,
        self.createdDate = stat.st_ctime,

    def id(self):
        return self.filename

    def name(self):
        return self.filename
