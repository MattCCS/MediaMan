"""
Universal API to interact with MediaMan
"""

from mediaman.core import client
from mediaman.core import methods
from mediaman.services import loader

__all__ = [
    "run_global",
    "run_single",
    "run_multi",
]


def run_global(root, args):
    services = loader.load_all()
    # TODO: single (multi-)client object wrapper
    clients = [client.Client(service) for service in services]
    return methods.run_global(root, args, clients)


def run_single(root, args):
    service = loader.load(args.service)
    client_ = client.Client(service)
    return methods.run_service(root, args, client_)


def run_multi(root, args):
    raise NotImplementedError()
