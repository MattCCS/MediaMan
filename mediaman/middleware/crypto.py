
import tempfile

from mediaman.middleware import simple


class EncryptionMiddlewareService(simple.SimpleMiddleware):

    ENCRYPTION_MIDDLEWARE_FILENAME = "index"
    ENCRYPTION_MIDDLEWARE_COMMAND_PATH_DEFAULT = "/usr/bin/openssl"
    ENCRYPTION_MIDDLEWARE_COMMAND_PATH = "/usr/local/Cellar/libressl/2.9.2/bin/openssl"

    def encrypt(self, file_path):
        tempfile_ref = tempfile.NamedTemporaryFile(mode="wb+")
        with open(file_path, "rb") as infile:
            # TODO: encrypt
            tempfile_ref.write(b"ENCRYPT:" + infile.read())
            tempfile_ref.seek(0)
        return tempfile_ref

    def upload(self, request):
        with self.encrypt(request.path) as encrypted_tempfile:
            request.path = encrypted_tempfile.name
            return self.service.upload(request)

    def download(self, request):
        # TODO: implement decrypt (need file path)
        raise NotImplementedError()
