
import os
import yaml


CONFIGURATION_PATH = os.environ.get("CONFIG", None)
CONFIGURATION = None


def reload_configuration():
    global CONFIGURATION
    assert CONFIGURATION_PATH
    with open(CONFIGURATION_PATH) as infile:
        CONFIGURATION = yaml.safe_load(infile)


def ensure_configuration():
    if not CONFIGURATION:
        reload_configuration()


def load(key):
    """
    Loads the given key from the preset configuration YAML file.
    Falls back to os.environ if no results found.
    """
    ensure_configuration()
    return CONFIGURATION.get(key, os.environ.get(key, None))
