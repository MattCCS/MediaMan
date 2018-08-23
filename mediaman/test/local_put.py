
import uuid

from mediaman.services import loader

local = loader.load_local()

random_filename = str(uuid.uuid4())

print(local.exists(random_filename))
print(local.upload("mediaman/test.txt", random_filename))
print(local.exists(random_filename))
print(local.download(random_filename, "mediaman/test.download.txt"))
