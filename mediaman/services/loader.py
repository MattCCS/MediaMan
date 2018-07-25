
from mediaman.core import hashenum
from mediaman.services.drive import service as driveservice
from mediaman.services.local import service as localservice


def prepare(service):
    assert service.hash_function() in hashenum.HashFunctions
    service.authenticate()
    return service


def load_drive():
    return prepare(driveservice.DriveService())


def load_local():
    return prepare(localservice.LocalService())
