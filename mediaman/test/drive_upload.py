
from mediaman.services import loader

drive = loader.load_drive()
receipt = drive.put("mediaman/test.txt", "asdf.dat")
print(receipt, receipt.id())

print(drive.exists("asdf.dat"))
print(drive.exists(receipt.id()))
