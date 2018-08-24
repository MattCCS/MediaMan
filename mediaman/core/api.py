
import argparse
import json
import pathlib

from mediaman import config
from mediaman.core import client
from mediaman.services import loader

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
    parser = argparse.ArgumentParser(description="MediaMan!")
    subparsers = parser.add_subparsers(help="command", dest="action")

    add_global_commands(subparsers)
    return parser.parse_args()


def parse_args_subcommand():
    parser = argparse.ArgumentParser(description="MediaMan!")
    subparsers = parser.add_subparsers(help="Backup service options", dest="service")

    subparsers_list = []
    subparsers_list.append(subparsers.add_parser("local", help="The local filesystem"))
    subparsers_list.append(subparsers.add_parser("drive", help="Google drive"))
    for subparser in subparsers_list:
        subsubparsers = subparser.add_subparsers(help="command", dest="action")
        add_service_commands(subsubparsers)

    add_global_commands(subparsers)
    return parser.parse_args()


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
    print(args)

    root = config.load("SAVED_PWD")
    if root is None:
        root = pathlib.Path(".")
    else:
        root = pathlib.Path(root)

    if not args.action:
        raise NotImplementedError()

    if not hasattr(args, "service"):
        raise NotImplementedError()

    service = loader.load(args.service)
    c = client.Client(service)

    action = args.action
    if action == "list":
        print(json.dumps(c.list_files(), indent=4))

    elif action == "put":
        file_paths = args.files
        # TODO: async/thread (failsafe)
        for file_path in file_paths:
            print(c.upload(root / file_path))

    elif action == "get":
        file_paths = args.files
        # TODO: async/thread (failsafe)
        for file_path in file_paths:
            print(c.download(root / file_path))

    else:
        raise NotImplementedError()

    # import code; code.interact(local=locals())


if __name__ == '__main__':
    main()
