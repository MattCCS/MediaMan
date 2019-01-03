
import shutil
import tempfile
import zlib

from mediaman.services.abstract import service


class CompressionMiddlewareService(service.AbstractService):

    def __init__(self, service):
        self.service = service

    def compress(self, file_path):
        tempfile_ref = tempfile.NamedTemporaryFile(mode="wb+")
        with open(file_path, "rb") as infile:
            tempfile_ref.write(zlib.compress(infile.read(), level=9))
            tempfile_ref.seek(0)
        return tempfile_ref

    def decompress(self, receipt):
        file_path = receipt.id()

        # decompress to tempfile
        tempfile_ref = tempfile.NamedTemporaryFile(mode="wb+", delete=False)
        with open(file_path, "rb") as infile:
            tempfile_ref.write(zlib.decompress(infile.read()))

        # replace original file
        decompressed_file_path = tempfile_ref.name
        shutil.move(decompressed_file_path, file_path)

        return receipt

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
        with self.compress(request.path) as compressed_tempfile:
            request.path = compressed_tempfile.name
            return self.service.upload(request)

    def download(self, request):
        return self.decompress(
            self.service.download(request)
        )
