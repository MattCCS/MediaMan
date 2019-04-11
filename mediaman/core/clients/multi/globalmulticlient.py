
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
            for each in result.response:
                if each["hash"] not in deduped_results:
                    deduped_results[each["hash"]] = each
                    yield {"id": each["id"], "name": each["name"], "hash": each["hash"]}

    def has(self, root, file_id):
        result = list(gen_first_valid(methods.has(self.clients, root, file_id)))
        return result[0] if result else False

    def search_by_name(self, file_name):
        results = gen_all(methods.search_by_name(self.clients, file_name))
        deduped_results = set()  # (name, hash)
        for result in results:
            for each in result.response:
                key = (each["name"], each["hash"])
                if key not in deduped_results:
                    yield each
                    deduped_results.add(key)

    def fuzzy_search_by_name(self, file_name):
        results = gen_all(methods.fuzzy_search_by_name(self.clients, file_name))
        deduped_results = set()  # (name, hash)
        for result in results:
            for each in result.response:
                key = (each["name"], each["hash"])
                if key not in deduped_results:
                    yield each
                    deduped_results.add(key)

    def upload(self, file_path):
        raise NotImplementedError()  # This has to be controlled by policy

    def download(self, file_path):
        raise NotImplementedError()  # This has to be controlled by policy

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
