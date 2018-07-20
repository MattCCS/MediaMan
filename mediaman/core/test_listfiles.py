
import json

from mediaman.services import loader
from mediaman.services.drive.models import drivefilelist

drive = loader.load_drive()
raw_file_list = drive.files()
print(json.dumps(raw_file_list))

file_list = drivefilelist.DriveFileList(raw_file_list)
