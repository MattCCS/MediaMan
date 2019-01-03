
import concurrent.futures
import random
import time


class Multiclient:

    def __init__(self, clients):
        self.clients = clients

    # def get_file_by_hash(self, file_hash):
    #     return self.index_manager.get_file_by_hash(file_hash)

    # def list_files(self):
    #     return list(self.index_manager.list_files())

    def list_file(self, file_id):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(client.list_file, file_id) for client in self.clients]
            for future in concurrent.futures.as_completed(futures):
                try:
                    return future.result()
                except Exception as exc:
                    print(type(exc))

    # def has_by_uuid(self, identifier):
    #     return self.index_manager.has_by_uuid(identifier)

    # def search_by_name(self, file_name):
    #     return list(self.index_manager.search_by_name(file_name))

    def exists(self, file_id):
        raise NotImplementedError()

    # def upload(self, file_path):
    #     return self.index_manager.upload(file_path)

    # def download(self, file_path):
    #     path = pathlib.Path(file_path)
    #     identifier = path.name
    #     return self.index_manager.download(identifier)


class Client1:
    def list_file(self, file_id):
        time.sleep(random.random())
        if random.randint(0, 1):
            raise FloatingPointError()
        return 1


class Client2:
    def list_file(self, file_id):
        time.sleep(random.random())
        return 2


m = Multiclient([Client1(), Client2()])
# loop = asyncio.get_event_loop()
# loop.wait(m.list_file('x'))
print(m.list_file('x'))
