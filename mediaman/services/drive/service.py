"""
Class to manage a Service connection to Google Drive.
"""

from mediaman.core import logtools
from mediaman.services.abstract import service
from mediaman.services.drive import methods
from mediaman.services.drive import models

logger = logtools.new_logger("mediaman.services.drive.service")


class DriveService(service.AbstractService):

    def __init__(self, config):
        logger.debug(f"Drive init")
        super().__init__(models.DriveConfig(config))

        self._drive = None
        self._folder_id = None
        self._authenticated = False

    def authenticate(self):
        logger.debug(f"Drive authenticated: {self._authenticated}")
        if self._authenticated:
            return
        self._drive = methods.authenticate(self._config.client_secrets, self._config.credentials)
        self._folder_id = methods.ensure_directory(self._drive, self._config.destination)
        self._authenticated = True

    @service.auth
    def list_files(self):
        return models.DriveResultFileList(
            methods.list_files(self._drive, folder_id=self._folder_id)
        )

    @service.auth
    def list_file(self, file_id):
        return models.DriveResultFile(
            methods.list_file(self._drive, file_id)
        )

    @service.auth
    def search_by_name(self, file_name):
        return models.DriveResultFileList(
            methods.search_by_name(
                self._drive,
                file_name,
                folder_id=self._folder_id,
            )
        )

    @service.auth
    def exists(self, file_id):
        return methods.exists(self._drive, file_id, folder_id=self._folder_id)

    @service.auth
    def upload(self, request):
        return models.DriveReceiptFile(
            methods.upload(self._drive, request, folder_id=self._folder_id)
        )

    @service.auth
    def download(self, request):
        return models.DriveDownloadReceiptFile(
            methods.download(self._drive, request, folder_id=self._folder_id)
        )

    @service.auth
    def capacity(self):
        return models.DriveResultQuota(
            methods.capacity(self._drive, self._config.quota)
        )
