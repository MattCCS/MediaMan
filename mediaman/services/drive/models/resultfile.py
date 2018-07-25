
from mediaman.core.models import resultfile


class DriveResultFile(resultfile.AbstractResultFile):

    def __init__(self, file_data):
        self._id = file_data["id"]
        self.title = file_data["title"]
        self.kind = file_data["kind"]
        self.md5_checksum = file_data.get("md5Checksum", "")
        # self.etag = file_data["etag"]
        self.self_link = file_data["selfLink"]
        # self.alternate_link = file_data["alternateLink"]
        # self.embed_link = file_data["embedLink"]
        # self.icon_link = file_data["iconLink"]
        # self.thumbnail_link = file_data["thumbnailLink"]
        self.mime_type = file_data["mimeType"]
        self.labels = file_data["labels"]
        self.created_date = file_data["createdDate"]
        self.modified_date = file_data["modifiedDate"]

    def id(self):
        return self._id

    def name(self):
        return self.title

    def hash(self):
        return self.md5_checksum
