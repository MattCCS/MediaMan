
import json

from mediaman.services import loader

drive = loader.load_drive()
receipt = drive.put("asdf.dat", "mediaman/test.txt")
print(json.dumps(receipt, indent=4))
