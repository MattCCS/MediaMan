
from mediaman.core import models
from mediaman.services import loader

drive = loader.load_drive()
receipt = drive.upload(models.Request(id="asdf.dat", path="mediaman/test.txt"))
print(receipt, receipt.id())

print(drive.exists("asdf.dat"))
print(drive.exists(receipt.id()))
print(drive.download(models.Request(id=receipt.id(), path="mediaman/test.download.txt")))
