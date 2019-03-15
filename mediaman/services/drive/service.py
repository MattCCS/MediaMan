"""
Class to manage a Service connection to Google Drive.
"""

from mediaman.services.abstract import service
from mediaman.services.drive import methods
from mediaman.services.drive import models


class DriveService(service.AbstractService):

    def __init__(self):
        self.drive = None
        self.folder_id = None
        self._authenticated = False

    def authenticate(self):
        if self._authenticated:
            return
        self.drive = methods.authenticate()
        self.folder_id = methods.ensure_directory(self.drive)
        self._authenticated = True

    @service.auth
    def list_files(self):
        return models.DriveResultFileList(
            methods.list_files(self.drive, folder_id=self.folder_id)
        )

    @service.auth
    def list_file(self, file_id):
        return models.DriveResultFile(
            methods.list_file(self.drive, file_id)
        )

    @service.auth
    def search_by_name(self, file_name):
        return models.DriveResultFileList(
            methods.search_by_name(
                self.drive,
                file_name,
                folder_id=self.folder_id,
            )
        )

    @service.auth
    def exists(self, file_id):
        return methods.exists(self.drive, file_id, folder_id=self.folder_id)

    @service.auth
    def upload(self, request):
        return models.DriveReceiptFile(
            methods.upload(self.drive, request, folder_id=self.folder_id)
        )

    @service.auth
    def download(self, request):
        return models.DriveReceiptFile(
            methods.download(self.drive, request, folder_id=self.folder_id)
        )

    @service.auth
    def capacity(self):
        return models.DriveResultQuota(
            methods.capacity(self.drive)
        )
