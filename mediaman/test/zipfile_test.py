
import pathlib
import zipfile

from mediaman.core import api


class ReadableFileLikeStream:
    def __init__(self, hash, service, size):
        self._hash = hash
        self._service = service
        self._size = size
        self._seek = 0

    def seekable(self):
        return True

    def seek(self, offset, whence=0):
        print(f"seek: offset={offset}, whence={whence}")
        if whence == 0:
            self._seek = offset
        elif whence == 1:
            self._seek = self._seek + offset
        elif whence == 2:
            self._seek = self._size + offset
        else:
            raise RuntimeError(f"invalid value for whence: {repr(whence)}")
        print(f"\tseek: new seek={self._seek}")

    def tell(self):
        print(f"tell")
        out = self._seek
        print(f"\ttell: out={out}")
        return out

    def read(self, length=0):
        print(f"read: length={length}")
        if not length:
            length = self._size - self._seek

        out = b''.join(
            api.run_stream_range(
                pathlib.Path(),
                self._hash,
                self._seek,
                length,
                service_selector=self._service
            )
        )
        self._seek = min(self._seek + length, self._size)
        print(f"\tread: len(out)={len(out)}, new seek={self._seek}")
        return out


class ZipStream(ReadableFileLikeStream):
    def __init__(self, *args, **kwargs):
        super(ZipStream).__init__(*args, **kwargs)
        self._cache_end()

    def cache_end(self):
        self.seek(1_000_000, whence=2)
        self.read()


# hash = "xxh64:743b568919972e91"; service = "local"  # noqa  # Harry Potter
# hash = "xxh64:7751b329b75f1b03"; service = "drive"  # noqa  # Old iPod Sorted
# hash = "xxh64:818f4e99c81d7d4a"; service = "drive"  # noqa # Denmark
hash = "xxh64:362c848f5c35d7ca"; service = "drive"  # noqa # Sea Sides V2

FILES = api.run_list(service_selector=service)
size = [f for f in FILES if hash in f["hashes"]][0]["size"]
print(hash, service, size)

stream = ReadableFileLikeStream(hash, service, size)

z = zipfile.ZipFile(stream)
