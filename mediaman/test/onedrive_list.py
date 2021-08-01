
from mediaman.services import loader

onedrive = loader.load_onedrive()
file_list = onedrive.list_files()

for result in file_list.results():
    print(f"{result.id()}: {result.name()}")
