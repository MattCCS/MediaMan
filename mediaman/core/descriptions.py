
from mediaman.services.loader import ServiceType


ALL_DESCRIPTION = """\
-- Allows you to back up files to all configured services at once.
Will also report information about all configured services."""

LOCAL_DESCRIPTION = f"""\
[{ServiceType.FOLDER.value}] -- Allows you to back up files to a network share, external drive,
or even a directory on your local drive (if that's what you're into).
Configurable in the config.yaml file."""

DRIVE_DESCRIPTION = f"""\
[{ServiceType.GOOGLE_DRIVE.value}] -- Allows you to back up files to Google Drive (requires Drive credentials).
Can even back up to a specific folder within Google Drive.
Configurable in the config.yaml file."""

DROPBOX_DESCRIPTION = f"""\
[{ServiceType.DROPBOX.value}] -- Allows you to back up files to Dropbox.
Can even back up to a specific folder within Dropbox.
Configurable in the config.yaml file."""

AWS_S3_DESCRIPTION = f"""\
[{ServiceType.AWS_S3.value}] -- Allows you to back up files to AWS S3 (requires AWS credentials).
It is recommended that you set "cost: true" in the config for any AWS service.
Configurable in the config.yaml file."""

AWS_GLACIER_DESCRIPTION = f"""\
[{ServiceType.AWS_GLACIER.value}] -- Allows you to back up files to AWS Glacier (requires AWS credentials).
It is recommended that you set "cost: true" in the config for any AWS service.
Configurable in the config.yaml file."""

HETZNER_STORAGE_BOX_DESCRIPTION = f"""\
[{ServiceType.HETZNER_STORAGE_BOX.value}] -- Allows you to back up files to a Hetzner Storage Box (requires SSH credentials).
Configurable in the config.yaml file."""


SERVICE_TYPE_TO_DESCRIPTION = {
    ServiceType.FOLDER: LOCAL_DESCRIPTION,
    ServiceType.GOOGLE_DRIVE: DRIVE_DESCRIPTION,
    ServiceType.DROPBOX: DROPBOX_DESCRIPTION,
    ServiceType.AWS_S3: AWS_S3_DESCRIPTION,
    ServiceType.AWS_GLACIER: AWS_GLACIER_DESCRIPTION,
    ServiceType.HETZNER_STORAGE_BOX: HETZNER_STORAGE_BOX_DESCRIPTION,
}
