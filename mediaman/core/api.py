"""
Universal API to interact with MediaMan
"""

import sys
assert sys.version_info >= (3, 7, 0)  # noqa

from mediaman.core import policy


__all__ = [
    "run_list",
    "run_has",
    "run_get",
    "run_stream",
    "run_put",
    "run_search",
    "run_fuzzy",
    "run_cap",
    "run_stats",
    "run_config",
    "get_service_names",
    "get_service_description",
]


def run_list(service_selector=None):
    return policy.load_client(service_selector=service_selector).list_files()


def run_has(root, *file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).has(root, *file_names)


def run_get(root, *file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).download(root, *file_names)


def run_stream(root, file_name, service_selector=None):
    return policy.load_client(service_selector=service_selector).stream(root, file_name)


def run_stream_range(root, file_name, offset, length, service_selector=None):
    return policy.load_client(service_selector=service_selector).stream_range(root, file_name, offset, length)


def run_put(root, *file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).upload(root, *file_names)


def run_search(*file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).search_by_name(*file_names)


def run_fuzzy(*file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).fuzzy_search_by_name(*file_names)


def run_cap(service_selector=None):
    return policy.load_client(service_selector=service_selector).capacity()


def run_stats(service_selector=None):
    return policy.load_client(service_selector=service_selector).stats()


def run_config(service_selector=None):
    return policy.load_policy().get_config(service_selector=service_selector)


def get_service_names():
    return policy.load_service_names()


def get_service_description(service_selector):
    return policy.load_policy().load_service_description(service_selector)


def run_sync(service_selector=None):
    return policy.load_client(service_selector=service_selector).sync()


def run_refresh(service_selector=None):
    return policy.load_client(service_selector=service_selector).refresh()


def run_remove(*identifiers, service_selector=None):
    return policy.load_client(service_selector=service_selector).remove(*identifiers)
