"""
Class to manage a Service connection to the local disk.
"""

from mediaman.core import hashenum
from mediaman.core import service
from mediaman.services.local import methods
# TODO: implement these
# from mediaman.services.local.models import resultfile, resultfilelist


class LocalService(service.AbstractService):

    @staticmethod
    def hash_function():
        return hashenum.HashFunctions.SHA256

    def authenticate(self):
        pass

    def files(self):
        # TODO: convert files
        return (
            methods.files()
        )

    def exists(self, file_id):
        return methods.exists(file_id)

    def put(self, file_id, file_path):
        # TODO: return a "LocalReceiptFile"-type object
        return methods.put(file_id, file_path)

    def get(self, file_id):
        # TODO: convert file
        return (
            methods.get(file_id)
        )
