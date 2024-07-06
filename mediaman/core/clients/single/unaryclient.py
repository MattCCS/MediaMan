
from typing import Iterator

from mediaman.core.models import Response
from mediaman.core.clients.multi import abstract
from mediaman.core.clients.multi import methods
from mediaman.services.abstract.models import AbstractResultFile


def gen(client, result):
    yield Response(client, response=result, exception=None)


class UnaryClient:
    """
    Class handling `mm <service> ...` commands.
    """

    RAW_FUNC_NAMES = [
        "download",
        "migrate_to_v2",
        "remove",
        "stream",
        "stream_range",
        "tag",
        "upload",
    ]

    RESPONSE_FUNC_NAMES = [
        "capacity",
        "fuzzy_search_by_name",
        "has",
        "has_hash",
        "list_files",
        "refresh",
        "refresh_global_hashes",
        "search_by_hash",
        "search_by_name",
        "stats",
    ]

    def __init__(self, client):
        self.client = client

        for func_name in UnaryClient.RAW_FUNC_NAMES:
            orig_func = getattr(self.client, func_name)
            setattr(self, func_name, orig_func)

        for func_name in UnaryClient.RESPONSE_FUNC_NAMES:
            def wrap_response(func):
                def wrapped(*a, **k):
                    return gen(self.client, func(*a, **k))
                return wrapped

            orig_func = getattr(self.client, func_name)
            setattr(self, func_name, wrap_response(orig_func))
