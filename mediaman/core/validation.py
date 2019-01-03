
import string
import uuid


SHA256_CHARS = frozenset(string.digits + string.ascii_lowercase[:6])


def is_valid_uuid(string, version=4):
    try:
        uuid.UUID(string, version=version)
        return True
    except ValueError:
        return False


def is_valid_sha256(string):
    return (len(string) == 64) and (set(string) <= SHA256_CHARS)
