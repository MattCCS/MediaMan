
from mediaman.core import hashing
from mediaman.core import settings


VERSION_KEY = "version"


def repair_metadata(metadata_json):
    # unversioned
    if VERSION_KEY not in metadata_json:
        metadata_json = update_metadata_to_0(metadata_json)

    assert metadata_json[VERSION_KEY] <= settings.VERSION

    if metadata_json[VERSION_KEY] == 0:
        metadata_json = update_metadata_0_to_1(metadata_json)

    if metadata_json[VERSION_KEY] == 1:
        metadata_json = update_metadata_1_to_2(metadata_json)

    if metadata_json[VERSION_KEY] == 2:
        metadata_json = update_metadata_2_to_3(metadata_json)

    assert metadata_json[VERSION_KEY] == settings.VERSION
    return metadata_json


def update_metadata_to_0(metadata_json):
    assert isinstance(metadata_json, dict)
    return {
        VERSION_KEY: 0,
        "files": metadata_json,
    }


def update_metadata_0_to_1(metadata_json):
    assert metadata_json[VERSION_KEY] == 0

    files = metadata_json["files"]
    for file in files.values():
        hash = hashing.to_sha256(file["hash"])
        file["hashes"] = [hash]
        del file["hash"]

    return {
        VERSION_KEY: 1,
        "files": files,
    }


def update_metadata_1_to_2(metadata_json):
    assert metadata_json[VERSION_KEY] == 1

    files = metadata_json["files"]
    for file in files.values():
        assert "merged_hashes" not in file
        file["merged_hashes"] = []

    return {
        VERSION_KEY: 2,
        "files": files,
    }


def update_metadata_2_to_3(metadata_json):
    assert metadata_json[VERSION_KEY] == 2

    files = metadata_json["files"]
    for file in files.values():
        assert "tags" not in file
        file["tags"] = []

    return {
        VERSION_KEY: 3,
        "files": files,
    }
