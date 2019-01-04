"""
Universal API to interact with MediaMan
"""

from mediaman.services import loader
from mediaman.core.clients.single import client as singleclient
from mediaman.core.clients.multi import multiclient
from mediaman.core.clients.multi import globalmulticlient

__all__ = [
    "run_list",
]


def load_single_client(service_name):
    service = loader.load(service_name)
    return singleclient.SingleClient(service)


def load_multi_client():
    return multiclient.Multiclient([singleclient.SingleClient(service) for service in loader.load_all()])


def load_global_client():
    return globalmulticlient.GlobalMulticlient([singleclient.SingleClient(service) for service in loader.load_all()])


def load_client(service_name=None):
    if service_name is None:
        return load_global_client()
    elif service_name == "all":
        return load_multi_client()
    else:
        return load_single_client(service_name)


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
