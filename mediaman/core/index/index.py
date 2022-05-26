
import contextlib
import functools
import json
import os
import pathlib
import shutil
import tempfile
import typing
import uuid

from mediaman.core import hashing
from mediaman.core import logtools
from mediaman.core import models
from mediaman.core import settings
from mediaman.core.index import base
from mediaman.core.index import migration

logger = logtools.new_logger(__name__)


ERROR_MULTIPLE_REMOTE_FILES = "\
[!] Multiple {} files found for service ({})!  \
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


def create_file(id, name, sid, size, hashes, tags):
    assert isinstance(size, int)
    assert isinstance(hashes, list)
    assert isinstance(tags, list)
    return {
        "id": id,
        "name": name,
        "sid": sid,
        "size": size,
        "hashes": hashes,
        "tags": tags,
        "encryption": {"cipher": "aes-256-cbc", "digest": "sha256"},
    }


def create_metadata():
    return {
        "version": settings.VERSION,
        "data": {
            "indices": [],
        },
    }


def get_one_file_by_name(service, filename) -> typing.Optional[dict]:
    logger.debug(f"Searching {service} for file with name {repr(filename)} ...")
    file_list = service.search_by_name(filename)
    files = file_list.results()

    logger.trace(f"files = {files}")
    logger.trace(f"file_list = {file_list}")
    if len(files) > 1:
        raise RuntimeError(ERROR_MULTIPLE_REMOTE_FILES.format(repr(filename), self.service))

    return files[0] if files else None


def temporary(bytez):
    tempfile_ref = tempfile.NamedTemporaryFile("w+", delete=True)
    tempfile_ref.write(bytez)
    tempfile_ref.seek(0)
    return tempfile_ref


class Index(base.BaseIndex):

    MLIST_FILENAME = "mlist"
    INDEX_PREFIX = "index"

    def __init__(self, service):
        super().__init__(service)
        logger.debug(f"Index init for {service}")

        self.index_id = None
        self.latest_file_index = 0  # used as "foreign key" for metadata tables
        self.metadata = {}  # {str(int) -> file_metadata}
        self.id_to_metadata_map = {}  # {id/UUID -> str(int)}
        self.hash_to_metadata_map = {}  # {hash -> str(int)}

    def _downloaded(self, file_sid, encryption):
        logger.debug(f"Downloading file with sid {file_sid}")
        tempfile_ref = tempfile.NamedTemporaryFile("w+", delete=True)
        request = models.Request(
            id=file_sid,
            path=tempfile_ref.name,
        )
        self.service.download(request, encryption=encryption)
        tempfile_ref.seek(0)
        return tempfile_ref

    def _resolve_identifier_to_file_metadata(self, identifier) -> typing.Union[None, typing.Literal[False], dict]:
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
        return metadata

    def files(self):
        return self.metadata["files"]

    def force_init(self):
        self.init_metadata()

    def init_metadata(self):
        if self.index_id is not None:
            return

        mlist_file = get_one_file_by_name(self.service, Index.MLIST_FILENAME)

        if not mlist_file:
            logger.debug(f"Creating metadata")
            self.metadata = create_metadata()
            self.update_metadata()
        else:
            logger.debug(f"Loading metadata")
            self.load_metadata(mlist_file)

    def update_metadata(self):
        with temporary(json.dumps(self.metadata)) as tempfile_ref:
            request = models.Request(
                id=Index.INDEX_FILENAME,
                path=tempfile_ref.name,
            )
            receipt = self.service.upload(request)

        logger.debug(f"update_metadata receipt: {receipt}")
        self.index_id = receipt.id()

    def load_metadata_json(self, mlist_file):
        logger.debug(f"load_metadata_json index: {mlist_file}")
        self.index_id = mlist_file.id()

        # NOTE: mlist file is never encrypted
        with self._downloaded(self.index_id, encryption=None) as tempfile_ref:
            return json.loads(tempfile_ref.read())

    def load_metadata(self, mlist_file):
        logger.trace(f"Loading metadata: {mlist_file}")
        mlist_data = self.load_metadata_json(mlist_file)
        logger.trace(f"Loaded mlist_data: {mlist_data}")

        if "version" not in mlist_data:
            logger.critical(f"Problem reading metadata for index {self}: 'version' field missing from metadata!  This is an outdated or unversioned `mlist` file.  You will need to fix it by running `mm <service> refresh`.")
            raise RuntimeError("Unversioned metadata")

        version = mlist_data["version"]
        if version > settings.VERSION:
            logger.critical(f"Problem reading metadata for index {self}: Metadata version ({version}) exceeds software version ({settings.VERSION}).  You need to update your software to parse this `mlist` file.")
            raise RuntimeError("Outdated software")

        if version < settings.VERSION:
            logger.critical(f"Problem reading metadata for index {self}: Metadata version ({version}) is below software version ({settings.VERSION}).  You need to update it by running `mm <service> refresh`.")
            raise RuntimeError("Outdated metadata")

        # Download and cache multiple indices
        self.metadata = {"files": {}}
        for index_envelope in mlist_data["data"]["indices"]:
            index_sid = index_envelope["sid"]
            index_encryption = index_envelope["encryption"]
            with self._downloaded(index_sid, encryption=index_encryption) as tempfile_ref:
                index_data = json.loads(tempfile_ref.read())
                self._load_index_data(index_data)

        logger.trace(f"Metadata loaded: {self.metadata}")

    def _load_index_data(self, index_data):
        logger.trace(f"Loading {index_data=}")
        files = index_data["files"]
        for f in files:
            file_index = str(self.latest_file_index)

            self.metadata["files"][file_index] = f
            self.id_to_metadata_map[f["id"]] = file_index
            self.hash_to_metadata_map.update(**{hash: file_index for hash in f["hashes"]})

            self.latest_file_index += 1
            # self.id_to_metadata_map.update(**{f["id"]: f for f in files})
            # self.hash_to_metadata_map.update(**{hash: f for f in files for hash in f["hashes"]})

    @init
    def new_id(self):
        id = str(uuid.uuid4())
        while id in self.id_to_metadata_map:
            id = str(uuid.uuid4())
        return id

    @init
    def get_metadata_by_hash(self, hash):
        index = self.hash_to_metadata_map.get(hash, None)
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
        return [f for f in self.files().values() if hash in f["hashes"]]

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

        self.track_file(create_file(
            id=upload_request.id,
            name=name,
            sid=receipt.id(),
            size=size,
            hashes=hashes,
            tags=[],
        ))

        return self.get_metadata_by_hash(hash)

    @init
    def track_file(self, file):
        new_index = str(max(map(int, self.files()), default=-1) + 1)
        logger.trace(f"Tracking file {file} with index {new_index}")

        self.files()[new_index] = file
        self.id_to_metadata_map[file["id"]] = new_index
        for hash in file["hashes"]:
            self.hash_to_metadata_map[hash] = new_index

        self.update_metadata()

    @init
    def download(self, root, identifier):
        logger.debug(f"Download request for: '{identifier}' to '{root}'...")
        if not (metadata := self._resolve_identifier_to_file_metadata(identifier)):
            return metadata

        logger.trace(f"Downloading file with metadata: {metadata}")
        encryption = metadata["encryption"]
        request = models.Request(
            id=metadata["sid"],
            path=root / metadata["name"],
        )
        return self.service.download(request, encryption=encryption)

    @init
    def stream(self, root, identifier):
        logger.debug(f"Stream request for: '{identifier}' to '{root}'...")
        if not (metadata := self._resolve_identifier_to_file_metadata(identifier)):
            return metadata

        encryption = metadata["encryption"]
        request = models.Request(
            id=metadata["sid"],
            path=root / metadata["name"],
        )
        return self.service.stream(request, encryption=encryption)

    @init
    def stream_range(self, root, identifier, offset, length):
        logger.debug(f"Stream request for: '{identifier}' to '{root}'...")
        if not (metadata := self._resolve_identifier_to_file_metadata(identifier)):
            return metadata

        encryption = metadata["encryption"]
        request = models.Request(
            id=metadata["sid"],
            path=root / metadata["name"],
        )
        return self.service.stream_range(request, offset, length, encryption=encryption)

    def refresh(self):
        raise NotImplementedError()
        raw_metadata = self.load_metadata_json(self.service.search_by_name("...").results()[0])
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
        raise NotImplementedError()
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

            new_file = create_file(
                id=id,
                name=name,
                sid=sid,
                size=size,
                hashes=hashes,
                tags=[],
            )
            new_files.append(new_file)
            logger.debug(new_file)

        new_metadata_files = {str(i): v for (i, v) in dict(enumerate(new_files)).items()}
        raise NotImplementedError()
        new_metadata = create_metadata(files=new_metadata_files)  # TODO: <---
        logger.info(f"New metadata: {new_metadata}")

        inp = input("Does everything look good? [Y/n] ")
        if inp not in ('y', 'Y'):
            print("Cancelled.")
            return

        self.metadata = new_metadata
        self.update_metadata()

    # def refresh_hashes(self):
    #     preferred_hash = hashing.PREFERRED_HASH.value

    #     for file in self.files().values():

    #         # TODO: make a helper for this
    #         hash_prefixes = set(hash.split(":")[0] for hash in file["hashes"])
    #         if preferred_hash in hash_prefixes:
    #             logger.info(f"Preferred hash already present for: {file}")
    #             continue

    #         with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
    #             path = tempfile_ref.name
    #             request = models.Request(
    #                 id=file["sid"],
    #                 path=path,
    #             )

    #             self.service.download(request)
    #             tempfile_ref.seek(0)

    #             hash = hashing.hash(path)
    #             logger.debug(f"Hash of {file}: {hash}")

    #             file["hashes"].append(hash)
    #             self.update_metadata()
    #             logger.info(f"Updated hash for: {file}")

    def refresh_global_hashes(self, hashes_by_hash):
        raise NotImplementedError()
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
        # TODO: delete file from CORRECT INDEX FILE (need to track that somewhere)
        # TODO: remove index file if not needed anymore!
        raise NotImplementedError()
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
        raise NotImplementedError()
        if not requests:
            return self.files()

        requests = list(requests)
        logger.debug(f"Applying tags add={add}, remove={remove}, set={set} to files {requests}")

        updated_files = []
        for request in requests:
            try:
                file = self.files()[self.hash_to_metadata_map[request.hash]]
            except KeyError:
                logger.error(f"No such file found ({request}) in Index {self}!")
                continue

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

    def migrate_to_v2(self):
        raise NotImplementedError()
        # logger.debug("Running `migrate_to_v2`")
        # try:
        #     mlist_file = self.service.search_by_name("mlist").results()[0]
        #     raise RuntimeError("`mlist` file already exists.")
        # except IndexError:
        #     pass

        # current_files = self.service.list_files().results()
        # index_file = self.service.search_by_name("index").results()[0]
        # crypt_file = self.service.search_by_name("crypt").results()[0]

        # index_file_sid = index_file.id()
        # crypt_file_sid = crypt_file.id()

        # with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
        #     request = models.Request(
        #         id=index_file_sid,
        #         path=tempfile_ref.name,
        #     )

        #     self.service.download(request)
        #     tempfile_ref.seek(0)

        #     index_data = json.loads(tempfile_ref.read())

        # with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
        #     request = models.Request(
        #         id=crypt_file_sid,
        #         path=tempfile_ref.name,
        #     )

        #     self.service.download(request)
        #     tempfile_ref.seek(0)

        #     crypt_data = json.loads(tempfile_ref.read())

        # file_sids = set(f.id() for f in current_files)
        # data_file_sids = file_sids - set([index_file_sid, crypt_file_sid])
        # assert len(data_file_sids) == (len(file_sids) - 2)

        # crypt_sids = set(crypt_data["data"])
        # index_sids = set(f["sid"] for f in index_data["files"].values())
        # index_sid_map = {f["sid"]: f for f in index_data["files"].values()}

        # files_that_exist_and_are_tracked = data_file_sids & index_sids

        # new_entries = []
        # for tracked_sid in files_that_exist_and_are_tracked:
        #     new_entry = dict(index_sid_map[tracked_sid])
        #     new_entry["hashes"] = list(set(new_entry["hashes"] + new_entry.pop("merged_hashes")))
        #     new_entry["encryption"] = crypt_data["data"].get(tracked_sid)  # or None, if not encrypted

        #     new_entries.append(new_entry)

        # files = new_entries

        # def chunks(lst, n):
        #     """Yield successive n-sized chunks from lst."""
        #     for i in range(0, len(lst), n):
        #         yield lst[i:i + n]

        # new_index_file_lists = list(chunks(files, 250))
        # new_indices = [
        #     {
        #         "version": 5,
        #         "files": nifl,
        #     }
        #     for nifl in new_index_file_lists
        # ]

        # new_indices_tracked = []
        # for new_index in new_indices:
        #     with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
        #         tempfile_ref.write(json.dumps(new_index))
        #         tempfile_ref.seek(0)

        #         new_index_id = f"{Index.INDEX_PREFIX}-{uuid.uuid4()}"
        #         request = models.Request(
        #             id=new_index_id,
        #             path=tempfile_ref.name,
        #         )
        #         print(request)
        #         receipt = self.service.upload(request)
        #         new_index_tracked = {
        #             "id": new_index_id,
        #             "sid": receipt.id(),
        #             "encryption": {"cipher": "aes-256-cbc", "digest": "sha256"},
        #         }
        #         new_indices_tracked.append(new_index_tracked)

        # mlist = {
        #     "version": 5,
        #     "data": {
        #         "indices": new_indices_tracked,
        #     }
        # }

        # with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
        #     tempfile_ref.write(json.dumps(mlist))
        #     tempfile_ref.seek(0)

        #     MLIST_FILENAME = "mlist"
        #     request = models.Request(
        #         id=MLIST_FILENAME,
        #         path=tempfile_ref.name,
        #     )
        #     print(request)
        #     receipt = self.service.service.upload(request)  # TODO: specifically avoid encrypting

        # MLIST_x = {
        #     "version": 5,
        #     "data": {
        #         "indices": [
        #             {
        #                 "id": "index-7397c657-902e-4e39-989b-d856e67319eb",
        #                 "sid": "Ahi1bkjxiu1-9df81ghu13",
        #             }
        #         ],
        #     },
        # }

        # # ex:
        # MLIST_e = {
        #     "version": 5,
        #     "encryption": {"cipher": "aes-256-cbc", "digest": "sha256", "key-sig": "sha256:8a74dbc738563fe2..."},
        #     "data": "dGVzdCB...kYXRhMTI=",
        # }

        # MLIST = {
        #     "version": 5,
        #     "encryption": None,
        #     "data": {
        #         "indices": [
        #             {
        #                 "id": "index-7397c657-902e-4e39-989b-d856e67319eb",
        #                 "sid": "Ahi1bkjxiu1-9df81ghu13",
        #                 "encryption": {
        #                     "cipher": "aes-256-cbc",
        #                     "digest": "sha256", "key-sig": "sha256:8a74dbc738563fe2...",
        #                 },
        #                 "compression": True,
        #             },
        #             {"id": "index-2f396176-ffa6-4883-b779-85d77366a750", "sid": "sg9aua0fd8oij1df38g187", "encryption": {"cipher": "aes-256-cbc", "digest": "sha256", "key-sig": "sha256:8a74dbc738563fe2..."}},
        #             {"id": "index-f1330256-040c-4852-bbf7-5f5565ec2294", "sid": "afdy1aa39dfhsf8ghdgasf", "encryption": {"cipher": "aes-256-cbc", "digest": "sha256", "key-sig": "sha256:8a74dbc738563fe2..."}},
        #         ],
        #     },
        # }

        # INDEX_7397 = {
        #     "version": 5,
        #     "files": [
        #         {
        #             "public": {
        #                 "id": "75c9a08d-6c76-4123-9a7f-7c5cd1232ceb",
        #                 "sid": "1xrPgeCEl7ncyJv1TLdRIHiqyacfNoWN1",
        #                 "encryption": {"cipher": "aes-256-cbc", "digest": "sha256"},
        #             },
        #             "private": {
        #                 "name": "Everybody Rise.mp3",
        #                 "size": 691493,
        #                 "hashes": ["xxh64:ed496289a15cd4cf"],
        #                 "tags": [],
        #             },
        #         },
        #         {
        #             "id": "75c9a08d-6c76-4123-9a7f-7c5cd1232ceb",
        #             "name": "Everybody Rise.mp3",
        #             "sid": "1xrPgeCE7ncyJv1TLdRIHiqyacfNoWN1",
        #             "size": 691493,
        #             "hashes": ["xxh64:ed496289a15cd4ce"],
        #             "tags": [],
        #             "encryption": {"cipher": "aes-256-cbc", "digest": "sha256"},
        #         },
        #     ],
        # }
