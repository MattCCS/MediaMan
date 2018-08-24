
from mediaman.services.abstract import models


class LocalReceiptFile(models.AbstractReceiptFile):

    def __init__(self, filename):
        self.filename = filename

    def id(self):
        return self.filename


class LocalResultFile(models.AbstractResultFile):

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


class LocalResultFileList(models.AbstractResultFileList):

    def __init__(self, file_list_data):
        self.items = {d["name"]: LocalResultFile(d) for d in file_list_data}

    def results(self):
        return self.items.values()