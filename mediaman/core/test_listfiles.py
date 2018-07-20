
from mediaman.services import loader

drive = loader.load_drive()
print(drive.files())
