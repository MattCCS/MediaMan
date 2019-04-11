
import os
import yaml


CONFIGURATION_ENV_VAR = "MMCONFIG"
DEFAULT_CONFIGURATION_PATH = "config.yaml"
CONFIGURATION_PATH = os.environ.get(CONFIGURATION_ENV_VAR, DEFAULT_CONFIGURATION_PATH)
CONFIGURATION = None


ERROR_GENERIC_CONFIGURATION_FAILURE = f"""\
There was a generic problem with the config file at '{CONFIGURATION_PATH}'.
Please ensure the file exists, is valid, and includes all required fields.

You can control the config file path by setting the environment variable
'{CONFIGURATION_ENV_VAR}'.  Otherwise, the default path is '{DEFAULT_CONFIGURATION_PATH}'."""


def reload_configuration():
    global CONFIGURATION
    assert CONFIGURATION_PATH
    try:
        with open(CONFIGURATION_PATH) as infile:
            CONFIGURATION = yaml.safe_load(infile)
    except FileNotFoundError as exc:
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
    return CONFIGURATION.get(key, os.environ.get(key, default))


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
    exit(ERROR_GENERIC_CONFIGURATION_FAILURE)
