
import uuid

from mediaman.core import crypto
from mediaman.services import loader

service = loader.load_drive()
service = crypto.EncryptionMiddlewareService(service)

random_filename = str(uuid.uuid4())

print(service.exists(random_filename))
result = service.put("mediaman/test.txt", random_filename)
print(result, result.id())
print(service.exists(result.id()))
