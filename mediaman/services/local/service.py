"""
Class to manage a Service connection to the local drive.
"""

from mediaman.services.abstract import service
from mediaman.services.local import methods
from mediaman.services.local import models


class LocalService(service.AbstractService):

    def __init__(self, config):
        super().__init__(models.LocalConfig(config))
        self.destination_path = methods.require_destination_path(self._config.destination)
        # TODO: rename "destination" to "store" or something asymmetrical

    def authenticate(self):
        pass

    def list_files(self):
        return models.LocalResultFileList(
            methods.list_files(self.destination_path)
        )

    def list_file(self, file_id):
        return models.LocalResultFile(
            methods.list_file(self.destination_path, file_id)
        )

    def search_by_name(self, file_name):
        return models.LocalResultFileList(
            methods.search_by_name(self.destination_path, file_name)
        )

    def exists(self, file_id):
        return methods.exists(self.destination_path, file_id)

    def upload(self, request):
        return models.LocalReceiptFile(
            methods.upload(self.destination_path, request)
        )

    def download(self, request):
        return models.LocalDownloadReceiptFile(
            methods.download(self.destination_path, request)
        )

    def capacity(self):
        return models.LocalResultQuota(
            methods.capacity(self.destination_path, self._config.quota)
        )

    def remove(self, file_id):
        return models.LocalReceiptFile(
            methods.remove(self.destination_path, file_id)
        )
