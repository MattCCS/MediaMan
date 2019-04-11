
import shutil
import tempfile
import zlib

from mediaman.middleware import abstract


class CompressionMiddlewareService(abstract.SimpleMiddleware):

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

    def upload(self, request):
        with self.compress(request.path) as compressed_tempfile:
            request.path = compressed_tempfile.name
            return self.service.upload(request)

    def download(self, request):
        return self.decompress(
            self.service.download(request)
        )
