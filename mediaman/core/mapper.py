

from mediaman.services.abstract import service


class MapperMiddlewareService(service.AbstractService):

    def __init__(self, service):
        self.service = service

    def hash_function(self):
        return self.service.hash_function()

    def authenticate(self):
        self.service.authenticate()

    def list_files(self):
        return self.service.list_files()

    def list_file(self, file_id):
        # TODO: implement
        raise NotImplementedError()
        return self.service.list_file(file_id)

    def exists(self, file_id):
        # TODO: implement
        raise NotImplementedError()
        return self.service.exists(file_id)

    def upload(self, source_file_path, destination_file_path):
        # TODO: implement
        raise NotImplementedError()
        return self.service.upload(
            source_file_path,
            destination_file_path,
        )
