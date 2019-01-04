
import argparse
import pathlib

from mediaman import config
from mediaman.core import api
from mediaman.core import logtools
from mediaman.core import watertable

COMMAND_NAME = "mm"

SHORT_DESCRIPTION = """\
MediaMan is a simple but robust file archiving tool.

Pass the help flag (-h or --help) for more info."""

DESCRIPTION = """\
MediaMan is a tool to manage the backup of files and data to arbitrary services
(such as Google Drive, Dropbox, external drives, etc.) with a consistent
interface and user experience."""

LOCAL_DESCRIPTION = """\
[local] -- Allows you to back up files to a network share, external drive,
or even a directory on your local drive (if that's what you're into).
Configurable in the config.yaml file."""

DRIVE_DESCRIPTION = """\
[drive] -- Allows you to back up files to Google Drive (requires Drive credentials).
Can even back up to a specific folder within Google Drive.
Configurable in the config.yaml file."""

ALL_DESCRIPTION = """\
[all] -- Allows you to back up files to all configured services at once.
Will also report information about all configured services."""

LIST_TEXT_MM = "List all files indexed by MediaMan"
HAS_TEXT_MM = "Check whether MediaMan has the given file(s)"
GET_TEXT_MM = "Get the given file(s)"
PUT_TEXT_MM = "Back up the given file(s)"

LIST_TEXT_GLOBAL = "List all files indexed across all services"
HAS_TEXT_GLOBAL = "Check which services have the given file(s)"
GET_TEXT_GLOBAL = "Get the given file(s) from whichever service"
PUT_TEXT_GLOBAL = "Back up the given file(s) to all services"

LIST_TEXT_SERVICE = "List the files indexed in this service"
HAS_TEXT_SERVICE = "Check whether this service has the given file(s)"
GET_TEXT_SERVICE = "Get the given file(s) from this service"
PUT_TEXT_SERVICE = "Back up the given file(s) to this service"


# def parse_args():
#     parser = argparse.ArgumentParser(description="MediaMan!")
#     command_group = parser.add_mutually_exclusive_group()
#     subcommand_group = parser.add_mutually_exclusive_group()

#     subparsers = subcommand_group.add_subparsers(help="sub-command help")
#     parser_list = [command_group]
#     parser_list.append(subparsers.add_parser("local", help="local help"))
#     parser_list.append(subparsers.add_parser("drive", help="drive help"))

#     for each in parser_list:
#         each.add_argument("action", choices=["list", "has", "put"])

#     return parser.parse_args()


def parse_args():
    args = parse_args_subcommand()
    if not hasattr(args, "action"):
        return parse_args_command()
    return args


def parse_args_command():
    parser = argparse.ArgumentParser()
    logtools.add_log_parser(parser)
    subparsers = parser.add_subparsers(help="command", dest="action")

    add_global_commands(subparsers)
    return parser.parse_args()


def parse_args_subcommand():
    parser = argparse.ArgumentParser(prog=COMMAND_NAME, description=DESCRIPTION)
    logtools.add_log_parser(parser)
    subparsers = parser.add_subparsers(help="Backup service options", dest="service")

    subparsers_map = {
        "local": subparsers.add_parser("local", help="The local filesystem", description=LOCAL_DESCRIPTION),
        "drive": subparsers.add_parser("drive", help="Google drive", description=DRIVE_DESCRIPTION),
        "all": subparsers.add_parser("all", help="(All configured services at once)", description=ALL_DESCRIPTION),
    }

    for subparser in subparsers_map.values():
        logtools.add_log_parser(subparser)
        subsubparsers = subparser.add_subparsers(help="command", dest="action")
        add_service_commands(subsubparsers)

    add_global_commands(subparsers)
    args = parser.parse_args()

    if hasattr(args, "action") and not args.action:
        subparser = subparsers_map[args.service]
        subparser.print_help()
        exit()

    return args


def add_global_commands(subparsers):
    subparsers.add_parser("sync", description="Synchronize all services (if possible)")
    subparsers.add_parser("list", description=LIST_TEXT_GLOBAL)
    subparsers.add_parser("has", description=HAS_TEXT_GLOBAL).add_argument("files", nargs="+")
    subparsers.add_parser("get", description=GET_TEXT_GLOBAL).add_argument("files", nargs="+")
    subparsers.add_parser("put", description=PUT_TEXT_GLOBAL).add_argument("files", nargs="+")
    subparsers.add_parser("stat")
    subparsers.add_parser("cap")


def add_service_commands(subparsers):
    subparsers.add_parser("list", help=LIST_TEXT_SERVICE, description=LIST_TEXT_SERVICE)
    subparsers.add_parser("has", help=HAS_TEXT_SERVICE, description=HAS_TEXT_SERVICE).add_argument("files", nargs="+")
    subparsers.add_parser("get", help=GET_TEXT_SERVICE, description=GET_TEXT_SERVICE).add_argument("files", nargs="+")
    subparsers.add_parser("put", help=PUT_TEXT_SERVICE, description=PUT_TEXT_SERVICE).add_argument("files", nargs="+")
    subparsers.add_parser("stat")
    subparsers.add_parser("cap")


def main():
    args = parse_args()
    # print(args)

    root = pathlib.Path(config.load("SAVED_PWD", default="."))

    if not args.action:
        print(SHORT_DESCRIPTION)
        return

    if not hasattr(args, "service"):
        service_name = None
    else:
        service_name = args.service

    # return api.run_global(root, args)
    if args.action == "list":
        results = api.run_list(service_name=service_name)
        if service_name == "all":
            columns = (("service", 16), ("name", 40), ("hash", 64), ("id", 36))
            # it = ((result.client.name(), (' ' if not result.response else str(len(result.response)))) for result in results)
            # it = (() for result in results for row in result.response)

            def it(results):
                for result in results:
                    if result.response:
                        for item in result.response:
                            yield (result.client.name(), item["name"], item["hash"], item["id"])

            gen = watertable.table_stream(columns, it(results))
            for row in gen:
                print(row)
        else:
            print(repr(results))
    elif args.action == "has":
        results = api.run_search(root, *args.files, service_name=service_name)
        if service_name == "all":
            columns = (("service", 16),) + tuple((file_name, len(file_name)) for file_name in args.files)
            it = ((result.client.name(), (' ' if not result.response else str(len(result.response)))) for result in results)
            gen = watertable.table_stream(columns, it)
            for row in gen:
                print(row)
        else:
            print(repr(results))
    elif args.action == "get":
        results = api.run_get(root, *args.files, service_name=service_name)
        print(repr(results))
    elif args.action == "put":
        results = api.run_put(root, *args.files, service_name=service_name)
        print(repr(results))
    else:
        raise NotImplementedError()


if __name__ == '__main__':
    main()
