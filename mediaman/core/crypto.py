
from mediaman.services.abstract import service


class EncryptionMiddlewareService(service.AbstractService):

    def __init__(self, service):
        self.service = service

    def hash_function(self):
        return self.service.hash_function()

    def authenticate(self):
        self.service.authenticate()

    def files(self):
        return (self.decrypt(f) for f in self.service.files())

    def exists(self, file_id):
        return self.service.exists(file_id)

    def put(self, source_file_path, destination_file_path):
        return self.service.put(
            self.encrypt(source_file_path),
            destination_file_path
        )

    def get(self, file_id):
        return self.decrypt(self.service.get(file_id))
