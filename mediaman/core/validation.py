
import string


SHA256_CHARS = frozenset(string.digits + string.ascii_lowercase[:6])


def is_valid_uuid(string, version=4):
    import uuid
    string = str(string)
    try:
        uuid.UUID(string, version=version)
        return True
    except ValueError:
        return False


def is_valid_sha256(string):
    string = str(string)
    return (len(string) == 64) and (set(string) <= SHA256_CHARS)


def parse_human_bytes(human_bytes):
    import re
    units = {"B": 0, "KB": 1, "MB": 2, "GB": 3, "TB": 4}
    human_bytes_regex = r"(?P<cap>[\d\._]+)(\s+)?(?P<unit>\D+)"
    try:
        m = re.match(human_bytes_regex, human_bytes.strip())
        cap = float(m["cap"].replace("_", ""))
        cap *= (1000 ** units[m["unit"]])
        return int(cap)
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(f"Couldn't parse human bytes: {human_bytes}", exc)
