
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


def gen_all(gen):
    try:
        result = next(gen)
        yield result
        while True:
            result = gen.send(True)
            yield result
    except StopIteration:
        pass


class GlobalMulticlient(abstract.AbstractMulticlient):

    def list_files(self):
        results = gen_all(methods.list_files(self.clients))
        flat_results = [result for response in [result.response for result in results] for result in response]
        deduped_results = {r["hash"]: r for r in flat_results}
        return [{"id": r["id"], "name": r["name"], "hash": r["hash"]} for r in deduped_results.values()]

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
