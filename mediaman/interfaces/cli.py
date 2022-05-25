
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
STREAM_TEXT = "Stream the given file from MediaMan"
STREAMRANGE_TEXT = "Stream the given file from MediaMan, from offset up to length"
PUT_TEXT = "Save the given file(s) to MediaMan"
SEARCH_TEXT = "Search MediaMan for the given filename(s)"
FUZZY_TEXT = "Search MediaMan for similar filename(s)"
STATS_TEXT = "Show the stats for Mediaman"
CAPACITY_TEXT = "Report on the visible capacity of MediaMan"
CONFIG_TEXT = "Show the config info of MediaMan"
REFRESH_TEXT = "Refresh the tracking info of MediaMan"
SEARCH_BY_HASH_TEXT = "Search MediaMan for the given hash(es)"
TAG_TEXT = "Set tags on one or more files in MediaMan"

LIST_TEXT_SERVICE = "List all files indexed by this service"
HAS_TEXT_SERVICE = "Check whether this service has the given file(s)"
GET_TEXT_SERVICE = "Retrieve the given file(s) from this service"
STREAM_TEXT_SERVICE = "Stream the given file from this service"
STREAMRANGE_TEXT_SERVICE = "Stream the given file from this service, from offset up to length"
PUT_TEXT_SERVICE = "Save the given file(s) to this service"
SEARCH_TEXT_SERVICE = "Search this service for the given filename(s)"
FUZZY_TEXT_SERVICE = "Search this service for similar filename(s)"
STATS_TEXT_SERVICE = "Show the stats for this service"
CAPACITY_TEXT_SERVICE = "Report on the visible capacity of this service"
CONFIG_TEXT_SERVICE = "Show the config info of this service"
REFRESH_TEXT_SERVICE = "Refresh the tracking info of this service"
REMOVE_TEXT_SERVICE = "Remove the given file(s) from this service (by hash only)"
SEARCH_BY_HASH_TEXT_SERVICE = "Search this service for the given hash(es)"
TAG_TEXT_SERVICE = "Set tags on one or more files in this service"


class Action(enum.Enum):
    SERVICES = "services"
    SYNC = "sync"

    LIST = "list"
    HAS = "has"
    GET = "get"
    STREAM = "stream"
    STREAMRANGE = "streamrange"
    PUT = "put"
    SEARCH = "search"
    FUZZY = "fuzzy"
    STATS = "stats"
    CAPACITY = "cap"
    CONFIG = "config"
    REFRESH = "refresh"
    REMOVE = "remove"
    SEARCH_BY_HASH = "search-by-hash"
    TAG = "tag"

    MIGRATE_TO_V2 = "migrate-to-v2"  # TODO: temporary command


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

    p_list = add_parser(Action.LIST.value, description=f"[{service}] -- {LIST_TEXT_SERVICE}" if service else LIST_TEXT)
    p_has = add_parser(Action.HAS.value, description=f"[{service}] -- {HAS_TEXT_SERVICE}" if service else HAS_TEXT)
    p_get = add_parser(Action.GET.value, description=f"[{service}] -- {GET_TEXT_SERVICE}" if service else GET_TEXT)
    p_stream = add_parser(Action.STREAM.value, description=f"[{service}] -- {STREAM_TEXT_SERVICE}" if service else STREAM_TEXT)
    p_streamrange = add_parser(Action.STREAMRANGE.value, description=f"[{service}] -- {STREAMRANGE_TEXT_SERVICE}" if service else STREAMRANGE_TEXT)
    p_put = add_parser(Action.PUT.value, description=f"[{service}] -- {PUT_TEXT_SERVICE}" if service else PUT_TEXT)
    p_search = add_parser(Action.SEARCH.value, description=f"[{service}] -- {SEARCH_TEXT_SERVICE}" if service else SEARCH_TEXT)
    p_fuzzy = add_parser(Action.FUZZY.value, description=f"[{service}] -- {FUZZY_TEXT_SERVICE}" if service else FUZZY_TEXT)
    add_parser(Action.STATS.value, description=f"[{service}] -- {STATS_TEXT_SERVICE}" if service else STATS_TEXT)
    add_parser(Action.CAPACITY.value, description=f"[{service}] -- {CAPACITY_TEXT_SERVICE}" if service else CAPACITY_TEXT)
    p_config = add_parser(Action.CONFIG.value, description=f"[{service}] -- {CONFIG_TEXT_SERVICE}" if service else CONFIG_TEXT)
    add_parser(Action.REFRESH.value, description=f"[{service}] -- {REFRESH_TEXT_SERVICE}" if service else REFRESH_TEXT)
    p_search_by_hash = add_parser(Action.SEARCH_BY_HASH.value, description=f"[{service}] -- {SEARCH_BY_HASH_TEXT_SERVICE}" if service else SEARCH_BY_HASH_TEXT)
    p_tag = add_parser(Action.TAG.value, description=f"[{service}] -- {TAG_TEXT_SERVICE}" if service else TAG_TEXT)
    p_migrate_to_v2 = add_parser(Action.MIGRATE_TO_V2.value, description=f"[{service}] -- migrate to v2")

    for parser in [p_stream, p_streamrange]:
        parser.add_argument("file")

    for parser in [p_streamrange]:
        parser.add_argument("offset", type=int, nargs="?", default=0)
        parser.add_argument("length", type=int, nargs="?", default=-1)

    for parser in [p_has, p_get, p_put, p_search, p_fuzzy]:
        parser.add_argument("files", nargs="+")

    for parser in [p_config]:
        parser.add_argument("-e", "--edit", action="store_true", default=False, help="Edit the config file with your $EDITOR")

    for parser in [p_search_by_hash]:
        parser.add_argument("hashes", nargs="+")

    for parser in [p_tag]:
        parser.add_argument("hashes", nargs="+")
        parser.add_argument("-a", "--add", nargs="+", help="Add the given tag(s) (idempotent)")
        parser.add_argument("-r", "--remove", nargs="+", help="Remove the given tag(s) (idempotent)")
        parser.add_argument("-s", "--set", nargs="+", help="Set the given tag(s), removing any tags not mentioned")

    for parser in [p_list, p_search, p_fuzzy, p_search_by_hash]:
        parser.add_argument("-r", "--raw", action="store_true", default=False, help="Do not print an ASCII table")


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


def files_iterator(responses, all_mode):
    if not all_mode:
        for (request, file_results_list) in responses:
            for item in file_results_list:
                yield (item["name"], human_bytes(item["size"]), item["hashes"][-1], item["id"], item["tags"])
    else:
        # TODO: this is screwed up, need to stick to classes better
        all_responses = responses
        for (request, responses) in all_responses:
            for response_obj in responses:
                if response_obj.response:
                    for item in response_obj.response:
                        yield (response_obj.client.nickname(), item["name"], human_bytes(item["size"]), item["hashes"][-1], item["id"], item["tags"])


def run_file_list(results, all_mode=False):
    from mediaman.core import watertable

    columns = ((("service", 16),) if all_mode else ()) + (("name", 39 + (0 if all_mode else 19)), ("size", 9), ("hash", 22), ("id", 36), ("tags", 20))

    gen = watertable.table_stream(columns, files_iterator(results, all_mode))
    for row in gen:
        print(row)


def main():
    args = parse_args()

    import os
    import pathlib

    from mediaman import config
    from mediaman.core import api
    from mediaman.core import watertable

    root = pathlib.Path(os.environ.get("SAVED_PWD", os.environ.get("PWD", ".")))

    service_selector = args.service
    all_mode = service_selector == "all"

    file_results_list_funcs = {
        "list", "search", "fuzzy", "search-by-hash"
    }

    if args.action in file_results_list_funcs:
        if args.action == "list":
            results = [(None, api.run_list(service_selector=service_selector))]
        elif args.action == "search":
            results = api.run_search(*args.files, service_selector=service_selector)
        elif args.action == "fuzzy":
            results = api.run_fuzzy(*args.files, service_selector=service_selector)
        elif args.action == Action.SEARCH_BY_HASH.value:
            results = api.run_search_by_hash(*args.hashes, service_selector=service_selector)
        else:
            raise NotImplementedError()

        if args.raw:
            for each in files_iterator(results, all_mode):
                print(each)
        else:
            run_file_list(results, all_mode=all_mode)
        exit(0)

    if args.action == "config":
        if args.edit:
            config.launch_editor()
        else:
            import pprint
            print(pprint.pformat(api.run_config(args.service)))
            exit(0)
    elif args.action == "services":
        print(run_services())
        exit(0)
    elif args.action == "has":
        all_results = api.run_has(root, *args.files, service_selector=service_selector)

        service_names = sorted(set(api.get_service_names()) - set(["all"]))
        max_filename = max([len(str(pathlib.Path(f).absolute())) for f in args.files])
        print([str(pathlib.Path(f).absolute()) for f in args.files])
        print(max_filename)

        columns = (("name", max(4, max_filename)),)
        if all_mode:
            columns += tuple((service, len(service)) for service in service_names)
        else:
            columns += (("found?", 6),)

        def inverted_iter(services, files, all_results, all_mode=False):
            if all_mode:
                for (request, results) in all_results:
                    service_map = {result.client.nickname(): ("No" if not result.response else "Yes") for result in results}
                    yield (request,) + tuple(service_map.get(service, "--") for service in services)

            else:
                results = all_results
                for (request, result) in results:
                    yield (request, ("No" if not result else "Yes"))

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
    elif args.action == "stream":
        stream = api.run_stream(root, args.file, service_selector=service_selector)
        for bytez in stream:
            sys.stdout.buffer.write(bytez)
            sys.stdout.buffer.flush()
    elif args.action == "streamrange":
        stream = api.run_stream_range(root, args.file, args.offset, args.length, service_selector=service_selector)
        for bytez in stream:
            sys.stdout.buffer.write(bytez)
            sys.stdout.buffer.flush()
    elif args.action == "put":
        all_results = api.run_put(root, *args.files, service_selector=service_selector)
        if all_mode:
            for (path, results) in all_results:
                for result in results:
                    print(path, result)
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
    elif args.action == Action.STATS.value:
        results = api.run_stats(service_selector=service_selector)
        if service_selector != "all":
            results = [results]
        for result in results:
            print(repr(result))
    elif args.action == Action.TAG.value:
        results = api.run_tag(
            root,
            identifiers=args.hashes,
            add=args.add,
            remove=args.remove,
            set=args.set,
            service_selector=service_selector,
        )
        if service_selector != "all":
            results = [results]
        for result in results:
            print(result)
    elif args.action == Action.MIGRATE_TO_V2.value:
        api.run_migrate_to_v2(service_selector=service_selector)
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
