"""
Class to manage a Service connection to a Hetzner Storage Box.
"""

from mediaman.services.abstract import service
from mediaman.services.hetzner_storage_box import methods
from mediaman.services.hetzner_storage_box import models


class HetznerStorageBoxService(service.AbstractService):

    def __init__(self, config):
        super().__init__(models.HetznerStorageBoxConfig(config))
        self.destination_path = methods.require_destination_path(self._config.destination)
        # TODO: rename "destination" to "store" or something asymmetrical

    def authenticate(self):
        pass

    def list_files(self):
        raise NotImplementedError()
    #     return models.HetznerStorageBoxResultFileList(
    #         methods.list_files(self.destination_path)
    #     )

    def list_file(self, file_id):
        raise NotImplementedError()
    #     return models.HetznerStorageBoxResultFile(
    #         methods.list_file(self.destination_path, file_id)
    #     )

    def search_by_name(self, file_name):
        return models.HetznerStorageBoxResultFileList(
            methods.search_by_name(self._config.extra, self.destination_path, file_name)
        )

    def exists(self, file_id):
        raise NotImplementedError()
    #     return methods.exists(self.destination_path, file_id)

    def upload(self, request):
        return models.HetznerStorageBoxReceiptFile(
            methods.upload(self._config.extra, self.destination_path, request)
        )

    def download(self, request):
        return models.HetznerStorageBoxDownloadReceiptFile(
            methods.download(self._config.extra, self.destination_path, request)
        )

    def stream(self, request):
        raise NotImplementedError()
    #     return methods.stream(self.destination_path, request)

    def stream_range(self, request, offset, length):
        return methods.stream_range(self._config.extra, self.destination_path, request, offset, length)

    def capacity(self):
        return models.HetznerStorageBoxResultQuota(
            methods.capacity(self.destination_path, self._config.quota, self._config.extra)
        )

    def remove(self, file_id):
        raise NotImplementedError()
    #     return models.HetznerStorageBoxReceiptFile(
    #         methods.remove(self.destination_path, file_id)
    #     )
