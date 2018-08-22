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

    def files(self):
        return resultfilelist.LocalResultFileList(
            methods.files()
        )

    def exists(self, file_id):
        return methods.exists(file_id)

    def put(self, source_file_path, destination_file_name):
        return receiptfile.LocalReceiptFile(
            methods.put(source_file_path, destination_file_name)
        )

    def get(self, file_id):
        return resultfile.LocalResultFile(
            methods.get(file_id)
        )
