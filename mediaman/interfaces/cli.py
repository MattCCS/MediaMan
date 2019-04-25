
import enum
import sys

from mediaman.core import api
from mediaman.core import logtools


COMMAND_NAME = "mm"

SHORT_DESCRIPTION = """\
MediaMan is a simple but robust file archiving tool.

Pass the help flag (-h or --help) for more info."""

DESCRIPTION = """\
MediaMan is a tool to manage the backup of files and data to arbitrary services
(such as Google Drive, Dropbox, external drives, etc.) with a consistent
interface and user experience.
Run `mm <service> (-h | --help)` for more info about any particular service."""

SERVICES_TEXT = """List the service nicknames found in your config file.
(Does not guarantee that the services are active, or are even configured properly.)"""
SYNC_TEXT = "Synchronizes all services (if possible)"
LIST_TEXT = "List all files indexed by MediaMan"
HAS_TEXT = "Check whether MediaMan has the given file(s)"
GET_TEXT = "Retrieve the given file(s) from MediaMan"
PUT_TEXT = "Save the given file(s) to MediaMan"
SEARCH_TEXT = "Search MediaMan for the given filename(s)"
FUZZY_TEXT = "Search MediaMan for similar filename(s)"
STATUS_TEXT = "Report on the status/availability of MediaMan"
CAPACITY_TEXT = "Report on the visible capacity of MediaMan"
CONFIG_TEXT = "Show the config info of MediaMan"
REFRESH_TEXT = "Refresh the tracking info of MediaMan"

LIST_TEXT_SERVICE = "List all files indexed by this service"
HAS_TEXT_SERVICE = "Check whether this service has the given file(s)"
GET_TEXT_SERVICE = "Retrieve the given file(s) from this service"
PUT_TEXT_SERVICE = "Save the given file(s) to this service"
SEARCH_TEXT_SERVICE = "Search this service for the given filename(s)"
FUZZY_TEXT_SERVICE = "Search this service for similar filename(s)"
STATUS_TEXT_SERVICE = "Report on the status/availability of this service"
CAPACITY_TEXT_SERVICE = "Report on the visible capacity of this service"
CONFIG_TEXT_SERVICE = "Show the config info of this service"
REFRESH_TEXT_SERVICE = "Refresh the tracking info of this service"
REMOVE_TEXT_SERVICE = "Remove the given file(s) from this service (by hash only)"


class Action(enum.Enum):
    SERVICES = "services"
    SYNC = "sync"

    LIST = "list"
    HAS = "has"
    GET = "get"
    PUT = "put"
    SEARCH = "search"
    FUZZY = "fuzzy"
    STATUS = "stat"
    CAPACITY = "cap"
    CONFIG = "config"
    REFRESH = "refresh"
    REMOVE = "remove"


ACTIONS = frozenset(action.value for action in Action)


def parse_args():
    if len(sys.argv) < 2:
        exit(parse_args_empty())  # to show short description

    service_names = api.get_service_names()

    args = set(sys.argv[1:])
    help = args & set(['-h', '--help'])
    services = args & set(service_names)
    actions = args & set(ACTIONS)

    if help and not (services or actions):
        exit(parse_args_base(service_names))

    if not services:
        args = parse_args_action()
        args.service = None
    else:
        args = parse_args_service_action(service_names)

    return args


def parse_args_empty():
    """Check for `mm`"""
    print(SHORT_DESCRIPTION)
    exit()


def base_parser():
    import argparse
    parser = argparse.ArgumentParser(prog=COMMAND_NAME, description=DESCRIPTION)
    logtools.add_log_parser(parser)
    return parser


def parse_args_base(service_names):
    """Check for `mm (-h, --help)`"""
    parser = base_parser()

    parser.add_argument("service", nargs="?", help=f"{{{', '.join(service_names)}}} (Optional. From your config file.)")
    parser.add_argument("action", nargs="?", metavar="action", choices=ACTIONS, help="{%(choices)s}")

    return parser.parse_args()


def parse_args_action():
    """Check for `mm <action>`"""
    parser = base_parser()

    action_parsers = parser.add_subparsers(dest="action")
    add_commands(action_parsers, service=None)

    return parser.parse_args()


def parse_args_service_action(service_names):
    """Check for `mm <service> [action]`"""
    parser = base_parser()

    service_parsers = parser.add_subparsers(dest="service")
    for service_name in service_names:
        description = f"'{service_name}' {api.get_service_description(service_name)}"
        service_parser = service_parsers.add_parser(service_name, description=description)

        logtools.add_log_parser(service_parser)
        service_action_parsers = service_parser.add_subparsers(dest="action")
        add_commands(service_action_parsers, service=service_name)

    args = parser.parse_args()
    if not args.action:
        parser.parse_args([args.service, '-h'])

    return args


def add_commands(subparsers, service=None):

    def add_parser(*args, **kwargs):
        nonlocal subparsers
        subparser = subparsers.add_parser(*args, **kwargs)
        logtools.add_log_parser(subparser)
        return subparser

    if not service:
        add_parser(Action.SERVICES.value, description=SERVICES_TEXT)
        add_parser(Action.SYNC.value, description=SYNC_TEXT)

    if service:
        p_remove = add_parser(Action.REMOVE.value, description=f"[{service}] -- {REMOVE_TEXT_SERVICE}")
        p_remove.add_argument("hashes", nargs="+")

    add_parser(Action.LIST.value, description=f"[{service}] -- {LIST_TEXT_SERVICE}" if service else LIST_TEXT)
    p_has = add_parser(Action.HAS.value, description=f"[{service}] -- {HAS_TEXT_SERVICE}" if service else HAS_TEXT)
    p_get = add_parser(Action.GET.value, description=f"[{service}] -- {GET_TEXT_SERVICE}" if service else GET_TEXT)
    p_put = add_parser(Action.PUT.value, description=f"[{service}] -- {PUT_TEXT_SERVICE}" if service else PUT_TEXT)
    p_search = add_parser(Action.SEARCH.value, description=f"[{service}] -- {SEARCH_TEXT_SERVICE}" if service else SEARCH_TEXT)
    p_fuzzy = add_parser(Action.FUZZY.value, description=f"[{service}] -- {FUZZY_TEXT_SERVICE}" if service else FUZZY_TEXT)
    add_parser(Action.STATUS.value, description=f"[{service}] -- {STATUS_TEXT_SERVICE}" if service else STATUS_TEXT)
    add_parser(Action.CAPACITY.value, description=f"[{service}] -- {CAPACITY_TEXT_SERVICE}" if service else CAPACITY_TEXT)
    add_parser(Action.CONFIG.value, description=f"[{service}] -- {CONFIG_TEXT_SERVICE}" if service else CONFIG_TEXT)
    add_parser(Action.REFRESH.value, description=f"[{service}] -- {REFRESH_TEXT_SERVICE}" if service else REFRESH_TEXT)

    for parser in [p_has, p_get, p_put, p_search, p_fuzzy]:
        parser.add_argument("files", nargs="+")


def run_services():
    return api.get_service_names()


def human_bytes(n):
    """Return the given bytes as a human-friendly string"""

    step = 1000
    abbrevs = ['KB', 'MB', 'GB', 'TB']

    if n < step:
        return f"{n}B"

    for abbrev in abbrevs:
        n /= step
        if n < step:
            break

    return f"{n:.2f}{abbrev}"


def run_file_list(results, all_mode=False):
    from mediaman.core import watertable

    columns = ((("service", 16),) if all_mode else ()) + (("name", 40 + (0 if all_mode else 19)), ("size", 9), ("hash", 71), ("id", 36))

    def files_iterator(responses):
        nonlocal all_mode
        if not all_mode:
            for file_results_list in responses:
                for item in file_results_list:
                    yield (item["name"], human_bytes(item["size"]), item["hashes"][-1], item["id"])
        else:
            # TODO: this is screwed up, need to stick to classes better
            all_responses = responses
            for responses in all_responses:
                for response_obj in responses:
                    if response_obj.response:
                        for item in response_obj.response:
                            yield (response_obj.client.nickname(), item["name"], human_bytes(item["size"]), item["hashes"][-1], item["id"])

    gen = watertable.table_stream(columns, files_iterator(results))
    for row in gen:
        print(row)


def main():
    args = parse_args()

    import pathlib

    from mediaman import config
    from mediaman.core import api
    from mediaman.core import watertable

    root = pathlib.Path(config.load("SAVED_PWD", default="."))

    service_selector = args.service
    all_mode = service_selector == "all"

    file_results_list_funcs = {
        "list", "search", "fuzzy"
    }

    if args.action in file_results_list_funcs:
        if args.action == "list":
            results = [api.run_list(service_selector=service_selector)]
        elif args.action == "search":
            results = api.run_search(*args.files, service_selector=service_selector)
        elif args.action == "fuzzy":
            results = api.run_fuzzy(*args.files, service_selector=service_selector)
        else:
            raise NotImplementedError()

        run_file_list(results, all_mode=all_mode)
        exit(0)

    if args.action == "config":
        import pprint
        print(pprint.pformat(api.run_config(args.service)))
        exit(0)
    elif args.action == "services":
        print(run_services())
        exit(0)
    elif args.action == "has":
        all_results = api.run_has(root, *args.files, service_selector=service_selector)

        service_names = sorted(set(api.get_service_names()) - set(["all"]))
        max_filename = max(map(len, args.files))

        columns = (("name", max(4, max_filename)),)
        if all_mode:
            columns += tuple((service, len(service)) for service in service_names)
        else:
            columns += (("found?", 6),)

        def inverted_iter(services, files, all_results, all_mode=False):
            if all_mode:
                for (file_name, results) in zip(files, all_results):
                    service_map = {result.client.nickname(): ("No" if not result.response else "Yes") for result in results}
                    yield (file_name,) + tuple(service_map.get(service, "--") for service in services)

            else:
                results = all_results
                for (file_name, result) in zip(files, results):
                    yield (file_name, ("No" if not result else "Yes"))

        gen = watertable.table_stream(columns, inverted_iter(
            service_names, args.files, all_results, all_mode=all_mode))

        for row in gen:
            print(row)

        # exit(1)

        # if results:
        #     print(results)
        # else:
        #     s = 's' if (len(args.files) > 1) else ''
        #     were = 'were' if (len(args.files) > 1) else 'was'
        #     print(f"[-] No file{s} with the name{s} {args.files} {were} found.")
        #     exit(1)
    elif args.action == "get":
        results = api.run_get(root, *args.files, service_selector=service_selector)
        for result in results:
            print(repr(result))
    elif args.action == "put":
        all_results = api.run_put(root, *args.files, service_selector=service_selector)
        if all_mode:
            for results in all_results:
                for result in results:
                    print(repr(result))
        else:
            results = all_results
            for result in results:
                print(repr(result))
    elif args.action == "cap":
        results = api.run_cap(service_selector=service_selector)
        if service_selector != "all":
            results = [results]
        for result in results:
            print(result)
    elif args.action == "sync":
        results = api.run_sync(service_selector=service_selector)
        print(repr(results))
    elif args.action == Action.REFRESH.value:
        results = api.run_refresh(service_selector=service_selector)
        print(repr(results))
    elif args.action == Action.REMOVE.value:
        results = api.run_remove(*args.hashes, service_selector=service_selector)
        for result in results:
            print(repr(result))
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
