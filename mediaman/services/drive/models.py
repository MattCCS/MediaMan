
from mediaman.services.abstract import models


class DriveReceiptFile(models.AbstractReceiptFile):

    def __init__(self, file_data):
        self._id = file_data["id"]

    def id(self):
        return self._id


class DriveResultFile(models.AbstractResultFile):

    def __init__(self, file_data):
        self._id = file_data["id"]
        self.title = file_data.get("title", "")

        self.md5_checksum = file_data.get("md5Checksum", "")
        self.kind = file_data.get("kind", "")
        self.self_link = file_data.get("selfLink", "")
        self.mime_type = file_data.get("mimeType", "")
        self.labels = file_data.get("labels", "")
        self.created_date = file_data.get("createdDate", "")
        self.modified_date = file_data.get("modifiedDate", "")

        # self.etag = file_data["etag"]
        # self.alternate_link = file_data["alternateLink"]
        # self.embed_link = file_data["embedLink"]
        # self.icon_link = file_data["iconLink"]
        # self.thumbnail_link = file_data["thumbnailLink"]

    def id(self):
        return self._id

    def name(self):
        return self.title


class DriveResultFileList(models.AbstractResultFileList):

    def __init__(self, file_list_data):
        self.items = {d["id"]: DriveResultFile(d) for d in file_list_data["items"]}

        self.kind = file_list_data.get("kind", "")
        self.etag = file_list_data.get("etag", "")
        self.next_link = file_list_data.get("nextLink", "")
        self.next_page_token = file_list_data.get("nextPageToken", "")
        self.incomplete_search = file_list_data.get("incompleteSearch", "")

        # self.self_link = file_list_data.get("selfLink", "")

    def results(self):
        return self.items.values()
