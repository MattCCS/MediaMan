
from mediaman.services import loader

drive = loader.load_drive()
receipt = drive.upload("mediaman/test.txt", "asdf.dat")
print(receipt, receipt.id())

print(drive.exists("asdf.dat"))
print(drive.exists(receipt.id()))
print(drive.download(receipt.id(), "test.download.txt"))
