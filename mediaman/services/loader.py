
from mediaman.services.drive import drive


def prepare(service):
    service.authenticate()
    return service


def load_drive():
    return prepare(drive.DriveService())
