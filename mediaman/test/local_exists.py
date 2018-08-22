
from mediaman.services import loader

local = loader.load_local()

print(local.exists("missing.txt"))
print(local.exists("test.txt"))
