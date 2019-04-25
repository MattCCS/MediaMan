
def repair_metadata(metadata_json):
    # unversioned
    if "version" not in metadata_json:
        metadata_json = update_metadata_to_0(metadata_json)

    return metadata_json


def update_metadata_to_0(metadata_json):
    assert isinstance(metadata_json, dict)
    return {
        "version": 0,
        "files": metadata_json,
    }
