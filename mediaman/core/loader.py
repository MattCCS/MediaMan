

def load_index_class():
    from mediaman.core.index.index import Index
    return Index


def load_multiindex_class():
    from mediaman.core.multiindex.base import BaseMultiIndex
    return BaseMultiIndex


def load_single_client(service):
    from mediaman.core.clients.single import client as singleclient
    return load_multiindex_class()(
        singleclient.SingleClient(load_index_class()(service)))


def load_multi_client(services):
    from mediaman.core.clients.multi import multiclient
    from mediaman.core.clients.single import client as singleclient
    return load_multiindex_class()(
        multiclient.Multiclient(
            [singleclient.SingleClient(load_index_class()(service))
             for service in services]))


def load_global_client(services):
    from mediaman.core.clients.multi import globalmulticlient
    from mediaman.core.clients.single import client as singleclient
    return load_multiindex_class()(
        globalmulticlient.GlobalMulticlient(
            [singleclient.SingleClient(load_index_class()(service))
             for service in services]))
