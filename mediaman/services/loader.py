
import enum

__all__ = [
    "load"
]


def load_local(config):
    from mediaman.services.local import service as localservice
    return localservice.LocalService(config)


def load_drive(config):
    from mediaman.services.drive import service as driveservice
    return driveservice.DriveService(config)


def load_onedrive(config):
    from mediaman.services.onedrive import service as onedriveservice
    return onedriveservice.OneDriveService(config)


class ServiceType(enum.Enum):
    FOLDER = "folder"
    GOOGLE_DRIVE = "google drive"
    MICROSOFT_ONEDRIVE = "microsoft onedrive"
    DROPBOX = "dropbox"
    AWS_S3 = "aws s3"
    AWS_GLACIER = "aws glacier"


SERVICE_TYPE_TO_LOADER = {
    ServiceType.FOLDER: load_local,
    ServiceType.GOOGLE_DRIVE: load_drive,
    ServiceType.MICROSOFT_ONEDRIVE: load_onedrive,
}


def load(service_type: ServiceType, config):
    try:
        return SERVICE_TYPE_TO_LOADER[service_type](config)
    except KeyError as exc:
        print(f"No service loader configured for {service_type}!")
        raise
