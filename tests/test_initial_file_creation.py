"""
TO TEST:
- can list/search/hashsearch/cap/...
    - mlist is created
- can upload file
    - mlist is created OR updated
    - index is created
    - file is created
- can download file
    - files unchanged
    - download matches
- can delete file
    - file is deleted
    - index is deleted
    - mlist is updated

- encryption ON/OFF
"""

import contextlib
import importlib
import json
import logging
import os
import pathlib
import sys
import tempfile
from types import SimpleNamespace

import pytest

os.environ["MMCONFIG"] = "/dev/null"
os.environ["MM_USE_REDIS"] = "0"

import mediaman.core.api


EMPTY_XX_HASH = "xxh64:ef46db3751d8e999"


def file_is_encrypted(filepath):
    with open(filepath, "rb") as infile:
        data = infile.read(8)
    assert data == b"Salted__"
    return True


def file_is_not_encrypted(filepath):
    with open(filepath, "rb") as infile:
        data = infile.read(8)
    assert data != b"Salted__"
    return True


@contextlib.contextmanager
def logger_at_level(logger, level):
    prev_level = logger.level
    logger.setLevel(level)
    yield
    logger.setLevel(prev_level)


def debug_logging(logger):
    return logger_at_level(logger, logging.DEBUG)


@pytest.fixture(autouse=True)
def reset_configuration():
    import mediaman.config
    import mediaman.core.policy
    mediaman.config.CONFIGURATION = None
    mediaman.core.policy.POLICY = None


@pytest.fixture()
def valid_config():
    stub = SimpleNamespace()
    with tempfile.TemporaryDirectory() as sandbox:
        sandbox_dir = pathlib.Path(sandbox)
        (valid_config_file := sandbox_dir / "valid_config").touch()
        (mediaman_dir := sandbox_dir / "MediaMan").mkdir()

        with open(valid_config_file, "w") as outfile:
            outfile.write(f"""
                services:
                  test:
                    type: folder
                    quota: 1GB
                    destination: {str(mediaman_dir)}
            """)

        mediaman.config.CONFIGURATION_PATH = valid_config_file

        stub.sandbox_dir = sandbox_dir
        stub.config = valid_config_file
        stub.mediaman_dir = mediaman_dir

        yield stub


def prepare_mm_without_any_files(valid_config):
    service_names = list(mediaman.core.api.get_service_names())
    assert service_names == ["all", "test"]

    # Assert no files exist
    mm = valid_config.mediaman_dir
    files_in_root = [p.name for p in mm.glob("*")]
    assert files_in_root == []

    return True


def prepare_mm_with_mlist_file_only(valid_config):
    prepare_mm_without_any_files(valid_config)

    files = list(mediaman.core.api.run_list())
    assert files == []

    mm = valid_config.mediaman_dir
    assert mm.exists() and mm.is_dir()

    # Assert mlist exists
    mlist = mm / "mlist"
    assert mlist.exists() and mlist.is_file()

    # Assert mlist contains 0 indices
    with open(mlist, "r") as infile:
        assert infile.read() == '{"version": 5, "data": {"indices": []}}'

    # Assert only 1 file exists: mlist
    files_in_root = [p.name for p in mm.glob("*")]
    assert files_in_root == ["mlist"]

    return True


def prepare_mm_with_one_file(caplog, valid_config):
    prepare_mm_with_mlist_file_only(valid_config)

    mm = valid_config.mediaman_dir
    assert mm.exists() and mm.is_dir()

    # Create empty file called file_1
    (file_1 := valid_config.sandbox_dir / "file_1").touch()

    # Asssert file can be `put`
    with debug_logging(logging.getLogger()):
        responses = list(mediaman.core.api.run_put("/", file_1, service_selector="test"))
    assert "FileNotFoundError" not in caplog.text

    # Assert correct name, size, and hash were saved
    (path, entry) = responses[0]
    assert path == file_1
    assert entry["name"] == "file_1"
    assert entry["size"] == 0
    assert entry["hashes"] == [EMPTY_XX_HASH]
    assert entry["tags"] == []
    assert entry["encryption"] == {"cipher": "aes-256-cbc", "digest": "sha256"}
    file_1_sid = entry["sid"]

    # Assert file can be `stream`ed and contents are correct
    data = b"".join(mediaman.core.api.run_stream(pathlib.Path("/"), "file_1"))
    assert data == b""

    # Assert file can be `list`ed
    files_response = list(mediaman.core.api.run_list())
    assert len(files_response) == 1
    assert files_response[0].client.nickname() == "test"
    assert files_response[0].response == [entry]

    # Assert mlist exists
    mlist = mm / "mlist"
    assert mlist.exists() and mlist.is_file()

    # Assert mlist contains 1 index
    with open(mlist, "r") as infile:
        mlist_data = json.loads(infile.read())
        assert mlist_data["version"] == 5

        indices = mlist_data["data"]["indices"]
        assert len(indices) == 1

        assert indices[0]["encryption"] == {"cipher": "aes-256-cbc", "digest": "sha256"}
        index_sid = indices[0]["sid"]

    # Assert only 3 files exist: mlist, index, file_1
    files_in_root = set(p.name for p in mm.glob("*"))
    assert len(files_in_root) == 3
    assert files_in_root == {"mlist", index_sid, file_1_sid}

    # Assert index is encrypted
    assert file_is_encrypted(mm / index_sid)

    # Assert file_1 is encrypted
    assert file_is_encrypted(mm / file_1_sid)

    return True


def test_prepare_mm_without_any_files(valid_config):
    assert True is prepare_mm_without_any_files(valid_config)


def test_prepare_mm_with_mlist_file_only(valid_config):
    assert True is prepare_mm_with_mlist_file_only(valid_config)


def test_prepare_mm_with_one_file(caplog, valid_config):
    assert True is prepare_mm_with_one_file(caplog, valid_config)
