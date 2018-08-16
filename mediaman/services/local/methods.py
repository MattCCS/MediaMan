
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


def files():
    return (pathlib.Path(path).name for path in glob.glob(f"{destination()}/*"))


def exists(file_id):
    # TODO: pass file_name instead
    return (destination_path() / file_id).exists()


def put(file_id, file_path):
    # TODO: implement
    raise NotImplementedError()


def get(file_id):
    # TODO: implement
    raise NotImplementedError()
    path = pathlib.Path(destination_path() / file_id)
    try:
        stat = path.stat()
    except FileNotFoundError as exc:
        raise  # TODO: raise custom error

    return {
        "filename": file_id,
        "size": stat.st_size,
        "kind": ...,
        "file_extension": path.suffix[1:],
        "checksum": ...,
        "accessedDate": stat.st_atime,
        "modifiedDate": stat.st_mtime,
        "createdDate": stat.st_ctime,
    }
