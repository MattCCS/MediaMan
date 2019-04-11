
import glob
import os
import pathlib
import shutil


def folder_size(path):
    total = 0
    for entry in os.scandir(path):
        if entry.is_file():
            total += entry.stat().st_size
        elif entry.is_dir():
            total += folder_size(entry.path)
    return total


def require_destination_path(destination):
    assert destination
    path = pathlib.Path(destination)
    assert path.exists()
    return path


def extractor(path):
    return {
        "name": path.name,
        "suffix": path.suffix,
        "stat": path.stat(),
    }


def list_files(destination_path):
    return map(
        extractor,
        (pathlib.Path(path) for path in glob.glob(f"{str(destination_path)}/*"))
    )


def list_file(destination_path, file_id):
    path = pathlib.Path(destination_path / file_id)
    if not path.exists():
        raise FileNotFoundError()  # TODO: raise custom error

    return extractor(path)


def search_by_name(destination_path, file_name):
    out = (data for data in list_files(destination_path) if data["name"] == file_name)
    return out


def exists(destination_path, file_id):
    return (destination_path / file_id).exists()


def upload(destination_path, request):
    # TODO: check for overwriting?
    dest = destination_path / request.id
    with open(request.path, "rb") as infile:
        with open(dest, "wb") as outfile:
            outfile.write(infile.read())
    return request.id


def download(destination_path, request):
    # TODO: check for overwriting?
    source_file_path = destination_path / request.id
    with open(source_file_path, "rb") as infile:
        with open(request.path, "wb") as outfile:
            outfile.write(infile.read())
    return request.path


def capacity(destination_path, quota):
    disk_usage = shutil.disk_usage(destination_path)
    used = folder_size(destination_path)
    return {"used": used, "quota": quota, "total": disk_usage.total}
