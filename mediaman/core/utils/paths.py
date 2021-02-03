
import pathlib
import traceback

from mediaman import logtools

logger = logtools.new_logger("mediaman.core.utils.paths")


def resolve_abs_path(root, file_id):
    path = pathlib.Path(file_id)

    if not path.is_absolute():
        path = root / path
    assert path.is_absolute()

    if path.is_dir():
        raise IsADirectoryError()

    if not path.exists():
        raise FileNotFoundError()

    return path


def resolve_abs_paths(root, file_ids):
    for file_id in file_ids:
        try:
            yield resolve_abs_path(root, file_id)
        except (IsADirectoryError, FileNotFoundError) as exc:
            logger.debug(f"{traceback.format_exc()}: {file_id}")
