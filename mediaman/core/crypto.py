
import tempfile

from mediaman.services.abstract import service


class EncryptionMiddlewareService(service.AbstractService):

    def __init__(self, service):
        self.service = service

    def encrypt(self, file_path):
        tempfile_ref = tempfile.NamedTemporaryFile(mode="wb+")
        with open(file_path, "rb") as infile:
            # TODO: encrypt
            tempfile_ref.write(b"ENCRYPT:" + infile.read())
            tempfile_ref.seek(0)
        return tempfile_ref

    def hash_function(self):
        return self.service.hash_function()

    def authenticate(self):
        self.service.authenticate()

    def files(self):
        return self.service.files()

    def exists(self, file_id):
        return self.service.exists(file_id)

    def put(self, source_file_path, destination_file_path):
        with self.encrypt(source_file_path) as encrypted_tempfile:
            encrypted_file_path = encrypted_tempfile.name
            return self.service.put(
                encrypted_file_path,
                destination_file_path
            )

    def get(self, file_id):
        return self.decrypt(self.service.get(file_id))
