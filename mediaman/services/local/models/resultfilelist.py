
from mediaman.core.models import resultfilelist
from mediaman.services.local.models import resultfile


class LocalResultFileList(resultfilelist.AbstractResultFileList):

    def __init__(self, file_list_data):
        self.items = {d["name"]: resultfile.LocalResultFile(d) for d in file_list_data}

    def results(self):
        return self.items.values()
