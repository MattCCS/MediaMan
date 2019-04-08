
from mediaman.services.abstract import models


class DriveConfig(models.BaseConfig):

    def __init__(self, config):
        super().__init__(config)
        self.client_secrets = self.extra["GOOGLE_CLIENT_SECRETS"]
        self.credentials = self.extra["GOOGLE_CREDENTIALS"]


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
        return list(self.items.values())


class DriveResultQuota(models.AbstractResultQuota):

    def __init__(self, quota_data):
        self._used = quota_data["used"]
        self._quota = quota_data["quota"]
        self._total = quota_data["total"]
        self._trashed = quota_data["trashed"]

    def used(self):
        return self._used

    def quota(self):
        return self._quota

    def total(self):
        return self._total
