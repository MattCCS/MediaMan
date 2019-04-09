
import enum

__all__ = [
    "load"
]


LOCAL_DESCRIPTION = """\
[local] -- Allows you to back up files to a network share, external drive,
or even a directory on your local drive (if that's what you're into).
Configurable in the config.yaml file."""

DRIVE_DESCRIPTION = """\
[drive] -- Allows you to back up files to Google Drive (requires Drive credentials).
Can even back up to a specific folder within Google Drive.
Configurable in the config.yaml file."""

ALL_DESCRIPTION = """\
[all] -- Allows you to back up files to all configured services at once.
Will also report information about all configured services."""


def load_local(config):
    from mediaman.services.local import service as localservice
    return localservice.LocalService(config)


def load_drive(config):
    from mediaman.services.drive import service as driveservice
    return driveservice.DriveService(config)


class ServiceType(enum.Enum):
    FOLDER = "folder"
    GOOGLE_DRIVE = "google drive"
    DROPBOX = "dropbox"
    AWS_S3 = "aws s3"
    AWS_GLACIER = "aws glacier"


SERVICE_TYPE_TO_LOADER = {
    ServiceType.FOLDER: load_local,
    ServiceType.GOOGLE_DRIVE: load_drive,
    ServiceType.DROPBOX: None,
    ServiceType.AWS_S3: None,
    ServiceType.AWS_GLACIER: None,
}

SERVICE_TYPE_TO_DESCRIPTION = {
    ServiceType.FOLDER: LOCAL_DESCRIPTION,
    ServiceType.GOOGLE_DRIVE: DRIVE_DESCRIPTION,
    ServiceType.DROPBOX: "(no description yet)",
    ServiceType.AWS_S3: "(no description yet)",
    ServiceType.AWS_GLACIER: "(no description yet)",
}


def load(service_type: ServiceType, config):
    return SERVICE_TYPE_TO_LOADER[service_type](config)


def load_description(service_type):
    if service_type == "all":
        return ALL_DESCRIPTION
    return SERVICE_TYPE_TO_DESCRIPTION[ServiceType(service_type)]
