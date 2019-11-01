
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


# <openssl> enc -<e/d> -<cipher> -kfile <keypath> -md <digest> -in <inpath> -out <outpath>
DEFAULT_CIPHER = "aes-256-cbc"
DEFAULT_DIGEST = "sha256"
CRYPTO_KEY_ENV_VAR = "MM_CRYPTO_KEY"
DEFAULT_KEY_PATH = os.path.expanduser("~/.mediaman/key")

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


def encrypt(request, keypath, cipher, digest):
    tempfile_ref = tempfile.NamedTemporaryFile(mode="wb+", delete=True)

    args = [
        "openssl", "enc", "-e",
        "-in", str(request.path),
        "-out", str(tempfile_ref.name),
        "-kfile", keypath, f"-{cipher}", "-md", digest,
    ]
    logger.info(f"encrypting: {args}")

    logger.info(f"Encrypting file...")
    subprocess.check_output(args, stderr=subprocess.PIPE, env=form_subprocess_environ())

    tempfile_ref.seek(0)
    return tempfile_ref


def decrypt(source, destination, keypath, cipher, digest):
    args = [
        "openssl", "enc", "-d",
        "-in", str(source),
        "-out", str(destination),
        "-kfile", keypath, f"-{cipher}", "-md", digest,
    ]
    logger.info(f"decrypting: {args}")

    logger.info(f"Decrypting file...")
    try:
        subprocess.check_output(args, stderr=subprocess.PIPE, env=form_subprocess_environ())
    except subprocess.CalledProcessError as exc:
        err_text = exc.stderr.decode("utf-8")

        logger.debug(exc)
        if err_text.startswith("bad decrypt"):
            logger.fatal(f"Decryption failed -- encryption key is incorrect.")
        else:
            logger.fatal(f"Decryption failed -- generic error: {err_text}")

        raise


def create_metadata(data=None):
    if data is None:
        data = {}

    return {
        "version": settings.VERSION,
        "data": data,
    }


class EncryptionMiddlewareService(simple.SimpleMiddleware):

    MIDDLEWARE_FILENAME = "crypt"

    def __init__(self, service):
        super().__init__(service)
        logger.info(f"EncryptionMiddlewareService init for {service}")

        self.metadata_id = None
        self.metadata = None

    def init_metadata(self):
        if self.metadata is not None:
            return

        # TODO: implement
        file_list = self.service.search_by_name(EncryptionMiddlewareService.MIDDLEWARE_FILENAME)
        files = file_list.results()

        if len(files) > 1:
            raise RuntimeError(ERROR_MULTIPLE_REMOTE_FILES.format(self.service))

        if not files:
            self.metadata = create_metadata()
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

        logger.info(f"update_metadata receipt: {receipt}")
        self.metadata_id = receipt.id()

    def load_metadata_json(self, metadata_file):
        logger.info(f"load_metadata_json file: {metadata_file}")
        self.metadata_id = metadata_file.id()

        with tempfile.NamedTemporaryFile("w+", delete=True) as tempfile_ref:
            request = models.Request(
                id=self.metadata_id,
                path=tempfile_ref.name,
            )

            self.service.download(request)
            tempfile_ref.seek(0)

            return json.loads(tempfile_ref.read())

    def load_metadata(self, metadata_file):
        self.metadata = self.load_metadata_json(metadata_file)
        logger.debug(f"Loaded metadata: {self.metadata}")

        if "version" not in self.metadata:
            logger.critical(f"'version' field missing from metadata!  This is an outdated or unversioned meta file.  You will need to fix it by running `mm <service> refresh`.")
            raise RuntimeError("Unversioned metadata")

        version = self.metadata["version"]
        if version > settings.VERSION:
            logger.critical(f"Metadata version ({version}) exceeds software version ({settings.VERSION}).  You need to update your software to parse this metadata file.")
            raise RuntimeError("Outdated software")

        if version < settings.VERSION:
            logger.critical(f"Metadata version ({version}) is below software version ({settings.VERSION}).  You need to update it by running `mm <service> refresh`.")
            raise RuntimeError("Outdated metadata")

    def track_cipher(self, key, cipher, digest):
        global CIPHER
        self.metadata["data"][key] = {"cipher": cipher, "digest": digest}
        self.update_metadata()

    def upload(self, request):
        # TODO: remove metadata when file is deleted
        keypath = KEYPATH
        cipher = DEFAULT_CIPHER
        digest = DEFAULT_DIGEST

        with encrypt(request, keypath, cipher, digest) as encrypted_tempfile:
            request.path = encrypted_tempfile.name
            receipt = self.service.upload(request)

        self.track_cipher(receipt.id(), cipher, digest)  # IMPORTANT -- must track by sid!
        return receipt

    def download(self, request):
        if request.id not in self.metadata["data"]:
            logger.info(f"Downloading unencrypted file: {request}")
            return self.service.download(request)

        params = self.metadata["data"][request.id]

        keypath = KEYPATH
        cipher = params["cipher"]
        digest = params["digest"]

        logger.info(f"Downloading encrypted file: {request}")
        with tempfile.NamedTemporaryFile("wb+", delete=True) as tempfile_ref:
            temp_request = models.Request(
                id=request.id,
                path=tempfile_ref.name,
            )

            receipt = self.service.download(temp_request)
            tempfile_ref.seek(0)

            decrypt(tempfile_ref.name, request.path, keypath, cipher, digest)

        return receipt
