
from mediaman import config
from mediaman.core import logtools
from mediaman.core.clients.multi import abstract
from mediaman.core.clients.multi import methods
from mediaman.core.models import MultiResultQuota

logger = logtools.new_logger("mediaman.core.clients.multi.globalmulticlient")


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


RESOLUTION_ORDER_KEY = "resolution-order"


class GlobalMulticlient(abstract.AbstractMulticlient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resolution_order = config.load(RESOLUTION_ORDER_KEY)
        self.sort_by_resolution_order()

    def sort_by_resolution_order(self):
        if not self._resolution_order:
            logger.warn(f"No '{RESOLUTION_ORDER_KEY}' key found in config file.")
            return

        logger.debug(f"'{RESOLUTION_ORDER_KEY}' key found: {self._resolution_order}")

        temp_clients = {c.nickname(): c for c in self.clients}
        self.clients = [
            temp_clients.pop(nn)
            for nn in self._resolution_order
            if nn in temp_clients
        ] + list(temp_clients.values())

    def list_files(self):
        deduped_results = {}
        for result in gen_all(methods.list_files(self.clients)):
            for each in result.response:
                if each["hash"] not in deduped_results:
                    deduped_results[each["hash"]] = each
                    yield {"id": each["id"], "name": each["name"], "hash": each["hash"], "size": each["size"]}

    def has(self, file_path):
        result = list(gen_first_valid(methods.has(self.clients, file_path)))
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

    def sync(self):
        print(self.clients[0])
        list_files_results = list(gen_all(methods.list_files(self.clients)))
        capacity_results = list(gen_all(methods.capacity(self.clients)))

        files_by_nickname = {rslt.client.nickname(): {f["hash"]: f for f in rslt.response} for rslt in list_files_results if rslt.response}
        capacity_by_nickname = {rslt.client.nickname(): rslt.response.allowed() for rslt in capacity_results if rslt.response}

        from mediaman.core.strategies import distribution
        bins = capacity_by_nickname
        items = {f["hash"]: f["size"] for fs in files_by_nickname.values() for f in fs.values()}
        print(len(items))

        dist = {nickname: set(hash for hash in files) for (nickname, files) in files_by_nickname.items()}
        new_dist = distribution.distribute(bins, items, distribution=dist)

        for nickname in dist:
            v1 = dist[nickname]
            v2 = new_dist[nickname]
            print(nickname, len(v1), len(v2), (v1 - v2), (v2 - v1))

        # import json
        # print(json.dumps({k: list(v) for (k, v) in dist.items()}, indent=4))
        # print(json.dumps({k: list(v) for (k, v) in new_dist.items()}, indent=4))

    def refresh(self):
        raise NotImplementedError()  # `mm refresh` not implemented yet
