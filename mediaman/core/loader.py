
from mediaman.core.index.index import Index
from mediaman.services import loader


def load_index_class():
    return Index


def load_index(service_name):
    index_class = load_index_class()
    service = loader.load(service_name)
    return index_class(service)


def load_all_indices():
    index_class = load_index_class()
    services = loader.load_all()
    return [index_class(service) for service in services]


def load_single_client(service_name):
    from mediaman.core.clients.single import client as singleclient
    return singleclient.SingleClient(load_index(service_name))


def load_multi_client():
    from mediaman.core.clients.multi import multiclient
    from mediaman.core.clients.single import client as singleclient
    return multiclient.Multiclient([singleclient.SingleClient(index) for index in load_all_indices()])


def load_global_client():
    from mediaman.core.clients.multi import globalmulticlient
    from mediaman.core.clients.single import client as singleclient
    return globalmulticlient.GlobalMulticlient([singleclient.SingleClient(index) for index in load_all_indices()])


def _load_client(service_selector=None):
    if service_selector is None:
        return load_global_client()
    elif service_selector == "all":
        return load_multi_client()
    else:
        service_name = service_selector
        return load_single_client(service_name)
