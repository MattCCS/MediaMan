"""
Universal API to interact with MediaMan
"""

from mediaman.core import client
from mediaman.core import multiclient
from mediaman.core import methods
from mediaman.services import loader

__all__ = [
    "run_list",
]


def load_single_client(service_name):
    service = loader.load(service_name)
    return client.Client(service)


def load_multi_client():
    return multiclient.Multiclient([client.Client(service) for service in loader.load_all()])


def load_global_client():
    raise NotImplementedError()


def load_client(service_name=None):
    if service_name is None:
        return load_global_client()
    elif service_name == "all":
        return load_multi_client()
    else:
        return load_single_client(service_name)


def run_global(root, args):
    services = loader.load_all()
    # TODO: single (multi-)client object wrapper
    clients = [client.Client(service) for service in services]
    return methods.run_global(root, args, clients)


def run_single(root, args):
    service = loader.load(args.service)
    client_ = client.Client(service)
    return methods.run_service(root, args, client_)


def run_list(service_name=None):
    return load_client(service_name=service_name).list_files()


def run_has(root, *file_names, service_name=None):
    return load_client(service_name=service_name).exists(*file_names)


def run_get(root, *file_names, service_name=None):
    return load_client(service_name=service_name).download(*file_names)


def run_put(root, *file_names, service_name=None):
    return load_client(service_name=service_name).upload(*file_names)


def run_search(root, *file_names, service_name=None):
    return load_client(service_name=service_name).search_by_name(*file_names)
