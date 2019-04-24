
import contextlib
import pathlib
import shutil
import tempfile

from mediaman import config
from mediaman.core import hashing
from mediaman.core import logtools
from mediaman.core import models
from mediaman.core import validation
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


def sort_by_resolution_order(names, resolution_order):
    temp_names = {name: name for name in names}
    return [
        temp_names.pop(name)
        for name in resolution_order
        if name in temp_names
    ] + list(temp_names)


@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


class GlobalMulticlient(abstract.AbstractMulticlient):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resolution_order = config.load(RESOLUTION_ORDER_KEY)
        self.sort_clients_by_resolution_order()

    def sort_clients_by_resolution_order(self):
        if not self._resolution_order:
            logger.warn(f"No '{RESOLUTION_ORDER_KEY}' key found in config file.")
            return

        logger.debug(f"'{RESOLUTION_ORDER_KEY}' key found: {self._resolution_order}")

        temp_clients = {c.nickname(): c for c in self.clients}
        sorted_names = sort_by_resolution_order(temp_clients.keys(), self._resolution_order)
        self.clients = [temp_clients[name] for name in sorted_names]

    def list_files(self):
        deduped_results = {}
        for result in gen_all(methods.list_files(self.clients)):
            for each in result.response:
                if each["hash"] not in deduped_results:
                    deduped_results[each["hash"]] = each
                    yield {"id": each["id"], "name": each["name"], "hash": each["hash"], "size": each["size"]}

    def has(self, request):
        hash = request.hash
        result = list(gen_first_valid(methods.has_hash(self.clients, hash)))
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

    def upload(self, request):
        # TODO: make this better...
        # DO: check policy for storage/redundancy
        # MAYBE: check capacity? (is that a client/index concern?)

        hash = request.hash
        candidates = set()
        for (client, result) in zip(self.clients, gen_all(methods.has_hash(self.clients, hash))):
            if result.response:
                logger.info("MediaMan already has this file.")
                return False
            elif result.response is False:
                candidates.add(client)

        if not candidates:
            logger.error("MediaMan doesn't have the file, but also can't upload it at this time!")
            raise RuntimeError()

        client = list(candidates)[0]
        return client.upload(request)

    def download(self, root, identifier):
        # TODO: make some sort of identifier Enum
        # (hash, uuid, name, row #, ...)
        if validation.is_valid_sha256(identifier):
            func = methods.has_hash
        elif validation.is_valid_uuid(identifier):
            func = methods.has_uuid
        else:
            # BUG: when checking by name, need to see if duplicates exist!
            func = methods.has_name

        for (client, result) in zip(self.clients, gen_all(func(self.clients, identifier))):
            if result.response:
                return client.download(root, identifier)

        logger.error(f"MediaMan doesn't have '{identifier}'.")
        return None

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
        logger.info("Collecting file lists and capacities...")
        list_files_results = list(gen_all(methods.list_files(self.clients)))
        capacity_results = list(gen_all(methods.capacity(self.clients)))

        files_by_nickname = {rslt.client.nickname(): {f["hash"]: f for f in rslt.response} for rslt in list_files_results if rslt.response}
        capacity_by_nickname = {rslt.client.nickname(): rslt.response.allowed() for rslt in capacity_results if rslt.response}

        from mediaman.core.strategies import distribution
        bins = capacity_by_nickname
        items = {f["hash"]: f["size"] for fs in files_by_nickname.values() for f in fs.values()}
        print(len(items))

        old_dist = {nickname: set(hash for hash in files) for (nickname, files) in files_by_nickname.items()}
        new_dist = distribution.distribute(bins, items, distribution=old_dist)

        for nickname in old_dist:
            v1 = old_dist[nickname]
            v2 = new_dist[nickname]
            remove = (v1 - v2)
            add = (v2 - v1)
            print(f"changes to '{nickname}':\nadd: {add}\nremove: {remove}")

        inp = input("Would you like to proceed? [Y/n] ")
        if inp != "Y":
            print("Cancelling sync.")
            return None

        clients = {c.nickname(): c for c in self.clients}

        for nickname in old_dist:
            client = clients[nickname]
            v1 = old_dist[nickname]
            v2 = new_dist[nickname]
            remove = (v1 - v2)
            add = (v2 - v1)
            self.sync_changes(client, remove, add)

    def sync_changes(self, client, remove, add):
        logger.info(f"Syncing '{client.nickname()}'...")

        # TODO: implement removing
        if remove:
            logger.error("Removing during sync is not implemented yet!")

        if not add:
            logger.info("Nothing to add.")
            return

        for hash in add:
            with make_temp_directory() as temp_dir:
                root = pathlib.Path(temp_dir)
                logger.info(f"Downloading '{hash}' to '{root}' ...")
                download_receipt = self.download(root, hash)
                logger.debug(f"Download receipt: {download_receipt}")

                upload_request = models.Request(
                    id=None,
                    path=download_receipt.path(),
                    hash=hashing.hash(download_receipt.path()))
                logger.debug(f"Upload request: {upload_request}")

                upload = client.upload(upload_request)
                logger.info(f"Uploaded: {upload}")

    def refresh(self):
        raise NotImplementedError()  # `mm refresh` not implemented yet
