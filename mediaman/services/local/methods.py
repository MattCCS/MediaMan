
import glob
import os
import pathlib
import shutil

from mediaman import logtools

logger = logtools.new_logger("mediaman.services.local.methods")


WRITE_BUFFER = 1_000_000


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
    assert path.is_absolute()
    return path


def extractor(path):
    return {
        "name": path.name,
        "suffix": path.suffix,
        "stat": path.stat(),
    }


def list_files(destination_path):
    logger.debug(f"listing files in {repr(destination_path)}")
    files = list(map(
        extractor,
        (pathlib.Path(path) for path in glob.glob(f"{str(destination_path)}/*"))
    ))
    logger.trace(f"files = {files}")
    logger.debug(f"files: {len(files)}")
    return files


def list_file(destination_path, file_id):
    path = pathlib.Path(destination_path / file_id)
    if not path.exists():
        raise FileNotFoundError()  # TODO: raise custom error

    return extractor(path)


def search_by_name(destination_path, file_name):
    logger.debug(f"searching for {repr(file_name)} in {repr(destination_path)}")
    out = (data for data in list_files(destination_path) if data["name"] == file_name)
    out = list(out)
    logger.debug(f"out = {out}")
    return out


def exists(destination_path, file_id):
    return (destination_path / file_id).exists()


def upload(destination_path, request):
    # TODO: check for overwriting?
    dest = destination_path / request.id
    written = 0
    with open(request.path, "rb") as infile:
        with open(dest, "wb") as outfile:
            data = infile.read(WRITE_BUFFER)
            while data:
                outfile.write(data)
                written += len(data)
                logger.info(f"Wrote {written / 1_000_000:.2f} MB...")
                data = infile.read(WRITE_BUFFER)
    return {
        "id": request.id,
    }


def download(destination_path, request):
    # TODO: check for overwriting?
    source_file_path = destination_path / request.id
    written = 0
    with open(source_file_path, "rb") as infile:
        with open(request.path, "wb") as outfile:
            data = infile.read(WRITE_BUFFER)
            while data:
                outfile.write(data)
                written += len(data)
                logger.info(f"Wrote {written / 1_000_000:.2f} MB...")
                data = infile.read(WRITE_BUFFER)
    return {
        "id": request.id,
        "path": request.path,
    }


def stream(destination_path, request):
    source_file_path = destination_path / request.id
    written = 0
    with open(source_file_path, "rb") as infile:
        data = infile.read(WRITE_BUFFER)
        while data:
            yield data
            written += len(data)
            logger.info(f"Wrote {written / 1_000_000:.2f} MB...")
            data = infile.read(WRITE_BUFFER)


def stream_range(destination_path, request, offset, length):
    source_file_path = destination_path / request.id
    with open(source_file_path, "rb") as infile:
        infile.seek(offset)
        data = infile.read(WRITE_BUFFER)
        while data:
            data = data[:length]
            yield data
            length -= len(data)
            if not length:
                break
            data = infile.read(WRITE_BUFFER)


def capacity(destination_path, quota):
    disk_usage = shutil.disk_usage(destination_path)
    used = folder_size(destination_path)
    return {"used": used, "quota": quota, "total": disk_usage.total}


def remove(destination_path, file_id):
    path = pathlib.Path(destination_path / file_id)
    logger.debug(f"Removing file at '{path}' ...")

    assert path.is_absolute()
    if not path.exists():
        raise FileNotFoundError()  # TODO: raise custom error

    os.remove(path)
    return {
        "id": file_id,
    }
