
from mediaman.core import multimethods


class Multiclient:

    def __init__(self, clients):
        self.clients = clients

    # def get_file_by_hash(self, file_hash):
    #     return self.index_manager.get_file_by_hash(file_hash)

    def list_files(self):
        return multimethods.list_files(self.clients)

    def list_file(self, file_id):
        raise NotImplementedError()

    # def has_by_uuid(self, identifier):
    #     return self.index_manager.has_by_uuid(identifier)

    def search_by_name(self, file_name):
        return multimethods.search_by_name(self.clients, file_name)

    def exists(self, file_id):
        return multimethods.exists(self.clients, file_id)

    # def upload(self, file_path):
    #     return self.index_manager.upload(file_path)

    # def download(self, file_path):
    #     path = pathlib.Path(file_path)
    #     identifier = path.name
    #     return self.index_manager.download(identifier)
