"""
Class to manage a Service connection to Microsoft OneDrive.
"""

from mediaman.core import logtools
from mediaman.services.abstract import service
from mediaman.services.onedrive import methods
from mediaman.services.onedrive import models

logger = logtools.new_logger("mediaman.services.onedrive.service")


class OneDriveService(service.AbstractService):

    def __init__(self, config):
        logger.debug(f"OneDrive init")
        super().__init__(models.OneDriveConfig(config))

        self._onedrive = None
        self._folder_id = None
        self._authenticated = False

    def authenticate(self):
        logger.debug(f"OneDrive authenticated: {self._authenticated}")
        if self._authenticated:
            return
        self._onedrive = methods.authenticate(self._config.client_secrets, self._config.credentials)
        self._folder_id = methods.ensure_directory(self._onedrive, self._config.destination)
        self._authenticated = True

    @service.auth
    def list_files(self):
        return models.OneDriveResultFileList(
            methods.list_files(self._onedrive, folder_id=self._folder_id)
        )

    @service.auth
    def list_file(self, file_id):
        return models.OneDriveResultFile(
            methods.list_file(self._onedrive, file_id)
        )

    @service.auth
    def search_by_name(self, file_name):
        return models.OneDriveResultFileList(
            methods.search_by_name(
                self._onedrive,
                file_name,
                folder_id=self._folder_id,
            )
        )

    @service.auth
    def exists(self, file_id):
        return methods.exists(self._onedrive, file_id, folder_id=self._folder_id)

    @service.auth
    def upload(self, request):
        return models.OneDriveReceiptFile(
            methods.upload(self._onedrive, request, folder_id=self._folder_id)
        )

    @service.auth
    def download(self, request):
        return models.OneDriveDownloadReceiptFile(
            methods.download(self._onedrive, request, folder_id=self._folder_id)
        )

    @service.auth
    def stream(self, request):
        return methods.stream(self._onedrive, request, folder_id=self._folder_id)

    @service.auth
    def stream_range(self, request, offset, length):
        return methods.stream_range(
            self._onedrive, request, folder_id=self._folder_id, offset=offset, length=length
        )

    @service.auth
    def capacity(self):
        return models.OneDriveResultQuota(
            methods.capacity(self._onedrive, self._config.quota)
        )

    @service.auth
    def remove(self, file_id):
        return models.OneDriveReceiptFile(
            methods.remove(self._onedrive, file_id)
        )
