
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
        with self.compress(source_file_path) as compressed_tempfile:
            compressed_file_path = compressed_tempfile.name
            return self.service.upload(
                compressed_file_path,
                destination_file_path,
            )

    def download(self, source_file_name, destination_file_path):
        return self.decompress(
            self.service.download(
                source_file_name,
                destination_file_path,
            )
        )
