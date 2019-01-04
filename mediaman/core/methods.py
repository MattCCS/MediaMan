
from mediaman.core import validation


def run_service_has_one(root, args, client):
    name = args.files[0]
    # raise NotImplementedError()

    if validation.is_valid_uuid(name):
        return client.has_by_uuid(name)
    elif validation.is_valid_sha256(name):
        return client.has_by_hash(name)
    else:
        return client.search_by_name(name)
