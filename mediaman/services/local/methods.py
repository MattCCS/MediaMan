
import glob
import pathlib

from mediaman import config


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


def files():
    return map(
        extractor,
        (pathlib.Path(path) for path in glob.glob(f"{destination()}/*"))
    )


def exists(file_id):
    return (destination_path() / file_id).exists()


def put(source_file_path, destination_file_name):
    # TODO: check for overwriting?
    dest = destination_path() / destination_file_name
    with open(source_file_path, "rb") as infile:
        with open(dest, "wb") as outfile:
            outfile.write(infile.read())
    return destination_file_name


def get(file_id):
    path = pathlib.Path(destination_path() / file_id)
    if not path.exists():
        raise FileNotFoundError()  # TODO: raise custom error

    return extractor(path)
