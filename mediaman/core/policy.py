
from mediaman import config
from mediaman.core import loader
from mediaman.core import validation
from mediaman.services import loader as services_loader


__all__ = [
    "load_client",
    "load_service_names",
]

SERVICES_CONFIG_KEY = "services"
SERVICE_NICKNAME_ALL = "all"

ERROR_RESERVED_SERVICE_NICKNAME = """\
Error: `all` is a reserved service nickname!  You must modify
your config file to rename that service, otherwise other
MediaMan commands will not run!"""

POLICY = None


def load_service_names():
    config_services = config.load_safe(SERVICES_CONFIG_KEY)
    if SERVICE_NICKNAME_ALL in config_services:
        exit(ERROR_RESERVED_SERVICE_NICKNAME)
    return [SERVICE_NICKNAME_ALL] + list(config_services)


class Policy:

    def __init__(self):
        self.nickname_to_config = {}
        self.nickname_to_service = {}
        self.load_service_configs()

    def load_service_configs(self):
        services_config = config.load(SERVICES_CONFIG_KEY)
        for (nickname, service_config) in services_config.items():
            self.load_service_config(nickname, service_config)

    def load_service_config(self, nickname, service_config):
        service_type = services_loader.ServiceType(service_config["type"])
        config_data = {
            "type": service_type,
            "quota": validation.parse_human_bytes(service_config["quota"]),
            "destination": service_config["destination"],
            "cost": service_config.get("cost", False),
            "extra": service_config.get("extra", None),
        }
        self.nickname_to_config[nickname] = config_data

    def load_service(self, nickname):
        config = self.nickname_to_config[nickname]
        service_type = config["type"]
        service = services_loader.load(service_type, config)
        self.nickname_to_service[nickname] = service
        return service

    def load_all_services(self):
        for nickname in self.nickname_to_config:
            try:
                yield self.load_service(nickname)
            except Exception as exc:
                print(f"Failed to load service '{nickname}': {exc}")

    def load_client(self, service_selector):
        if service_selector is None:
            return loader.load_global_client(self.load_all_services())
        elif service_selector == "all":
            return loader.load_multi_client(self.load_all_services())
        else:
            service_name = service_selector
            return loader.load_single_client(self.load_service(service_name))

    def get_all_configs(self):
        return self.nickname_to_config

    def get_config(self, nickname):
        return self.nickname_to_config[nickname]

    def get_service_description(self, service_type):
        return services_loader.load_description(service_type)


def load_policy():
    global POLICY
    if POLICY is None:
        POLICY = Policy()
    return POLICY


def load_client(service_selector):
    return load_policy().load_client(service_selector)
