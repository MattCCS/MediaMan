
import enum

from mediaman import config
from mediaman.core import loader
from mediaman.services import loader as services_loader


__all__ = [
    "load_client",
]


class ServiceType(enum.Enum):
    FOLDER = "folder"
    GOOGLE_DRIVE = "google drive"
    DROPBOX = "dropbox"
    AWS_S3 = "aws s3"
    AWS_GLACIER = "aws glacier"


SERVICE_TYPE_TO_LOADER = {
    ServiceType.FOLDER: services_loader.load_local,
    ServiceType.GOOGLE_DRIVE: services_loader.load_drive,
    ServiceType.DROPBOX: None,
    ServiceType.AWS_S3: None,
    ServiceType.AWS_GLACIER: None,
}


POLICY = None


class Policy:

    def __init__(self):
        self.nickname_to_config = {}
        self.nickname_to_service = {}
        self.load_service_configs()

    def load_service_configs(self):
        services_config = config.load("services")
        for (nickname, service_config) in services_config.items():
            self.load_service_config(nickname, service_config)

    def load_service_config(self, nickname, service_config):
        # TODO: pass down quota/destination to each service (index)
        service_type = ServiceType(service_config["type"])
        config_data = {
            "type": service_type,
            "quota": config.parse_human_bytes(service_config["quota"]),
            "destination": service_config["destination"],
            "cost": service_config.get("cost", False),
        }
        print(config_data)
        self.nickname_to_config[nickname] = config_data

    def load_client(self, service_selector):
        raise NotImplementedError()


def ensure_policy():
    global POLICY
    if POLICY is None:
        POLICY = Policy()
    return POLICY


def load_client(service_selector):
    return ensure_policy().load_client(service_selector)
