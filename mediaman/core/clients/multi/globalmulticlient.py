
from mediaman.core.clients.multi import abstract
from mediaman.core.clients.multi import methods


def gen_first_valid(gen):
    try:
        result = next(gen)
        while True:
            if result.response:
                yield result
                gen.send(False)
            else:
                result = gen.send(True)
    except StopIteration:
        pass


class GlobalMulticlient(abstract.AbstractMulticlient):

    def list_files(self):
        raise NotImplementedError()

    def list_file(self, file_id):
        raise NotImplementedError()

    def search_by_name(self, file_name):
        return gen_first_valid(methods.search_by_name(self.clients, file_name))

    def fuzzy_search_by_name(self, file_name):
        raise NotImplementedError()

    def exists(self, file_id):
        raise NotImplementedError()

    def upload(self, file_path):
        raise NotImplementedError()

    def download(self, file_path):
        raise NotImplementedError()

    def capacity(self):
        raise NotImplementedError()
