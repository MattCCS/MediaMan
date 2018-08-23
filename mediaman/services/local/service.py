"""
Class to manage a Service connection to the local drive.
"""

from mediaman.core import hashenum
from mediaman.services.abstract import service
from mediaman.services.local import methods
from mediaman.services.local.models import resultfile, resultfilelist, receiptfile


class LocalService(service.AbstractService):

    @staticmethod
    def hash_function():
        return hashenum.HashFunctions.SHA256

    def authenticate(self):
        pass

    def list_files(self):
        return resultfilelist.LocalResultFileList(
            methods.list_files()
        )

    def list_file(self, file_id):
        return resultfile.LocalResultFile(
            methods.list_file(file_id)
        )

    def exists(self, file_id):
        return methods.exists(file_id)

    def upload(self, source_file_path, destination_file_name):
        return receiptfile.LocalReceiptFile(
            methods.upload(source_file_path, destination_file_name)
        )

    def download(self, source_file_name, destination_file_path):
        return receiptfile.LocalReceiptFile(
            methods.download(source_file_name, destination_file_path)
        )
