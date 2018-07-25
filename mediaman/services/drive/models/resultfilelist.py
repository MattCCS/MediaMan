
from mediaman.core.models import resultfilelist
from mediaman.services.drive.models import resultfile


class DriveResultFileList(resultfilelist.AbstractResultFileList):

    def __init__(self, file_list_data):
        self.kind = file_list_data["kind"]
        self.etag = file_list_data["etag"]
        # self.self_link = file_list_data["selfLink"]
        self.next_link = file_list_data["nextLink"]
        self.next_page_token = file_list_data["nextPageToken"]
        self.incomplete_search = file_list_data["incompleteSearch"]
        self.items = {d["id"]: resultfile.DriveResultFile(d) for d in file_list_data["items"]}

    def results(self):
        return self.items.values()
