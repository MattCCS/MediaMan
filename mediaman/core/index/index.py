
import contextlib
import functools
import json
import os
import pathlib
import shutil
import tempfile
import uuid

from mediaman.core import hashing
from mediaman.core import logtools
from mediaman.core import models
from mediaman.core import settings
from mediaman.core.index import base
from mediaman.core.index import migration

logger = logtools.new_logger(__name__)


ERROR_MULTIPLE_REMOTE_INDICES = "\
[!] Multiple index files found for service ({})!  \
This must be resolved manually.  Exiting..."


def init(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        self.init_metadata()
        return func(self, *args, **kwargs)
    return wrapped


@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir)


def create_file(id, name, sid, size, hashes, merged_hashes, tags):
    assert isinstance(hashes, list)
    assert isinstance(merged_hashes, list)
    return {
        "id": id,
        "name": name,
        "sid": sid,
        "size": size,
        "hashes": hashes,
        "merged_hashes": merged_hashes,
        "tags": tags,
    }


def create_metadata(files=None):
    if files is None:
        files = {}

    return {
        "version": settings.VERSION,
        "files": files,
    }


class Index(base.BaseIndex):

    INDEX_FILENAME = "index"

    def __init__(self, service):
        super().__init__(service)
        logger.debug(f"Index init for {service}")

        self.index_id = None
        self.metadata = {}
        self.id_to_metadata_map = {}
        self.hash_to_metadata_map = {}
        self.merged_hash_to_metadata_map = {}

    def files(self):
        return self.metadata["files"]

    def force_init(self):
        self.init_metadata()

    def init_metadata(self):
        if self.index_id is not None:
            return

        # TODO: implement
        file_list = self.service.search_by_name(Index.INDEX_FILENAME)
        files = file_list.results()

        logger.debug(f"files = {files}")
        logger.debug(f"file_list = {file_list}")
        if len(files) > 1:
            raise RuntimeError(ERROR_MULTIPLE_REMOTE_INDICES.format(self.service))

        # new index file
        if not files:
            logger.debug(f"creating metadata")
            self.metadata = create_metadata()
            self.update_metadata()
        else:
            logger.debug(f"loading metadata")
            self.load_metadata(files[0])

    def update_metadata(self):
        with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
            tempfile_ref.write(json.dumps(self.metadata))
            tempfile_ref.seek(0)

            request = models.Request(
                id=Index.INDEX_FILENAME,
                path=tempfile_ref.name,
            )
            receipt = self.service.upload(request)

        logger.debug(f"update_metadata receipt: {receipt}")
        self.index_id = receipt.id()

    def load_metadata_json(self, index):
        logger.debug(f"load_metadata_json index: {index}")
        self.index_id = index.id()

        with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
            request = models.Request(
                id=self.index_id,
                path=tempfile_ref.name,
            )

            self.service.download(request)
            tempfile_ref.seek(0)

            return json.loads(tempfile_ref.read())

    def load_metadata(self, index):
        metadata = self.load_metadata_json(index)
        logger.debug(f"Loaded metadata: {metadata}")

        if "version" not in metadata:
            logger.critical(f"Problem reading metadata for index {self}: 'version' field missing from metadata!  This is an outdated or unversioned index file.  You will need to fix it by running `mm <service> refresh`.")
            raise RuntimeError("Unversioned metadata")

        version = metadata["version"]
        if version > settings.VERSION:
            logger.critical(f"Problem reading metadata for index {self}: Metadata version ({version}) exceeds software version ({settings.VERSION}).  You need to update your software to parse this index file.")
            raise RuntimeError("Outdated software")

        if version < settings.VERSION:
            logger.critical(f"Problem reading metadata for index {self}: Metadata version ({version}) is below software version ({settings.VERSION}).  You need to update it by running `mm <service> refresh`.")
            raise RuntimeError("Outdated metadata")

        self.metadata = metadata
        self.id_to_metadata_map = {v["id"]: k for (k, v) in self.files().items()}
        self.hash_to_metadata_map = {hash: k for (k, v) in self.files().items() for hash in v["hashes"]}
        self.merged_hash_to_metadata_map = {hash: k for (k, v) in self.files().items() for hash in v["merged_hashes"]}

    @init
    def new_id(self):
        id = str(uuid.uuid4())
        while id in self.id_to_metadata_map:
            id = str(uuid.uuid4())
        return id

    @init
    def get_metadata_by_hash(self, hash):
        index = self.hash_to_metadata_map.get(hash, self.merged_hash_to_metadata_map.get(hash, None))
        return self.files()[index]

    @init
    def get_metadata_by_uuid(self, uuid):
        return self.files()[self.id_to_metadata_map[uuid]]

    @init
    def list_files(self):
        return iter(self.files().values())

    @init
    def search_by_name(self, file_name):
        return [f for f in self.files().values() if f["name"] == file_name]

    @init
    def fuzzy_search_by_name(self, file_name):
        return [f for f in self.files().values() if file_name.lower() in f["name"].lower()]

    @init
    def search_by_hash(self, hash):
        return [f for f in self.files().values() if hash in f["hashes"] or hash in f["merged_hashes"]]

    @init
    def has_hash(self, hash):
        return hash in self.hash_to_metadata_map or hash in self.merged_hash_to_metadata_map

    @init
    def has_uuid(self, uuid):
        return uuid in self.id_to_metadata_map

    @init
    def has_name(self, name):
        return self.search_by_name(name)

    @init
    def upload(self, request):
        name = pathlib.Path(request.path).name
        size = os.stat(request.path).st_size
        hash = request.hash

        if self.has_hash(hash):
            logger.info(f"[-] (File already indexed: {request.path})")
            return self.get_metadata_by_hash(hash)

        upload_request = models.Request(
            id=self.new_id(),
            path=request.path,
        )

        logger.info(f"Uploading '{request}' as '{upload_request}' ...")
        receipt = self.service.upload(upload_request)

        hashes = [hash]
        merged_hashes = []

        self.track_file(create_file(
            id=upload_request.id,
            name=name,
            sid=receipt.id(),
            size=size,
            hashes=hashes,
            merged_hashes=merged_hashes,
            tags=[],
        ))

        return self.get_metadata_by_hash(hash)

    def merge_into_existing_file(self, request, exiting_file):
        existing_hash = exiting_file["hashes"][-1]
        new_hash = request.hash

        if new_hash in self.merged_hash_to_metadata_map:
            raise RuntimeError("Merged hash already present!")

        choices = {
            "1": exiting_file["name"],
            "2": pathlib.Path(request.path).name,
        }

        for (k, v) in choices.items():
            print(k, v)

        inp = input("If you want to merge these files, which name to keep? [1/2/n] ")
        if inp not in ('1', '2'):
            return False

        chosen_name = choices[inp]

        info = self.get_metadata_by_hash(existing_hash)
        logger.info(f"Old info: {info}")

        info["name"] = chosen_name
        info["merged_hashes"].append(new_hash)
        logger.info(f"New info: {self.get_metadata_by_hash(existing_hash)}")

        index = self.hash_to_metadata_map[existing_hash]
        self.merged_hash_to_metadata_map[new_hash] = index

        # inp = input("Look good? [Y/n] ")
        # if inp not in 'Yy':
        #     print("Cancelled.")
        #     exit(1)

        self.update_metadata()
        return True

    @init
    def track_file(self, file):
        new_index = str(max(map(int, self.files()), default=-1) + 1)
        logger.debug(file)
        self.files()[new_index] = file
        self.id_to_metadata_map[file["id"]] = new_index
        for hash in file["hashes"]:
            self.hash_to_metadata_map[hash] = new_index
        for hash in file["merged_hashes"]:
            self.merged_hash_to_metadata_map[hash] = new_index

        self.update_metadata()

    @init
    def download(self, root, identifier):
        logger.debug(f"Download request for: '{identifier}' to '{root}'...")

        if self.has_uuid(identifier):
            metadata = self.get_metadata_by_uuid(identifier)
        elif self.has_hash(identifier):
            metadata = self.get_metadata_by_hash(identifier)
        else:
            metadatas = self.search_by_name(identifier)
            if not metadatas:
                logger.error("[-] No such file found!")
                return None
            elif len(metadatas) > 1:
                logger.error("[-] Multiple files exist with that name!  Pass the hash or ID instead.")
                return False
            else:
                metadata = metadatas[0]

        request = models.Request(
            id=metadata["sid"],
            path=root / metadata["name"],
        )
        return self.service.download(request)

    @init
    def stream(self, root, identifier):
        logger.debug(f"Stream request for: '{identifier}' to '{root}'...")

        if self.has_uuid(identifier):
            metadata = self.get_metadata_by_uuid(identifier)
        elif self.has_hash(identifier):
            metadata = self.get_metadata_by_hash(identifier)
        else:
            metadatas = self.search_by_name(identifier)
            if not metadatas:
                logger.error("[-] No such file found!")
                return None
            elif len(metadatas) > 1:
                logger.error("[-] Multiple files exist with that name!  Pass the hash or ID instead.")
                return False
            else:
                metadata = metadatas[0]

        request = models.Request(
            id=metadata["sid"],
            path=root / metadata["name"],
        )
        return self.service.stream(request)

    @init
    def stream_range(self, root, identifier, offset, length):
        logger.debug(f"Stream request for: '{identifier}' to '{root}'...")

        if self.has_uuid(identifier):
            metadata = self.get_metadata_by_uuid(identifier)
        elif self.has_hash(identifier):
            metadata = self.get_metadata_by_hash(identifier)
        else:
            metadatas = self.search_by_name(identifier)
            if not metadatas:
                logger.error("[-] No such file found!")
                return None
            elif len(metadatas) > 1:
                logger.error("[-] Multiple files exist with that name!  Pass the hash or ID instead.")
                return False
            else:
                metadata = metadatas[0]

        request = models.Request(
            id=metadata["sid"],
            path=root / metadata["name"],
        )
        return self.service.stream_range(request, offset, length)

    def refresh(self):
        raw_metadata = self.load_metadata_json(self.service.search_by_name(Index.INDEX_FILENAME).results()[0])
        metadata = migration.repair_metadata(raw_metadata)

        print(f"Repaired metadata: {metadata}")
        inp = input("Does everything look good? [Y/n] ")
        if inp not in ('y', 'Y'):
            print("Cancelled.")
            return

        self.metadata = metadata
        self.update_metadata()

        inp = input("Would you like to refresh the file list? [Y/n] ")
        if inp in ('y', 'Y'):
            logger.info(f"Old metadata: {raw_metadata}")
            self.refresh_file_list(metadata)

        inp = input("Would you like to refresh the file hashes?  This may take a long time, but is useful when you have changed the preferred hash function. [Y/n]  ")
        if inp in ('y', 'Y'):
            self.refresh_hashes()

        return

    def refresh_file_list(self, metadata):
        sid_to_metadata = {f["sid"]: f for f in metadata["files"].values()}

        current_files = self.service.list_files().results()
        new_files = []
        for current_file in current_files:

            # NOTE: we're listing raw files!
            sid = current_file.id()
            id = current_file.name()
            size = current_file.size()
            logger.debug(f"current_file: {current_file}")

            try:
                file_metadata = sid_to_metadata[sid]
            except KeyError:
                # TODO: MUST HANDLE THIS!
                # This will occur for "index", but also for
                # new/lost files.  Have to track them sanely.
                logger.warn(f"Couldn't find metadata for sid '{sid}': {current_file}")
                continue

            name = file_metadata["name"]
            hashes = file_metadata["hashes"]
            merged_hashes = file_metadata["merged_hashes"]

            new_file = create_file(
                id=id,
                name=name,
                sid=sid,
                size=size,
                hashes=hashes,
                merged_hashes=merged_hashes,
                tags=[],
            )
            new_files.append(new_file)
            logger.debug(new_file)

        new_metadata_files = {str(i): v for (i, v) in dict(enumerate(new_files)).items()}
        new_metadata = create_metadata(files=new_metadata_files)
        logger.info(f"New metadata: {new_metadata}")

        inp = input("Does everything look good? [Y/n] ")
        if inp not in ('y', 'Y'):
            print("Cancelled.")
            return

        self.metadata = new_metadata
        self.update_metadata()

    def refresh_hashes(self):
        preferred_hash = hashing.PREFERRED_HASH.value

        for file in self.files().values():

            # TODO: make a helper for this
            hash_prefixes = set(hash.split(":")[0] for hash in file["hashes"])
            if preferred_hash in hash_prefixes:
                logger.info(f"Preferred hash already present for: {file}")
                continue

            with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
                path = tempfile_ref.name
                request = models.Request(
                    id=file["sid"],
                    path=path,
                )

                self.service.download(request)
                tempfile_ref.seek(0)

                hash = hashing.hash(path)
                logger.debug(f"Hash of {file}: {hash}")

                file["hashes"].append(hash)
                self.update_metadata()
                logger.info(f"Updated hash for: {file}")

    def refresh_global_hashes(self, hashes_by_hash):
        for (hash, hashes) in hashes_by_hash.items():
            if self.has_hash(hash):
                file = self.get_metadata_by_hash(hash)
                file["hashes"] = sorted(set(file["hashes"]) | hashes)

        # TODO: there's no context here, user doesn't
        # know which service they're approving changes for...
        print(f"Repaired hashes: {self.files()}")
        inp = input("Does everything look good? [Y/n] ")
        if inp not in 'yY':
            print("Cancelled.")
            return

        self.update_metadata()

    @init
    def remove(self, request):
        hash = request.hash
        if not self.has_hash(hash):
            logger.error(f"[-] No such file exists with that hash!")
            return None

        # NOTE: slightly lower-level than ideal...
        index = self.hash_to_metadata_map[hash]
        file = self.files()[index]
        id = file["id"]

        result = self.service.remove(file["sid"])
        logger.info(result)

        del self.hash_to_metadata_map[hash]
        del self.id_to_metadata_map[id]
        del self.files()[index]

        logger.debug(self.hash_to_metadata_map.keys())
        logger.debug(self.id_to_metadata_map.keys())
        logger.debug(self.files().keys())

        self.update_metadata()

        return result

    @init
    def tag(self, requests=None, add=None, remove=None, set=None):
        if not requests:
            return self.files()

        requests = list(requests)
        logger.debug(f"Applying tags add={add}, remove={remove}, set={set} to files {requests}")

        updated_files = []
        for request in requests:
            file = self.files()[self.hash_to_metadata_map[request.hash]]
            logger.trace(f"Tagging file {file}")
            logger.trace(f"Original tags: {file['tags']}")

            tags = frozenset(file["tags"])
            if add:
                tags |= frozenset(add)
            if remove:
                tags -= frozenset(remove)
            if set:
                tags = frozenset(set)  # I apologize...

            file["tags"] = list(sorted(tags))
            logger.trace(f"New tags: {file['tags']}")

            updated_files.append(file)

        # TODO: confirm with user before saving changes

        self.update_metadata()

        return updated_files
