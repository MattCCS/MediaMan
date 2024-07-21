
import importlib
import os
import pathlib
import sys
import tempfile
from types import SimpleNamespace

import pytest

os.environ["MMCONFIG"] = "/dev/null"
os.environ["MM_USE_REDIS"] = "0"

import mediaman.core.api


@pytest.fixture(autouse=True)
def reset_configuration():
    import mediaman.config
    import mediaman.core.policy
    mediaman.config.CONFIGURATION = None
    mediaman.core.policy.POLICY = None


@pytest.fixture()
def no_config():
    stub = SimpleNamespace()
    with tempfile.TemporaryDirectory() as sandbox:
        sandbox_dir = pathlib.Path(sandbox)
        no_config_file = sandbox_dir / "no_config"

        mediaman.config.CONFIGURATION_PATH = no_config_file

        stub.sandbox_dir = sandbox_dir
        stub.config = no_config_file

        yield stub


@pytest.fixture()
def empty_config():
    stub = SimpleNamespace()
    with tempfile.TemporaryDirectory() as sandbox:
        sandbox_dir = pathlib.Path(sandbox)
        (empty_config_file := sandbox_dir / "empty_config").touch()

        mediaman.config.CONFIGURATION_PATH = empty_config_file

        stub.sandbox_dir = sandbox_dir
        stub.config = empty_config_file

        yield stub


@pytest.fixture()
def invalid_config():
    stub = SimpleNamespace()
    with tempfile.TemporaryDirectory() as sandbox:
        sandbox_dir = pathlib.Path(sandbox)
        (invalid_config_file := sandbox_dir / "invalid_config").touch()

        with open(invalid_config_file, "w") as outfile:
            outfile.write("adfgadfhdjk")

        mediaman.config.CONFIGURATION_PATH = invalid_config_file

        stub.sandbox_dir = sandbox_dir
        stub.config = invalid_config_file

        yield stub


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


def test_no_config_works_but_returns_no_services(caplog, no_config):
    assert mediaman.core.api.get_service_names() == []
    assert caplog.text == ""


def test_empty_config_works_but_returns_no_services_and_logs_error(caplog, empty_config):
    assert mediaman.core.api.get_service_names() == []
    assert "KeyError: 'MM_SERVICES'" in caplog.text


def test_invalid_config_works_but_returns_no_services_and_logs_error(caplog, invalid_config):
    assert mediaman.core.api.get_service_names() == []
    assert "KeyError: 'MM_SERVICES'" in caplog.text


def test_valid_config_works_and_returns_services(caplog, valid_config):
    assert mediaman.core.api.get_service_names() == ["all", "test"]
    assert caplog.text == ""
