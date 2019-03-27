
from mediaman.core.clients.multi import abstract
from mediaman.core.clients.multi import methods


def gen_all(gen):
    try:
        result = next(gen)
        yield result
        while True:
            result = gen.send(True)
            yield result
    except StopIteration:
        pass


class Multiclient(abstract.AbstractMulticlient):

    def list_files(self):
        return gen_all(methods.list_files(self.clients))

    def list_file(self, file_id):
        raise NotImplementedError()

    def search_by_name(self, file_name):
        return gen_all(methods.search_by_name(self.clients, file_name))

    def fuzzy_search_by_name(self, file_name):
        return gen_all(methods.fuzzy_search_by_name(self.clients, file_name))

    def exists(self, file_id):
        return gen_all(methods.exists(self.clients, file_id))

    def upload(self, file_path):
        raise NotImplementedError()

    def download(self, file_path):
        raise NotImplementedError()

    def capacity(self):
        return gen_all(methods.capacity(self.clients))
