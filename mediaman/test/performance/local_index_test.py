import logging
import os
import pathlib
import time

from mediaman.core import api, policy


# logging.getLogger("mattccs").setLevel("DEBUG")


ROOT = pathlib.Path()
SERVICE_SELECTOR = "devnull"
FILEPATH = pathlib.Path("random.bin").absolute()

NUM = 100

service = policy.load_client(service_selector=SERVICE_SELECTOR)


# l1 = len(api.run_list(service_selector=SERVICE_SELECTOR))
l1 = len(service.list_files())

for i in range(NUM):
    with open(FILEPATH, "wb") as outfile:
        outfile.write(os.urandom(32))

    t0 = time.time()
    # next(api.run_put(ROOT, FILEPATH, service_selector=SERVICE_SELECTOR))
    next(service.upload(ROOT, FILEPATH))
    t1 = time.time()
    print(t1 - t0)


# l2 = len(api.run_list(service_selector=SERVICE_SELECTOR))
l2 = len(service.list_files())
print(l1, l2)
print(f"Wrote {NUM} files")
