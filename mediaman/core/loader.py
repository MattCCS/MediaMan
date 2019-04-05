
from mediaman.core.index.index import Index


def load_index_class():
    return Index


def load_single_client(service):
    from mediaman.core.clients.single import client as singleclient
    return singleclient.SingleClient(load_index_class()(service))


def load_multi_client(services):
    from mediaman.core.clients.multi import multiclient
    from mediaman.core.clients.single import client as singleclient
    return multiclient.Multiclient([singleclient.SingleClient(load_index_class()(service)) for service in services])


def load_global_client(services):
    from mediaman.core.clients.multi import globalmulticlient
    from mediaman.core.clients.single import client as singleclient
    return globalmulticlient.GlobalMulticlient([singleclient.SingleClient(load_index_class()(service)) for service in services])
