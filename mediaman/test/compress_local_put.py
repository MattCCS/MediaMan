
import uuid

from mediaman.core import compression
from mediaman.services import loader

service = loader.load_local()
service = compression.CompressionMiddlewareService(service)

random_filename = str(uuid.uuid4())

print(service.exists(random_filename))
result = service.upload("mediaman/test.txt", random_filename)
print(result, result.id())
print(service.exists(result.id()))
print(service.download(random_filename, "mediaman/test.download.txt"))
