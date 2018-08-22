
from mediaman.services import loader

local = loader.load_local()
local_list = local.files()

for file in local_list.results():
    print(file.name())
