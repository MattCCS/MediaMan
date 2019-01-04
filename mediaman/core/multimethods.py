"""
"""

import concurrent.futures
from typing import Iterable

from mediaman.core import logtools
from mediaman.core import models

logger = logtools.new_logger("mediaman.core.multimethods")


def multi_apply(clients, func, *args, **kwargs):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(func(client), *args, **kwargs): client for client in clients}
        for future in concurrent.futures.as_completed(futures):
            client = futures[future]
            try:
                yield models.MultiResponse(client, future.result(), None)
            except Exception as exc:
                logger.error(f"[!] Client {repr(client)} threw error: {repr(exc)}", exc_info=True)
                yield models.MultiResponse(client, None, exc)


def list_files(clients) -> Iterable[models.MultiResponse]:
    yield from multi_apply(clients, lambda c: c.list_files)


def exists(clients, file_id) -> Iterable[models.MultiResponse]:
    yield from multi_apply(clients, lambda c: c.exists, file_id)


def search_by_name(clients, file_name) -> Iterable[models.MultiResponse]:
    yield from multi_apply(clients, lambda c: c.search_by_name, file_name)
