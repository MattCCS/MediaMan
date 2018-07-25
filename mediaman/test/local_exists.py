
from mediaman.services import loader

local = loader.load_local()

print(local.exists("test.txt"))
