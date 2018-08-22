"""
Class to manage a Service connection to Google Drive.
"""

from mediaman.core import hashenum
from mediaman.services.abstract import service
from mediaman.services.drive import methods
from mediaman.services.drive.models import resultfile, resultfilelist, receiptfile


class DriveService(service.AbstractService):

    def __init__(self):
        self.drive = None

    @staticmethod
    def hash_function():
        return hashenum.HashFunctions.MD5

    def authenticate(self):
        self.drive = methods.authenticate()

    def files(self):
        return resultfilelist.DriveResultFileList(
            methods.files(self.drive)
        )

    def exists(self, file_id):
        return methods.exists(self.drive, file_id)

    def put(self, source_file_path, destination_file_name):
        return receiptfile.DriveReceiptFile(
            methods.put(self.drive, source_file_path, destination_file_name)
        )

    def get(self, file_id):
        return resultfile.DriveResultFile(
            methods.get(self.drive, file_id)
        )
