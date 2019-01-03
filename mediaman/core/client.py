
import json
import pathlib
import tempfile
import uuid

from mediaman.core import hashing
from mediaman.core import models


ERROR_MULTIPLE_REMOTE_INDICES = "\
[!] Multiple index files found for service ({})!  \
This must be resolved manually.  Exiting..."


class IndexManager:

    INDEX_FILENAME = "index"

    def __init__(self, service):
        self.service = service

        self.index_id = None
        self.metadata = {}
        self.id_to_metadata_map = {}
        self.hash_to_metadata_map = {}

        self.init_metadata()

    def init_metadata(self):
        # TODO: implement
        file_list = self.service.search_by_name(IndexManager.INDEX_FILENAME)
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
                id=IndexManager.INDEX_FILENAME,
                path=tempfile_ref.name,
            )
            receipt = self.service.upload(request)

        self.index_id = receipt.id()

    def load_metadata(self, index):
        self.index_id = index.id()

        with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
            request = models.Request(
                id=self.index_id,
                path=tempfile_ref.name,
            )

            self.service.download(request)
            tempfile_ref.seek(0)

            self.metadata = json.loads(tempfile_ref.read())
            self.id_to_metadata_map = {v["id"]: k for (k, v) in self.metadata.items()}
            self.hash_to_metadata_map = {v["hash"]: k for (k, v) in self.metadata.items()}

        # print(self.metadata)

    def new_id(self):
        id = str(uuid.uuid4())
        while id in self.id_to_metadata_map:
            id = str(uuid.uuid4())
        return id

    def get_file_by_hash(self, file_hash):
        return self.metadata[self.hash_to_metadata_map[file_hash]]

    def list_files(self):
        return iter(self.metadata.values())

    def list_file(self, file_id):
        return self.metadata[self.id_to_metadata_map[file_id]]

    def search_by_name(self, file_name):
        return [f for f in self.metadata.values() if f["name"] == file_name]

    def exists(self, file_id):
        return file_id in self.id_to_metadata_map

    def upload(self, file_path):
        hash = hashing.hash(file_path)
        if hash in self.hash_to_metadata_map:
            print(f"    [*] (File already indexed: {file_path})")
            return self.get_file_by_hash(hash)

        request = models.Request(
            id=self.new_id(),
            path=file_path,
        )
        receipt = self.service.upload(request)

        self.track_file({
            "id": request.id,
            "name": pathlib.Path(request.path).name,
            "sid": receipt.id(),
            "hash": hash,
        })

    def track_file(self, file):
        new_index = str(max(map(int, self.metadata), default=-1) + 1)
        print(file)
        self.metadata[new_index] = file
        self.id_to_metadata_map[file["id"]] = new_index
        self.hash_to_metadata_map[file["hash"]] = new_index

        self.update_metadata()

    def download(self, identifier):
        print(identifier)

        if identifier in self.id_to_metadata_map:
            metadata = self.list_file(identifier)
            request = models.Request(
                id=metadata["sid"],
                path=metadata["name"],
            )
            return self.service.download(request)

        metadatas = self.search_by_name(identifier)
        if metadatas:
            metadata = metadatas[0]
            request = models.Request(
                id=metadata["sid"],
                path=metadata["name"],
            )
            return self.service.download(request)

        print("[-] No such file found!")


class Client:

    def __init__(self, service):
        self.service = service

        self.index_manager = IndexManager(self.service)

    def get_file_by_hash(self, file_hash):
        return self.index_manager.get_file_by_hash(file_hash)

    def list_files(self):
        return list(self.index_manager.list_files())

    def list_file(self, file_id):
        return self.index_manager.list_file(file_id)

    def has_by_uuid(self, identifier):
        return self.index_manager.has_by_uuid(identifier)

    def search_by_name(self, file_name):
        return list(self.index_manager.search_by_name(file_name))

    def exists(self, file_id):
        return self.index_manager.exists(file_id)

    def upload(self, file_path):
        return self.index_manager.upload(file_path)

    def download(self, file_path):
        path = pathlib.Path(file_path)
        identifier = path.name
        return self.index_manager.download(identifier)
