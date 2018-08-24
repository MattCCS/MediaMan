
import json
import tempfile

from mediaman.core import models


ERROR_MULTIPLE_REMOTE_INDICES = "\
[!] Multiple index files found for service ({})!  \
This must be resolved manually.  Exiting..."


class Client:

    INDEX_FILENAME = "index"

    def __init__(self, service):
        self.service = service

        self.metadata = {}
        self.id_to_metadata_map = {}
        self.hash_to_metadata_map = {}

    def init_metadata(self):
        # TODO: implement
        file_list = self.service.search_by_name(Client.INDEX_FILENAME)
        files = file_list.results()

        if len(files) > 1:
            raise RuntimeError(ERROR_MULTIPLE_REMOTE_INDICES.format(self.service))

        if not files:
            self.update_metadata()
        else:
            self.load_metadata(files[0])

    def update_metadata(self):
        # TODO: actually calculate metadata to write
        with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
            tempfile_ref.write(json.dumps(self.metadata))
            tempfile_ref.seek(0)

            request = models.Request(id="index", path=tempfile_ref.name)
            self.service.upload(request)

    def load_metadata(self, index):
        # TODO: implement
        raise NotImplementedError()

    def authenticate(self):
        self.service.authenticate()
        self.init_metadata()

    def list_files(self):
        return self.service.list_files()

    def list_file(self, file_id):
        # TODO: implement
        raise NotImplementedError()
        return self.service.list_file(file_id)

    def search_by_name(self, file_name):
        # TODO: implement (do NOT convert for name search!)
        raise NotImplementedError()
        return self.service.search_by_name(file_name)

    def exists(self, file_id):
        # TODO: implement
        raise NotImplementedError()
        return self.service.exists(file_id)

    def upload(self, source_file_path, destination_file_path):
        # TODO: implement
        raise NotImplementedError()
        return self.service.upload(
            source_file_path,
            destination_file_path,
        )
