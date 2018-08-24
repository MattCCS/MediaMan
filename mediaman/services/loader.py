
from mediaman.core import hashenum
from mediaman.services.drive import service as driveservice
from mediaman.services.local import service as localservice


def load(name):
    if name == "local":
        return load_local()
    elif name == "drive":
        return load_drive()
    else:
        raise NotImplementedError()


def prepare(service):
    assert service.hash_function() in hashenum.HashFunctions
    service.authenticate()
    return service


def load_drive():
    return prepare(driveservice.DriveService())


def load_local():
    return prepare(localservice.LocalService())
