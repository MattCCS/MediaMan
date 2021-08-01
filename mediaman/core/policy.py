
from mediaman import config
from mediaman.core import loader
from mediaman.core import logtools
from mediaman.core import validation
from mediaman.services import loader as services_loader

logger = logtools.new_logger("mediaman.core.policy")


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
        self.nickname_to_client = {}
        self.load_service_configs()

    def load_service_configs(self):
        services_config = config.load(SERVICES_CONFIG_KEY)
        for (nickname, service_config) in services_config.items():
            self.load_service_config(nickname, service_config)

    def load_service_config(self, nickname, service_config):
        service_type = services_loader.ServiceType(service_config["type"])
        config_data = {
            "nickname": nickname,
            "type": service_type,
            "quota": validation.parse_human_bytes(service_config["quota"]),
            "destination": service_config["destination"],
            "cost": service_config.get("cost", False),
            "extra": service_config.get("extra", None),
        }
        self.nickname_to_config[nickname] = config_data

    def load_service(self, nickname):
        if nickname in self.nickname_to_service:
            return self.nickname_to_service[nickname]
        config = self.nickname_to_config[nickname]
        service_type = config["type"]
        service = services_loader.load(service_type, config)
        self.nickname_to_service[nickname] = service
        return service

    def load_all_services(self):
        failures = []
        for nickname in self.nickname_to_config:
            try:
                yield self.load_service(nickname)
            except Exception as exc:
                import traceback
                # NOTE: Failure to load a service is expected.
                #       Perhaps a custom error should be thrown
                failures.append(nickname)
                logger.debug(traceback.format_exc())

        if failures:
            logger.warn(f"Failed to load some services: {', '.join(failures)}")

    def load_client(self, service_selector):
        if service_selector in self.nickname_to_client:
            return self.nickname_to_client[service_selector]
        if service_selector is None:
            client = loader.load_global_client(self.load_all_services())
        elif service_selector == SERVICE_NICKNAME_ALL:
            client = loader.load_multi_client(self.load_all_services())
        else:
            service_name = service_selector
            client = loader.load_single_client(self.load_service(service_name))
        self.nickname_to_client[service_selector] = client
        return client

    def get_config(self, service_selector=None):
        if not service_selector or service_selector == SERVICE_NICKNAME_ALL:
            return self.nickname_to_config
        return self.nickname_to_config[service_selector]

    def load_service_description(self, service_selector):
        from mediaman.core import descriptions
        if service_selector == SERVICE_NICKNAME_ALL:
            return descriptions.ALL_DESCRIPTION
        service_type = self.nickname_to_config[service_selector]["type"]
        return descriptions.SERVICE_TYPE_TO_DESCRIPTION[service_type]


def load_policy():
    global POLICY
    if POLICY is None:
        POLICY = Policy()
    return POLICY


def load_client(service_selector):
    return load_policy().load_client(service_selector)
