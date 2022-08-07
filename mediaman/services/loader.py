
import enum

__all__ = [
    "load"
]


def load_local(config):
    from mediaman.services.local import service as localservice
    return localservice.LocalService(config)


def load_drive(config):
    # Apply monkey patches first
    from mediaman.patches.drive import patch_googleapiclient
    patch_googleapiclient.patch_googleapiclient_http()

    from mediaman.services.drive import service as driveservice
    return driveservice.DriveService(config)


def load_hetzner_storage_box(config):
    from mediaman.services.hetzner_storage_box import service as hetzner_storage_box_service
    return hetzner_storage_box_service.HetznerStorageBoxService(config)


class ServiceType(enum.Enum):
    FOLDER = "folder"
    GOOGLE_DRIVE = "google drive"
    DROPBOX = "dropbox"
    AWS_S3 = "aws s3"
    AWS_GLACIER = "aws glacier"
    HETZNER_STORAGE_BOX = "hetzner storage box"


SERVICE_TYPE_TO_LOADER = {
    ServiceType.FOLDER: load_local,
    ServiceType.GOOGLE_DRIVE: load_drive,
    ServiceType.HETZNER_STORAGE_BOX: load_hetzner_storage_box,
}


def load(service_type: ServiceType, config):
    try:
        return SERVICE_TYPE_TO_LOADER[service_type](config)
    except KeyError as exc:
        print(f"No service loader configured for {service_type}!")
        raise
