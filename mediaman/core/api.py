"""
Universal API to interact with MediaMan
"""

from mediaman.core import policy

__all__ = [
    "run_list",
    "run_has",
    "run_get",
    "run_put",
    "run_search",
]


def run_list(service_selector=None):
    return policy.load_client(service_selector=service_selector).list_files()


def run_has(root, *file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).has(root, *file_names)


def run_get(root, *file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).download(*file_names)


def run_put(root, *file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).upload(*file_names)


def run_search(root, *file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).search_by_name(*file_names)


def run_fuzzy(root, *file_names, service_selector=None):
    return policy.load_client(service_selector=service_selector).fuzzy_search_by_name(*file_names)


def run_cap(service_selector=None):
    return policy.load_client(service_selector=service_selector).capacity()
