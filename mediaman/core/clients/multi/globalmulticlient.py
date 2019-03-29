
from mediaman.core.clients.multi import abstract
from mediaman.core.clients.multi import methods
from mediaman.core.models import MultiResultQuota


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
        deduped_results = {}
        for result in gen_all(methods.list_files(self.clients)):
            for result in result.response:
                if result["hash"] not in deduped_results:
                    deduped_results[result["hash"]] = result
                    yield {"id": result["id"], "name": result["name"], "hash": result["hash"]}

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
        results = gen_all(methods.capacity(self.clients))
        grand_used = grand_allowed = grand_total = 0
        is_partial = False
        for result in results:
            if result.response:
                response = result.response
                grand_used += response.used()
                grand_allowed += response.allowed()
                grand_total += response.total()
            else:
                is_partial = True
        return MultiResultQuota(grand_used, grand_allowed, grand_total, is_partial)
