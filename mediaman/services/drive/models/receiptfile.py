
from mediaman.core.models import receiptfile


class DriveReceiptFile(receiptfile.AbstractReceiptFile):

    def __init__(self, file_data):
        self._id = file_data["id"]

    def id(self):
        return self._id
