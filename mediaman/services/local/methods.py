
import glob
import os
import pathlib
import shutil

from mediaman import config


# TODO: rename "destination" to "store" or something asymmetrical
LOCAL_DESTINATION = config.load("LOCAL_DESTINATION")
LOCAL_QUOTA = config.load_quota("LOCAL_QUOTA")


def folder_size(path):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += folder_size(entry.path)
    return total


def destination_path():
    assert LOCAL_DESTINATION
    path = pathlib.Path(LOCAL_DESTINATION)
    assert path.exists()
    return path


def destination():
    return str(destination_path())


def extractor(path):
    return {
        "name": path.name,
        "suffix": path.suffix,
        "stat": path.stat(),
    }


def list_files():
    return map(
        extractor,
        (pathlib.Path(path) for path in glob.glob(f"{destination()}/*"))
    )


def list_file(file_id):
    path = pathlib.Path(destination_path() / file_id)
    if not path.exists():
        raise FileNotFoundError()  # TODO: raise custom error

    return extractor(path)


def search_by_name(file_name):
    out = (data for data in list_files() if data["name"] == file_name)
    return out


def exists(file_id):
    return (destination_path() / file_id).exists()


def upload(request):
    # TODO: check for overwriting?
    dest = destination_path() / request.id
    with open(request.path, "rb") as infile:
        with open(dest, "wb") as outfile:
            outfile.write(infile.read())
    return request.id


def download(request):
    # TODO: check for overwriting?
    source_file_path = destination_path() / request.id
    with open(source_file_path, "rb") as infile:
        with open(request.path, "wb") as outfile:
            outfile.write(infile.read())
    return request.path


def capacity():
    disk_usage = shutil.disk_usage(LOCAL_DESTINATION)
    used = folder_size(LOCAL_DESTINATION)
    return {"used": used, "quota": LOCAL_QUOTA, "total": disk_usage.total}
