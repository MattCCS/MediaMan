
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

    def list_files(self):
        return self.service.list_files()

    def list_file(self, file_id):
        return self.service.list_file(file_id)

    def exists(self, file_id):
        return self.service.exists(file_id)

    def upload(self, source_file_path, destination_file_path):
        with self.encrypt(source_file_path) as encrypted_tempfile:
            encrypted_file_path = encrypted_tempfile.name
            return self.service.upload(
                encrypted_file_path,
                destination_file_path
            )

    def download(self, source_file_name, destination_file_path):
        # TODO: implement decrypt (need file path)
        raise NotImplementedError()
