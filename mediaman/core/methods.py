
import collections
import json

from mediaman.core import validation
from mediaman.core import watertable


def run_global(root, args, clients):
    action = args.action
    if action == "list":
        print(json.dumps(run_global_list(root, args, clients), indent=4))
    else:
        raise NotImplementedError()


def run_global_list(root, args, clients):
    metadata_map = {}

    for client in clients:
        # TODO: allow specific files
        metadata_map[client] = client.list_files()

    file_map = collections.defaultdict(list)
    for (client, file_list) in metadata_map.items():
        for file in file_list:
            file["client"] = client
            file_map[file["hash"]].append(file)

    def copy_gen():
        nonlocal file_map
        for (hash, files) in file_map.items():
            for f in files:
                yield (hash, f["name"], f["id"], f["sid"])
                hash = ""

    columns = (("hash", 20), ("name", 50), ("id", 24), ("sid", 24))
    iterable = copy_gen()
    gen = watertable.table_stream(columns, iterable)
    for row in gen:
        print(row)

    return


def run_service(root, args, client):
    action = args.action
    if action == "has":
        return run_service_has(root, args, client)

    elif action == "put":
        file_paths = args.files
        # TODO: async/thread (failsafe)
        for file_path in file_paths:
            print(client.upload(root / file_path))

    elif action == "get":
        file_paths = args.files
        # TODO: async/thread (failsafe)
        for file_path in file_paths:
            print(client.download(root / file_path))

    else:
        raise NotImplementedError()


def run_service_has(root, args, client):
    if len(args.files) == 1:
        return run_service_has_one(root, args, client)
    return run_service_has_many(root, args, client)


def run_service_has_one(root, args, client):
    name = args.files[0]
    # raise NotImplementedError()

    if validation.is_valid_uuid(name):
        return client.has_by_uuid(name)
    elif validation.is_valid_sha256(name):
        return client.has_by_hash(name)
    else:
        return client.search_by_name(name)


def run_service_has_many(root, args, client):
    raise NotImplementedError()


def run_multi_has(client, root, *files):
    if len(files) == 1:
        return run_multi_has_one(client, root, files[0])
    else:
        raise NotImplementedError()


def run_multi_has_one(client, root, file):
    return client.search_by_name(file)


# def run_multi_get(client, root, *files):
#     if len(files) == 1:
#         return run_multi_get_one(client, root, files[0])
#     else:
#         raise NotImplementedError()


# def run_multi_get_one(client, root, file):
#     return client.get(file)
