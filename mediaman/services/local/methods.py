
import glob
import pathlib

from mediaman import config


# TODO: rename "destination" to "store" or something asymmetrical
LOCAL_DESTINATION = config.load("LOCAL_DESTINATION")


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
    return (data for data in list_files() if data["name"] == file_name)


def exists(file_id):
    return (destination_path() / file_id).exists()


def upload(source_file_path, destination_file_name):
    # TODO: check for overwriting?
    dest = destination_path() / destination_file_name
    with open(source_file_path, "rb") as infile:
        with open(dest, "wb") as outfile:
            outfile.write(infile.read())
    return destination_file_name


def download(source_file_name, destination_file_path):
    # TODO: check for overwriting?
    source_file_path = destination_path() / source_file_name
    with open(source_file_path, "rb") as infile:
        with open(destination_file_path, "wb") as outfile:
            print(source_file_path, destination_file_path)
            outfile.write(infile.read())
    return destination_file_path
