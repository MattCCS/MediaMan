
import uuid

from mediaman.core import models
from mediaman.services import loader

local = loader.load_local()

random_filename = str(uuid.uuid4())

print(local.exists(random_filename))
print(local.upload(models.Request(id=random_filename, path="mediaman/test.txt")))
print(local.exists(random_filename))
print(local.download(models.Request(id=random_filename, path="mediaman/test.download.txt")))
