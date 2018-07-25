
from mediaman.core import hashenum
from mediaman.services.drive import drive


def prepare(service):
    assert service.hash_function() in hashenum.HashFunctions
    service.authenticate()
    return service


def load_drive():
    return prepare(drive.DriveService())
