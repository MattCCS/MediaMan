
import os
import re
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


def load_quota(key, default=None):
    human_quota = load(key)
    return parse_human_bytes(human_quota) if human_quota else human_quota


def parse_human_bytes(human_bytes):
    units = {"B": 0, "KB": 1, "MB": 2, "GB": 3, "TB": 4}
    human_bytes_regex = r"(?P<cap>[\d\._]+)(\s+)?(?P<unit>\D+)"
    try:
        m = re.match(human_bytes_regex, human_bytes.strip())
        cap = float(m["cap"].replace("_", ""))
        cap *= (1024 ** units[m["unit"]])
        return int(cap)
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(f"Couldn't parse human bytes: {human_bytes}", exc)
