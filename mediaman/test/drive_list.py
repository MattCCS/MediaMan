
from mediaman.services import loader

drive = loader.load_drive()
file_list = drive.files()

for result in file_list.results():
    print(f"{result.id()}: {result.name()}")
