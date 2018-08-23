
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

    def search_by_name(self, file_name):
        return self.service.search_by_name(file_name)

    def exists(self, file_id):
        return self.service.exists(file_id)

    def upload(self, request):
        with self.encrypt(request.path) as encrypted_tempfile:
            request.path = encrypted_tempfile.name
            return self.service.upload(request)

    def download(self, request):
        # TODO: implement decrypt (need file path)
        raise NotImplementedError()
