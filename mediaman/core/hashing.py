
import hashlib


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

    return sha.hexdigest()
