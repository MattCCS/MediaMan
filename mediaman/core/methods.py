
import collections
import json

from mediaman.core import validation


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
    for file_list in metadata_map.values():
        for file in file_list:
            file_map[file["hash"]].append(file)

    return file_map


def run_service(root, args, client):
    action = args.action
    if action == "list":
        print(json.dumps(client.list_files(), indent=4))

    elif action == "has":
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
    raise NotImplementedError()

    if validation.is_valid_uuid(name):
        return client.has_by_uuid(name)
    elif validation.is_valid_sha256(name):
        return client.has_by_hash(name)
    else:
        return client.has(name)


def run_service_has_many(root, args, client):
    raise NotImplementedError()
