
import os
import pathlib
import shutil
import sys

import yaml


ROOT_ENV_VAR = "MMROOT"
DEFAULT_ROOT_NAME = ".mediaman"
DEFAULT_ROOT_PATH = pathlib.Path.home() / DEFAULT_ROOT_NAME
ROOT_PATH = pathlib.Path(os.environ.get(ROOT_ENV_VAR, DEFAULT_ROOT_PATH)).expanduser()

CONFIGURATION_ENV_VAR = "MMCONFIG"
DEFAULT_CONFIGURATION_NAME = "config.yaml"
DEFAULT_CONFIGURATION_PATH = ROOT_PATH / DEFAULT_CONFIGURATION_NAME
CONFIGURATION_PATH = pathlib.Path(os.environ.get(CONFIGURATION_ENV_VAR, DEFAULT_CONFIGURATION_PATH)).expanduser()
CONFIGURATION = None

EDITOR_ENV_VAR = "EDITOR"
DEFAULT_EDITOR_NAME = "nano"
EDITOR_NAME = os.environ.get(EDITOR_ENV_VAR, DEFAULT_EDITOR_NAME)


ERROR_GENERIC_CONFIGURATION_FAILURE = f"""\
There was a generic problem with the config file at '{CONFIGURATION_PATH}'.
Please ensure the file exists, is valid, and includes all required fields.

You can control the config file path by setting the environment variable
'{CONFIGURATION_ENV_VAR}'.  Otherwise, the default path is '{DEFAULT_CONFIGURATION_PATH}'."""


def configuration_exists():
    return pathlib.Path(CONFIGURATION_PATH).is_file()


def reload_configuration():
    global CONFIGURATION
    assert CONFIGURATION_PATH
    try:
        with open(CONFIGURATION_PATH) as infile:
            CONFIGURATION = yaml.safe_load(infile)
    except FileNotFoundError:
        import traceback
        print(traceback.format_exc())
        exit_with_generic_warning()


def ensure_configuration():
    if not CONFIGURATION:
        reload_configuration()


def load(key, default=None):
    """
    Loads the given key from the preset configuration YAML file.

    Falls back to os.environ if no results found.
    Returns `default` (default None) if key not present.
    """
    ensure_configuration()
    try:
        return CONFIGURATION.get(key, os.environ.get(key, default))
    except AttributeError as exc:
        raise Exception(ERROR_GENERIC_CONFIGURATION_FAILURE) from exc


def load_safe(key):
    ensure_configuration()
    try:
        return CONFIGURATION[key]
    except KeyError:
        try:
            return os.environ[key]
        except KeyError:
            print(f"Failed to load `{key}` from your config file!\n")
    exit_with_generic_warning()


def exit_with_generic_warning():
    sys.exit(ERROR_GENERIC_CONFIGURATION_FAILURE)


def launch_editor():
    import subprocess

    if not configuration_exists():
        print(f"[!] No file was found at the path '{CONFIGURATION_PATH}'")
        print(f"    Make sure that your config file environment variable "
              f"('{CONFIGURATION_ENV_VAR}') is correct first.")
        print(f"[?] Would like to create a new config file?")
        consent = input(f"    [Y/n] ")

        if consent != "Y":
            print()
            exit_with_generic_warning()

        print(f"[?] Would you like the file to be [B]lank, or to start from a [T]emplate?")
        choice = input(f"    [B/T/n] ")

        if choice == "B":
            pathlib.Path(CONFIGURATION_PATH).touch(mode=0o600, exist_ok=True)
        elif choice == "T":
            shutil.copy("config.yaml.sample", CONFIGURATION_PATH)
        else:
            print()
            exit_with_generic_warning()

    subprocess.call([EDITOR_NAME, CONFIGURATION_PATH], shell=False)
