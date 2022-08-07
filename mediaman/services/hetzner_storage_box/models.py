
from mediaman.services.abstract import models


class HetznerStorageBoxConfig(models.BaseConfig):
    pass


class HetznerStorageBoxReceiptFile(models.AbstractReceiptFile):
    def __init__(self, data):
        self.filename = data["id"]

    def id(self):
        return self.filename


class HetznerStorageBoxDownloadReceiptFile(models.AbstractDownloadReceiptFile, HetznerStorageBoxReceiptFile):
    def __init__(self, data):
        super().__init__(data)
        self._path = data["path"]

    def path(self):
        return self._path


class HetznerStorageBoxResultFile(models.AbstractResultFile):
    def __init__(self, file_data):
        self.filename = file_data["name"]
        self._size = file_data["size"]

    def id(self):
        return self.filename

    def name(self):
        return self.filename

    def size(self):
        return self._size


class HetznerStorageBoxResultFileList(models.AbstractResultFileList):
    def __init__(self, file_list_data):
        self.items = {d["name"]: HetznerStorageBoxResultFile(d) for d in file_list_data}

    def results(self):
        return list(self.items.values())


class HetznerStorageBoxResultQuota(models.AbstractResultQuota):
    def __init__(self, capacity_data):
        self._used = capacity_data["used"]
        self._quota = capacity_data["quota"]
        self._total = capacity_data["total"]

    def used(self):
        return self._used

    def quota(self):
        return self._quota

    def total(self):
        return self._total
