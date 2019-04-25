
import functools
import json
import os
import pathlib
import tempfile
import uuid

from mediaman.core import settings
from mediaman.core import logtools
from mediaman.core import models
from mediaman.core.index import base
from mediaman.core.index import migration

logger = logtools.new_logger("mediaman.core.index.index")


ERROR_MULTIPLE_REMOTE_INDICES = "\
[!] Multiple index files found for service ({})!  \
This must be resolved manually.  Exiting..."


def init(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        self.init_metadata()
        return func(self, *args, **kwargs)
    return wrapped


def create_file(id, name, sid, hash, size):
    return {
        "id": id,
        "name": name,
        "sid": sid,
        "hash": hash,
        "size": size,
    }


def create_metadata(files):
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

        if len(files) > 1:
            raise RuntimeError(ERROR_MULTIPLE_REMOTE_INDICES.format(self.service))

        if not files:
            self.update_metadata()
        else:
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
            logger.critical(f"'version' field missing from metadata!  This is an outdated or unversioned index file.  You will need to fix it by running `mm <service> refresh`.")
            raise RuntimeError("Unversioned metadata")

        version = metadata["version"]
        if version > settings.VERSION:
            logger.critical(f"Metadata version ({version}) exceeds software version ({settings.VERSION}).  You need to update your software to parse this index file.")
            raise RuntimeError("Outdated software")

        if version < settings.VERSION:
            logger.critical(f"Metadata version ({version}) is below software version ({settings.VERSION}).  You need to update it by running `mm <service> refresh`.")
            raise RuntimeError("Outdated metadata")

        self.metadata = metadata
        self.id_to_metadata_map = {v["id"]: k for (k, v) in self.files().items()}
        self.hash_to_metadata_map = {v["hash"]: k for (k, v) in self.files().items()}

    @init
    def new_id(self):
        id = str(uuid.uuid4())
        while id in self.id_to_metadata_map:
            id = str(uuid.uuid4())
        return id

    @init
    def get_metadata_by_hash(self, hash):
        return self.files()[self.hash_to_metadata_map[hash]]

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
    def has_hash(self, hash):
        return hash in self.hash_to_metadata_map

    @init
    def has_uuid(self, uuid):
        return uuid in self.id_to_metadata_map

    @init
    def has_name(self, name):
        return self.search_by_name(name)

    @init
    def upload(self, request):
        hash = request.hash
        if self.has_hash(hash):
            logger.info(f"    [*] (File already indexed: {request.path})")
            return self.get_metadata_by_hash(hash)

        request = models.Request(
            id=self.new_id(),
            path=request.path,
        )
        receipt = self.service.upload(request)

        self.track_file(create_file(
            request.id,
            pathlib.Path(request.path).name,
            receipt.id(),
            hash,
            os.stat(request.path).st_size,
        ))

        return self.get_metadata_by_hash(hash)

    @init
    def track_file(self, file):
        new_index = str(max(map(int, self.files()), default=-1) + 1)
        logger.debug(file)
        self.files()[new_index] = file
        self.id_to_metadata_map[file["id"]] = new_index
        self.hash_to_metadata_map[file["hash"]] = new_index

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

    def refresh(self):
        raw_metadata = self.load_metadata_json(self.service.search_by_name(Index.INDEX_FILENAME).results()[0])
        metadata = migration.repair_metadata(raw_metadata)

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
            hash = file_metadata["hash"]

            new_file = create_file(id, name, sid, hash, size)
            new_files.append(new_file)
            logger.debug(new_file)

        new_metadata_files = {str(i): v for (i, v) in dict(enumerate(new_files)).items()}
        new_metadata = create_metadata(new_metadata_files)
        logger.info(f"Old metadata: {raw_metadata}")
        logger.info(f"New metadata: {new_metadata}")

        self.metadata = new_metadata
        self.update_metadata()

    @init
    def remove(self, request):
        hash = request.hash
        if not self.has_hash(hash):
            logger.error(f"[-] No such file exists with that hash!")
            return None

        # NOTE: slightly lower-level than ideal...
        index = self.hash_to_metadata_map[hash]
        metadata = self.files()[index]
        id = metadata["id"]

        result = self.service.remove(metadata["sid"])
        logger.info(result)

        del self.hash_to_metadata_map[hash]
        del self.id_to_metadata_map[id]
        del self.files()[index]

        logger.debug(self.hash_to_metadata_map.keys())
        logger.debug(self.id_to_metadata_map.keys())
        logger.debug(self.files().keys())

        self.update_metadata()

        return result
