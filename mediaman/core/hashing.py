
import enum


DELIMITER = ":"


def join(*args):
    return DELIMITER.join(args)


def to_sha256(unlabeled_hash):
    return join(Hash.SHA256.value, unlabeled_hash)


def to_xxh64(unlabeled_hash):
    return join(Hash.XXH64.value, unlabeled_hash)


# def is_sha256(labeled_hash):
#     return labeled_hash.startswith(label) and labeled_hash


class Hash(enum.Enum):
    SHA256 = "sha256"
    XXH64 = "xxh64"


def sha256(path, buffer=8192):
    """
    Hashes the contents of the given filepath in chunks.
    Returns a hex digest (0-9a-f) of the SHA256 hash.
    Performance on a Macbook Pro is about 384 MB/s.
    """
    import hashlib

    sha = hashlib.sha256()

    with open(path, "rb") as infile:
        data = infile.read(buffer)
        while data:
            sha.update(data)
            data = infile.read(buffer)

    return to_sha256(sha.hexdigest())


def xxh64(path, buffer=1024**2):
    """
    Hashes the contents of the given filepath in chunks.
    Returns a hex digest (0-9a-f) of the xxh64 hash.
    Performance on a Macbook Pro is about 4.20 GB/s.
    """
    import xxhash
    import sys

    xxh64 = xxhash.xxh64(seed=0)
    read = 0

    with open(path, "rb") as infile:
        data = infile.read(buffer)
        read += buffer
        while data:
            # sys.stdout.write(f"\rHashed {read / 1024**3:.2f} GiB...")
            # sys.stdout.flush()
            xxh64.update(data)
            data = infile.read(buffer)
            read += buffer

    return to_xxh64(xxh64.hexdigest())


PREFERRED_HASH = Hash.XXH64

HASH_FUNCTIONS = {
    Hash.SHA256: sha256,
    Hash.XXH64: xxh64,
}


def hash(path, preference=None):
    func = HASH_FUNCTIONS[preference or PREFERRED_HASH]
    return func(path)


def is_preferred_hash(labeled_hash):
    start = PREFERRED_HASH.value + DELIMITER
    return labeled_hash.startswith(start)
