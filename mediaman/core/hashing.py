
import enum
import hashlib


DELIMITER = ":"


def join(*args):
    return DELIMITER.join(args)


def to_sha256(unlabeled_hash):
    return join(Hash.SHA256.value, unlabeled_hash)


# def is_sha256(labeled_hash):
#     return labeled_hash.startswith(label) and labeled_hash


class Hash(enum.Enum):
    SHA256 = "sha256"


def hash(path, buffer=8192):
    """
    Hashes the contents of the given filepath in chunks.
    Returns a hex digest (0-9a-f) of the SHA256 hash.
    Performance on a Macbook Pro is about 384 MB/s.
    """

    sha = hashlib.sha256()

    with open(path, "rb") as infile:
        data = infile.read(buffer)
        while data:
            sha.update(data)
            data = infile.read(buffer)

    return to_sha256(sha.hexdigest())


# def hash(path):
#     import subprocess
#     return subprocess.check_output(["xxhsum", str(path)])
