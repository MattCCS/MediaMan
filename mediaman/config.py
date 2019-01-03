
import os
import yaml


DEFAULT_CONFIGURATION_PATH = "config.yaml"
CONFIGURATION_PATH = os.environ.get("CONFIG", DEFAULT_CONFIGURATION_PATH)
CONFIGURATION = None


def reload_configuration():
    global CONFIGURATION
    assert CONFIGURATION_PATH
    with open(CONFIGURATION_PATH) as infile:
        CONFIGURATION = yaml.safe_load(infile)


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
