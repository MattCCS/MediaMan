
import enum
import sys

from mediaman.core import logtools


COMMAND_NAME = "mm"

SHORT_DESCRIPTION = """\
MediaMan is a simple but robust file archiving tool.

Pass the help flag (-h or --help) for more info."""

DESCRIPTION = """\
MediaMan is a tool to manage the backup of files and data to arbitrary services
(such as Google Drive, Dropbox, external drives, etc.) with a consistent
interface and user experience."""

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

LIST_TEXT_SERVICE = "List all files indexed by this service"
HAS_TEXT_SERVICE = "Check whether this service has the given file(s)"
GET_TEXT_SERVICE = "Retrieve the given file(s) from this service"
PUT_TEXT_SERVICE = "Save the given file(s) to this service"
SEARCH_TEXT_SERVICE = "Search this service for the given filename(s)"
FUZZY_TEXT_SERVICE = "Search this service for similar filename(s)"
STATUS_TEXT_SERVICE = "Report on the status/availability of this service"
CAPACITY_TEXT_SERVICE = "Report on the visible capacity of this service"
CONFIG_TEXT_SERVICE = "Show the config info of this service"


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


ACTIONS = frozenset(action.value for action in Action)


def parse_args():
    if len(sys.argv) < 2:
        exit(parse_args_empty())  # to show short description

    if sys.argv[1] in ('-h', '--help'):
        exit(parse_args_base())  # to show help text

    if sys.argv[1] in ACTIONS:
        args = parse_args_action()
        args.service = None
    else:
        args = parse_args_service_action()

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


def parse_args_base():
    """Check for `mm (-h, --help)`"""
    parser = base_parser()

    parser.add_argument("service", nargs="?", help="(run `mm services` for options)")
    parser.add_argument("action", nargs="?", metavar="action", choices=ACTIONS, help="{%(choices)s}")

    return parser.parse_args()


def parse_args_action():
    """Check for `mm <action>`"""
    parser = base_parser()

    action_parsers = parser.add_subparsers(dest="action")
    add_commands(action_parsers, service=None)

    return parser.parse_args()


def parse_args_service_action():
    """Check for `mm <service> [action]`"""
    from mediaman.core import api
    service_names = api.get_service_names()

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

    add_parser(Action.LIST.value, description=f"[{service}] -- {LIST_TEXT_SERVICE}" if service else LIST_TEXT)
    p_has = add_parser(Action.HAS.value, description=f"[{service}] -- {HAS_TEXT_SERVICE}" if service else HAS_TEXT)
    p_get = add_parser(Action.GET.value, description=f"[{service}] -- {GET_TEXT_SERVICE}" if service else GET_TEXT)
    p_put = add_parser(Action.PUT.value, description=f"[{service}] -- {PUT_TEXT_SERVICE}" if service else PUT_TEXT)
    p_search = add_parser(Action.SEARCH.value, description=f"[{service}] -- {SEARCH_TEXT_SERVICE}" if service else SEARCH_TEXT)
    p_fuzzy = add_parser(Action.FUZZY.value, description=f"[{service}] -- {FUZZY_TEXT_SERVICE}" if service else FUZZY_TEXT)
    add_parser(Action.STATUS.value, description=f"[{service}] -- {STATUS_TEXT_SERVICE}" if service else STATUS_TEXT)
    add_parser(Action.CAPACITY.value, description=f"[{service}] -- {CAPACITY_TEXT_SERVICE}" if service else CAPACITY_TEXT)
    add_parser(Action.CONFIG.value, description=f"[{service}] -- {CONFIG_TEXT_SERVICE}" if service else CONFIG_TEXT)

    for parser in [p_has, p_get, p_put, p_search, p_fuzzy]:
        parser.add_argument("files", nargs="+")


def run_services():
    from mediaman.core import policy
    return policy.load_service_names()


def main():
    args = parse_args()

    import pathlib

    from mediaman import config
    from mediaman.core import api
    from mediaman.core import watertable

    root = pathlib.Path(config.load("SAVED_PWD", default="."))

    service_selector = args.service
    all_mode = service_selector == "all"

    if args.action == "config":
        import pprint
        print(pprint.pformat(api.run_config(args.service)))
        exit(0)
    elif args.action == "services":
        print(run_services())
        exit(0)
    elif args.action == "list":
        results = api.run_list(service_selector=service_selector)
        columns = ((("service", 16),) if all_mode else ()) + (("name", 40 + (0 if all_mode else 12)), ("hash", 64), ("id", 36))
        # it = ((result.client.name(), (' ' if not result.response else str(len(result.response)))) for result in results)
        # it = (() for result in results for row in result.response)

        def it(results):
            nonlocal all_mode
            if not all_mode:
                for item in results:
                    yield (item["name"], item["hash"], item["id"])
            else:
                for result in results:
                    if result.response:
                        for item in result.response:
                            yield (result.client.name(), item["name"], item["hash"], item["id"])

        gen = watertable.table_stream(columns, it(results))
        for row in gen:
            print(row)
    elif args.action == "has":
        results = api.run_has(root, *args.files, service_selector=service_selector)
        if service_selector == "all":
            columns = (("service", 16),) + tuple((file_name, max(3, len(file_name))) for file_name in args.files)
            it = ((result.client.name(), ("No" if not result.response else "Yes")) for result in results)
            gen = watertable.table_stream(columns, it)
            for row in gen:
                print(row)
        else:
            print(repr(results))
            exit(not results)
            # if results:
            #     print(results)
            # else:
            #     s = 's' if (len(args.files) > 1) else ''
            #     were = 'were' if (len(args.files) > 1) else 'was'
            #     print(f"[-] No file{s} with the name{s} {args.files} {were} found.")
            #     exit(1)
    elif args.action == "get":
        results = api.run_get(root, *args.files, service_selector=service_selector)
        print(repr(results))
    elif args.action == "put":
        results = api.run_put(root, *args.files, service_selector=service_selector)
        if all_mode:
            for result in results:
                print(repr(result))
        else:
            print(repr(results))
    elif args.action == "search":
        results = api.run_search(root, *args.files, service_selector=service_selector)
        total = 0
        for (total, result) in enumerate(results, 1):
            print(result)
        print(f"{total} results found.")
    elif args.action == "fuzzy":
        results = api.run_fuzzy(root, *args.files, service_selector=service_selector)
        if service_selector != "all":
            columns = (("name", 60), ("hash", 64), ("id", 36))

            def it(results):
                for item in results:
                    yield (item["name"], item["hash"], item["id"])

            gen = watertable.table_stream(columns, it(results))
            for row in gen:
                print(row)
        else:
            total = 0
            for (total, result) in enumerate(results, 1):
                print(result)
            print(f"{total} results found.")
    elif args.action == "cap":
        results = api.run_cap(service_selector=service_selector)
        if service_selector != "all":
            results = [results]
        for result in results:
            print(result)
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
