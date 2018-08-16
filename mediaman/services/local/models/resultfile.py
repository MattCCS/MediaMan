
import abc


class LocalResultFile(abc.ABC):

    def __init__(self, file_data):
        self.filename = file_data["filename"]
        self.kind = file_data["kind"]
        self.file_extension = file_data["file_extension"]
        self.checksum = file_data["checksum"]
        self.accessed_date = file_data["accessedDate"]
        self.modified_date = file_data["modifiedDate"]
        self.created_date = file_data["createdDate"]

    def id(self):
        return self.filename

    def name(self):
        return self.filename

    def hash(self):
        return self.checksum
