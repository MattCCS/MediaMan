
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

logger = logtools.new_logger(__name__)


def gen_first_valid(gen):
    try:
        result = next(gen)
        while True:
            if result.response:
                yield result
                gen.send(False)  # prompts a StopIteration from parent gen.
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


def has_preferred_hash(file):
    return any(map(hashing.is_preferred_hash, file["hashes"]))


def preferred_hash(file):
    for hash in file["hashes"]:
        if hashing.is_preferred_hash(hash):
            return hash


class GlobalMulticlient(abstract.AbstractMulticlient):
    """
    Class handling `mm ...` commands.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resolution_order = config.load(RESOLUTION_ORDER_KEY)
        self.sort_clients_by_resolution_order()

    def sort_clients_by_resolution_order(self):
        if not self._resolution_order:
            logger.warn(f"No '{RESOLUTION_ORDER_KEY}' key found in config file.")
            return

        logger.debug(f"'{RESOLUTION_ORDER_KEY}' key found: {self._resolution_order}")

        self.clients_by_nickname = {c.nickname(): c for c in self.clients}
        sorted_names = sort_by_resolution_order(self.clients_by_nickname.keys(), self._resolution_order)
        self.clients = [self.clients_by_nickname[name] for name in sorted_names]

    def list_files(self):
        deduped_results = set()
        for result in gen_all(methods.list_files(self.clients)):
            if result.response is None:
                logger.debug(f"Response is missing, can't parse result: {result}")
                continue

            for each in result.response:
                hashes = each["hashes"]
                if not set(hashes) & deduped_results:
                    value = {"id": each["id"], "name": each["name"], "hashes": hashes, "size": each["size"], "tags": "???"}
                    yield models.Response(client=result.client, response=[each], exception=None)
                deduped_results.update(hashes)

    def has(self, request):
        hash = request.hash
        return self.has_hash(request.hash)

    def search_by_name(self, file_name):
        results = gen_all(methods.search_by_name(self.clients, file_name))
        deduped_results = set()  # (name, hash)
        for result in results:
            for each in result.response:
                keys = set((each["name"], hash) for hash in each["hashes"])
                if not keys & deduped_results:
                    yield models.Response(client=result.client, response=[each], exception=None)
                deduped_results.update(keys)

    def fuzzy_search_by_name(self, file_name):
        results = gen_all(methods.fuzzy_search_by_name(self.clients, file_name))
        deduped_results = set()  # (name, hash)
        for result in results:
            for each in result.response:
                keys = set((each["name"], hash) for hash in each["hashes"])
                if not keys & deduped_results:
                    # yield each
                    yield models.Response(client=result.client, response=[each], exception=None)
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

    def stream(self, root, identifier):
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
                return client.stream(root, identifier)

        logger.error(f"MediaMan doesn't have '{identifier}'.")
        return None

    def stream_range(self, root, identifier, offset, length):
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
                return client.stream_range(root, identifier, offset, length)

        logger.error(f"MediaMan doesn't have '{identifier}'.")
        return None

    def stats(self):
        # TODO: don't double-count identical files!
        # TODO: method should return hashes instead.. but what about SHA vs. XXH?
        # NOTE: This is not trivial.
        raise NotImplementedError()
        results = gen_all(methods.stats(self.clients))
        grand_file_count = 0
        is_partial = False
        for result in results:
            if result.response:
                response = result.response
                grand_file_count += response["file_count"]
            else:
                is_partial = True
        return MultiResultQuota(grand_file_count, is_partial)

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

        yield models.Response(client=None,
            response=MultiResultQuota(
                used=grand_used,
                allowed=grand_allowed,
                total=grand_total,
                is_partial=is_partial),
            exception=None)

    def clone(self, target_services, hashes=None, source_services=None):
        logger.debug(f"clone({target_services=}, {hashes=}, {source_services=})")
        allowed_nicknames = set(self.clients_by_nickname)

        hashes = set(hashes or [])

        if not target_services:
            raise RuntimeError("Must pass at least one target service!")
        if not all(t in allowed_nicknames for t in target_services):
            raise RuntimeError(f"Must pass real target services, got {target_services}, expected subset of {allowed_nicknames}")

        source_services = source_services or []
        if not all(t in allowed_nicknames for t in source_services):
            raise RuntimeError(f"Must pass real source services, got {source_services}, expected subset of {allowed_nicknames}")

        logger.info("[clone] Determining which services to use...")
        # 1) Determine what services to use.
        # 1a) If we were told to source from specific services, only look at those.
        if source_services:
            clients_to_scan = [self.clients_by_nickname[c] for c in set(target_services) | set(source_services)]
        else:
            clients_to_scan = self.clients

        logger.info(f"[clone] Scanning services ({[c.nickname() for c in clients_to_scan]})...")
        # 2) Determine what these services have.
        list_files_results = list(gen_all(methods.list_files(clients_to_scan)))
        file_maps_by_client_nickname = {rslt.client.nickname(): {preferred_hash(f): f for f in rslt.response if has_preferred_hash(f)} for rslt in list_files_results if rslt.response}
        files_by_hash_with_best_client = {}

        # Map hashes to (hash, file, best client nickname) in files_by_hash_with_best_client.
        # (this is pre-sorted by preference)
        for client in self.clients:
            if (client_nickname := client.nickname()) in file_maps_by_client_nickname:
                for (hash, file) in file_maps_by_client_nickname[client_nickname].items():
                    if hashes and hash not in hashes:
                        continue

                    if hash not in files_by_hash_with_best_client:
                        files_by_hash_with_best_client[hash] = (hash, file, client_nickname)

        # print(list(files_by_hash_with_best_client.items())[:3])

        @contextlib.contextmanager
        def local_copy_of(hash, filename, from_service):
            with make_temp_directory() as temp_dir:
                root = pathlib.Path(temp_dir)
                logger.info(f"Downloading '{hash}' to '{root}' ...")

                client = self.clients_by_nickname[from_service]
                download_receipt = client.download(root, hash)
                logger.debug(f"Download receipt: {download_receipt}")
                # TODO(mcotton): Verify hash!

                local_filepath = root / filename
                yield local_filepath

        # 3) For each file that (at least one) target needs, get a local copy and distribute it.
        for (hash, file, client_nickname) in files_by_hash_with_best_client.values():
            if (every_target_has_file := all((hash in file_maps_by_client_nickname.get(t, {})) for t in target_services)):
                continue

            with local_copy_of(hash=hash, filename=file["name"], from_service=client_nickname) as local_filepath:
                for target_service in target_services:
                    if (service_has_file := (hash in file_maps_by_client_nickname.get(target_service, {}))):
                        continue

                    upload_request = models.Request(
                        id=None,
                        path=local_filepath,
                        hash=hash)
                    logger.debug(f"Upload request: {upload_request}")

                    inp = input(f"Syncing file at {local_filepath=} with {hash=} to {target_service=}.  File={file}.  Proceed? [Y/n] ")
                    if inp != "Y":
                        return

                    # TODO(mcotton): Need a high-level method for tags, etc. ...
                    client = self.clients_by_nickname[target_service]
                    upload = client.upload(upload_request)
                    logger.info(f"Uploaded: {upload}")

        if hashes and (remaining := (hashes - set(files_by_hash_with_best_client))):
            remaining_text = "".join(f"\n    {hash}" for hash in sorted(remaining))
            logger.warning(f"[x] Unable to locate the following requested hashes: {remaining_text}")

    # TODO(mcotton): Determine whether to salvage this method
    def sync(self):
        logger.info("Collecting file lists and capacities...")
        list_files_results = list(gen_all(methods.list_files(self.clients)))
        capacity_results = list(gen_all(methods.capacity(self.clients)))

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

    def search_by_hash(self, hash):
        results = gen_all(methods.search_by_hash(self.clients, hash))
        deduped_results = set()  # (name, hash)
        for result in results:
            for each in result.response:
                keys = set((each["name"], hash) for hash in each["hashes"])
                if not keys & deduped_results:
                    yield models.Response(client=result.client, response=[each], exception=None)
                deduped_results.update(keys)

    def has_hash(self, hash):
        for result in gen_all(methods.has_hash(self.clients, hash)):
            if result.response is True:
                yield result
                return

    def tag(self, *args, **kwargs):
        raise NotImplementedError()  # `mm tag` is not allowed (yet)

    def migrate_to_v2(self):
        raise NotImplementedError()  # `mm migrate_to_v2` is not allowed
