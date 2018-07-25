
import json

from mediaman.services import loader
from mediaman.services.drive.models import resultfilelist

drive = loader.load_drive()
raw_file_list = drive.files()
print(json.dumps(raw_file_list))

file_list = resultfilelist.DriveResultFileList(raw_file_list)

for result in file_list.results():
    print(f"{result.id()}: {result.name()} ({result.hash()})")
