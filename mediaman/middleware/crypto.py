
import functools
import json
import os
import subprocess
import tempfile

from mediaman import config
from mediaman.core import logtools
from mediaman.core import models
from mediaman.core import settings
from mediaman.middleware import simple

logger = logtools.new_logger("mediaman.middleware.crypto")


def init(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        self.init_metadata()
        return func(self, *args, **kwargs)
    return wrapped


# <openssl> enc -<e/d> -<cipher> -kfile <keypath> -in <inpath> -out <outpath>
CIPHER = "aes-256-cbc"
CRYPTO_KEY_ENV_VAR = "MM_CRYPTO_KEY"
DEFAULT_KEY_PATH = "~/.mediaman/key"

KEYPATH = config.load(CRYPTO_KEY_ENV_VAR, default=DEFAULT_KEY_PATH)

OPENSSL_PREFERRED_BINS = [
    "/usr/local/Cellar/libressl/2.9.2/bin",
    "/usr/bin",
]

ERROR_MULTIPLE_REMOTE_FILES = "\
[!] Multiple crypt files found for service ({})!  \
This must be resolved manually.  Exiting..."


def form_path_prepend():
    global OPENSSL_PREFERRED_BINS
    return ":".join(OPENSSL_PREFERRED_BINS + [config.load_safe("PATH")])


def form_subprocess_environ():
    new_env = os.environ.copy()
    new_env["PATH"] = form_path_prepend()
    return new_env


def create_metadata():
    return {
        "version": settings.VERSION,
        "ciphers": {},
    }


class EncryptionMiddlewareService(simple.SimpleMiddleware):

    MIDDLEWARE_FILENAME = "crypt"

    def __init__(self, service):
        super().__init__(service)
        logger.debug(f"EncryptionMiddlewareService init for {service}")

        self.metadata = None

    def init_metadata(self):
        if self.metadata is not None:
            return
        self.metadata = create_metadata()

        # TODO: implement
        file_list = self.service.search_by_name(EncryptionMiddlewareService.MIDDLEWARE_FILENAME)
        files = file_list.results()

        if len(files) > 1:
            raise RuntimeError(ERROR_MULTIPLE_REMOTE_FILES.format(self.service))

        if not files:
            self.update_metadata()
        else:
            self.load_metadata(files[0])

    def update_metadata(self):
        with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
            tempfile_ref.write(json.dumps(self.metadata))
            tempfile_ref.seek(0)

            request = models.Request(
                id=EncryptionMiddlewareService.MIDDLEWARE_FILENAME,
                path=tempfile_ref.name,
            )
            receipt = self.service.upload(request)

        logger.debug(f"update_metadata receipt: {receipt}")
        self.index_id = receipt.id()

    def load_metadata_json(self, index):
        logger.debug(f"load_metadata_json index: {index}")
        self.index_id = index.id()

        with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
            request = models.Request(
                id=self.index_id,
                path=tempfile_ref.name,
            )

            self.service.download(request)
            tempfile_ref.seek(0)

            return json.loads(tempfile_ref.read())

    def load_metadata(self, index):
        self.metadata = self.load_metadata_json(index)
        logger.debug(f"Loaded metadata: {self.metadata}")

        if "version" not in self.metadata:
            logger.critical(f"'version' field missing from metadata!  This is an outdated or unversioned meta file.  You will need to fix it by running `mm <service> refresh`.")
            raise RuntimeError("Unversioned metadata")

        version = self.metadata["version"]
        if version > settings.VERSION:
            logger.critical(f"Metadata version ({version}) exceeds software version ({settings.VERSION}).  You need to update your software to parse this index file.")
            raise RuntimeError("Outdated software")

        if version < settings.VERSION:
            logger.critical(f"Metadata version ({version}) is below software version ({settings.VERSION}).  You need to update it by running `mm <service> refresh`.")
            raise RuntimeError("Outdated metadata")

    def encrypt(self, request):
        global CIPHER, KEYPATH

        tempfile_ref = tempfile.NamedTemporaryFile(mode="wb+", delete=True)

        args = [
            "openssl", "enc", "-e", f"-{CIPHER}",
            "-kfile", KEYPATH,
            "-in", request.path,
            "-out", tempfile_ref.name,
        ]
        logger.debug(f"encrypting: {args}")

        subprocess.check_output(args, stderr=subprocess.PIPE, env=form_subprocess_environ())

        tempfile_ref.seek(0)
        return tempfile_ref

    def decrypt(self, source, destination):
        global CIPHER, KEYPATH

        args = [
            "openssl", "enc", "-d", f"-{CIPHER}",
            "-kfile", KEYPATH,
            "-in", source,
            "-out", destination,
        ]
        logger.debug(f"decrypting: {args}")

        subprocess.check_output(args, stderr=subprocess.PIPE, env=form_subprocess_environ())

    def track_cipher(self, key):
        global CIPHER
        if key not in self.metadata["ciphers"]:
            self.metadata["ciphers"][key] = {}
        self.metadata["ciphers"][key] = CIPHER

    def upload(self, request):
        print(request)
        self.track_cipher(request.id)
        print(self.metadata)
        exit()

        raise NotImplementedError()
        # with self.encrypt(request.path) as encrypted_tempfile:
        #     request.path = encrypted_tempfile.name
        #     receipt = self.service.upload(request)

    def download(self, request):
        if request.id not in self.metadata["ciphers"]:
            return self.service.download(request)

        with tempfile.NamedTemporaryFile("wb+", delete=True) as tempfile_ref:
            temp_request = models.Request(
                id=request.id,
                path=tempfile_ref.name,
            )

            receipt = self.service.download(temp_request)
            tempfile_ref.seek(0)

            self.decrypt(tempfile_ref.name, request.path)

        return receipt
