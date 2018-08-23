

from mediaman.services.abstract import service


ERROR_MULTIPLE_REMOTE_INDICES = "\
[!] Multiple index files found for service ({})!  \
This must be resolved manually.  Exiting..."


class MapperMiddlewareService(service.AbstractService):

    INDEX_FILENAME = "index"

    def __init__(self, service):
        self.service = service

        self.metadata = {}
        self.id_to_metadata_map = {}
        self.hash_to_metadata_map = {}

    def load_metadata(self):
        # TODO: implement
        files = self.service.search_by_name(MapperMiddlewareService.INDEX_FILENAME)
        if len(files) > 1:
            raise RuntimeError(ERROR_MULTIPLE_REMOTE_INDICES.format(self.service))

        raise NotImplementedError()

    def hash_function(self):
        return self.service.hash_function()

    def authenticate(self):
        self.service.authenticate()
        self.load_metadata()

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
