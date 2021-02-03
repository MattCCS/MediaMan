"""
"""

import concurrent.futures
from typing import Iterable

from mediaman.core import logtools
from mediaman.core import models

logger = logtools.new_logger(__name__)


def apply_consecutive(clients, func_name, *args, **kwargs):
    for client in clients:
        try:
            result = getattr(client, func_name)(*args, **kwargs)
            go = yield models.Response(client, result, None)
        except Exception as exc:
            go = yield models.Response(client, None, exc)

        if not go:
            return


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
            logger.debug(future)
            client = futures[future]
            try:
                yield models.Response(client, future.result(), None)
            except Exception as exc:
                logger.error(f"[!] Client {repr(client)} threw error: {repr(exc)}", exc_info=True)
                yield models.Response(client, None, exc)


# XXX: Can't use multiprocessing, as it doesn't keep state.
# def call(q, client, func_name, args, kwargs):
#     try:
#         result = getattr(client, func_name)(*args, **kwargs)
#         out = models.Response(client, result, None)
#     except Exception as exc:
#         logger.error(f"[!] Client {client} threw error: {repr(exc)}", exc_info=True)
#         out = models.Response(client, None, exc)

#     q.put(out)


# def multi_apply(clients, func_name, *args, **kwargs):
#     """WARNING: manually terminates processes."""
#     q = Queue()

#     procs = [Process(target=call, args=(q, c, func_name, args, kwargs)) for c in clients]
#     for proc in procs:
#         proc.start()

#     for _ in range(len(clients)):
#         go = yield q.get()

#         if not go:
#             for proc in procs:
#                 proc.terminate()
#             return


def force_init(clients):
    logger.warn("this is disabled")
    # return multi_apply_concurrent(clients, "force_init")


def list_files(clients) -> Iterable[models.Response]:
    return apply_consecutive(clients, "list_files")


def has(clients, file_path) -> Iterable[models.Response]:
    return apply_consecutive(clients, "has", file_path)


def has_hash(clients, hash) -> Iterable[models.Response]:
    return apply_consecutive(clients, "has_hash", hash)


def has_uuid(clients, uuid) -> Iterable[models.Response]:
    return apply_consecutive(clients, "has_uuid", uuid)


def has_name(clients, name) -> Iterable[models.Response]:
    return apply_consecutive(clients, "has_name", name)


def search_by_name(clients, file_name) -> Iterable[models.Response]:
    return apply_consecutive(clients, "search_by_name", file_name)


def fuzzy_search_by_name(clients, file_name) -> Iterable[models.Response]:
    return apply_consecutive(clients, "fuzzy_search_by_name", file_name)


def search_by_hash(clients, hash) -> Iterable[models.Response]:
    return apply_consecutive(clients, "search_by_hash", hash)


def upload(clients, file_path) -> Iterable[models.Response]:
    return apply_consecutive(clients, "upload", file_path)


def stats(clients) -> Iterable[models.Response]:
    return apply_consecutive(clients, "stats")


def capacity(clients) -> Iterable[models.Response]:
    return apply_consecutive(clients, "capacity")


def refresh_global_hashes(clients, hashes_by_hash) -> Iterable[models.Response]:
    return apply_consecutive(clients, "refresh_global_hashes", hashes_by_hash)
