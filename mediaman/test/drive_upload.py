
import json

from mediaman.services import loader

drive = loader.load_drive()
receipt = drive.put("mediaman/test.txt", "asdf.dat")
print(json.dumps(receipt, indent=4))

print(drive.exists("asdf.dat"))
print(drive.exists("14wASfQiiJk_ykBhArw6iY5G9QLZgx6q7"))
