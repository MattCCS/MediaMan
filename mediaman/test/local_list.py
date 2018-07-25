
from mediaman.services import loader

local = loader.load_local()

for file in local.files():
    print(file)
