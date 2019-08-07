
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
        deduped_results = set()
        for result in gen_all(methods.list_files(self.clients)):
            if result.response is None:
                logger.debug(f"Response is missing, can't parse result: {result}")
                continue

            for each in result.response:
                hashes = each["hashes"]
                if not set(hashes) & deduped_results:
                    yield {"id": each["id"], "name": each["name"], "hashes": hashes, "size": each["size"]}
                deduped_results.update(hashes)

    def has(self, request):
        hash = request.hash
        result = list(gen_first_valid(methods.has_hash(self.clients, hash)))
        return result[0] if result else False

    def search_by_name(self, file_name):
        results = gen_all(methods.search_by_name(self.clients, file_name))
        deduped_results = set()  # (name, hash)
        for result in results:
            for each in result.response:
                keys = set((each["name"], hash) for hash in each["hashes"])
                if not keys & deduped_results:
                    yield each
                deduped_results.update(keys)

    def fuzzy_search_by_name(self, file_name):
        results = gen_all(methods.fuzzy_search_by_name(self.clients, file_name))
        deduped_results = set()  # (name, hash)
        for result in results:
            for each in result.response:
                keys = set((each["name"], hash) for hash in each["hashes"])
                if not keys & deduped_results:
                    yield each
                deduped_results.update(keys)

    def upload(self, request):
        # TODO: make this better...
        # DO: check policy for storage/redundancy
        # MAYBE: check capacity? (is that a client/index concern?)

        hash = request.hash
        candidates = set()
        for (client, result) in zip(self.clients, gen_all(methods.has_hash(self.clients, hash))):
            if result.response:
                logger.info(f"MediaMan already has this file ('{request.path}').")
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
        if validation.is_valid_hash(identifier):
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

        def has_preferred_hash(file):
            return any(map(hashing.is_preferred_hash, file["hashes"]))

        def preferred_hash(file):
            for hash in file["hashes"]:
                if hashing.is_preferred_hash(hash):
                    return hash

        files_by_nickname = {rslt.client.nickname(): {preferred_hash(f): f for f in rslt.response if has_preferred_hash(f)} for rslt in list_files_results if rslt.response}
        capacity_by_nickname = {rslt.client.nickname(): rslt.response.available() for rslt in capacity_results if rslt.response}

        from mediaman.core.strategies import distribution
        bins = capacity_by_nickname
        items = {hash: f["size"] for fs in files_by_nickname.values() for (hash, f) in fs.items()}
        logger.debug(f"Bins: {bins}")
        logger.debug(f"Total unique items: {len(items)}")

        old_dist = {nickname: set() for nickname in bins}
        for (nickname, files) in files_by_nickname.items():
            old_dist[nickname] = set(hash for hash in files)
        new_dist = distribution.distribute(bins, items, distribution=old_dist)

        any_changes = False
        for nickname in old_dist:
            v1 = old_dist[nickname]
            v2 = new_dist[nickname]
            print(nickname, len(v1), len(v2))
            remove = (v1 - v2)
            add = (v2 - v1)
            if add or remove:
                any_changes = True
                print(f"changes to '{nickname}':\nadd: {add}\nremove: {remove}")
            else:
                print(f"No changes for '{nickname}'.")

        if not any_changes:
            print(f"No changes necessary, MediaMan is already synchronized.")
            return False

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

        return True

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
                    hash=hash)
                logger.debug(f"Upload request: {upload_request}")

                upload = client.upload(upload_request)
                logger.info(f"Uploaded: {upload}")

    def refresh(self):
        return self.refresh_global_hashes()

    def refresh_global_hashes(self):
        logger.info("Collecting file lists...")
        list_files_results = list(gen_all(methods.list_files(self.clients)))
        hashes_by_hash = {}

        for rslt in list_files_results:
            if rslt.response:
                for file in rslt.response:
                    hashes = set(file["hashes"])
                    group = set(hashes).union(*(hashes_by_hash.get(h, set()) for h in hashes))
                    for h in group:
                        hashes_by_hash[h] = group

        return list(gen_all(methods.refresh_global_hashes(self.clients, hashes_by_hash)))

    def remove(self, request):
        raise NotImplementedError()  # `mm remove` is not allowed
