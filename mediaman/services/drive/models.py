
import pathlib

from mediaman import config
from mediaman.services.abstract import models


class DriveConfig(models.BaseConfig):

    def __init__(self, _config):
        super().__init__(_config)
        client_secrets = self.extra["GOOGLE_CLIENT_SECRETS"]
        credentials = self.extra["GOOGLE_CREDENTIALS"]

        client_secrets = pathlib.Path(client_secrets).expanduser()
        credentials = pathlib.Path(credentials).expanduser()

        if not client_secrets.is_absolute():
            client_secrets = config.ROOT_PATH / client_secrets
        if not credentials.is_absolute():
            credentials = config.ROOT_PATH / credentials

        self.client_secrets = client_secrets
        self.credentials = credentials


class DriveReceiptFile(models.AbstractReceiptFile):

    def __init__(self, file_data):
        self._id = file_data["id"]

    def id(self):
        return self._id


class DriveDownloadReceiptFile(models.AbstractDownloadReceiptFile, DriveReceiptFile):

    def __init__(self, file_data):
        super().__init__(file_data)
        self._path = file_data["path"]

    def path(self):
        return self._path


class DriveResultFile(models.AbstractResultFile):

    def __init__(self, file_data):
        self._id = file_data["id"]
        self.title = file_data.get("title", "")
        self.file_size = int(file_data["fileSize"])

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

    def size(self):
        return self.file_size


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
