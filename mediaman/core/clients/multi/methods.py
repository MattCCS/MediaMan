"""
"""

import concurrent.futures
from multiprocessing import Process, Queue
from typing import Iterable

from mediaman.core import logtools
from mediaman.core import models

logger = logtools.new_logger("mediaman.core.clients.multimethods")


def multi_apply_concurrent(clients, func_name, *args, **kwargs):
    """
    WARNING: will finish all execution before garbage collection.

    1. Finish all execution
    2. Garbage collection
    3. Raise StopIteration
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(getattr(client, func_name), *args, **kwargs): client for client in clients}
        for future in concurrent.futures.as_completed(futures):
            print(future)
            client = futures[future]
            try:
                yield models.Response(client, future.result(), None)
            except Exception as exc:
                logger.error(f"[!] Client {repr(client)} threw error: {repr(exc)}", exc_info=True)
                yield models.Response(client, None, exc)


def call(q, client, func_name, args, kwargs):
    try:
        result = getattr(client, func_name)(*args, **kwargs)
        out = models.Response(client, result, None)
    except Exception as exc:
        logger.error(f"[!] Client {client} threw error: {repr(exc)}", exc_info=True)
        out = models.Response(client, None, exc)

    q.put(out)


def multi_apply(clients, func_name, *args, **kwargs):
    """WARNING: manually terminates processes."""
    q = Queue()

    procs = [Process(target=call, args=(q, c, func_name, args, kwargs)) for c in clients]
    for proc in procs:
        proc.start()

    for _ in range(len(clients)):
        go = yield q.get()

        if not go:
            for proc in procs:
                proc.terminate()
            return


def list_files(clients) -> Iterable[models.Response]:
    return multi_apply(clients, "list_files")


def has(clients, root, file_id) -> Iterable[models.Response]:
    return multi_apply(clients, "has", root, file_id)


def search_by_name(clients, file_name) -> Iterable[models.Response]:
    return multi_apply(clients, "search_by_name", file_name)


def fuzzy_search_by_name(clients, file_name) -> Iterable[models.Response]:
    return multi_apply(clients, "fuzzy_search_by_name", file_name)


def upload(clients, file_path) -> Iterable[models.Response]:
    return multi_apply(clients, "upload", file_path)


def capacity(clients) -> Iterable[models.Response]:
    return multi_apply(clients, "capacity")
