
from mediaman.core.models import receiptfile


class LocalReceiptFile(receiptfile.AbstractReceiptFile):

    def __init__(self, filename):
        self.filename = filename

    def id(self):
        return self.filename
