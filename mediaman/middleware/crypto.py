
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

logger = logtools.new_logger(__name__)

# <openssl> enc -<e/d> -<cipher> -kfile <keypath> -md <digest> -in <inpath> -out <outpath>
DEFAULT_CIPHER = "aes-256-cbc"
DEFAULT_DIGEST = "sha256"
CRYPTO_KEY_ENV_VAR = "MM_CRYPTO_KEY"
DEFAULT_KEY_PATH = os.path.expanduser("~/.mediaman/key")

KEYPATH = config.load(CRYPTO_KEY_ENV_VAR, default=DEFAULT_KEY_PATH)

OPENSSL_PREFERRED_BINS = [
    "/usr/local/Cellar/libressl/3.2.2/bin",
    "/usr/local/Cellar/libressl/2.9.2/bin",
    "/usr/bin",
]

ERROR_MULTIPLE_REMOTE_FILES = "\
[!] Multiple crypt files found for service ({})!  \
This must be resolved manually.  Exiting..."


TEST_SESH = {}  # name: salt


def form_path_prepend():
    global OPENSSL_PREFERRED_BINS
    return ":".join(OPENSSL_PREFERRED_BINS + [config.load_safe("PATH")])  # TODO: replace with env call


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


def decrypt_stream(source, keypath, cipher, digest):
    import threading

    def pump_input(pipe, source):
        # https://stackoverflow.com/questions/32322034/writing-large-amount-of-data-to-stdin
        with pipe:
            for bytez in source:
                pipe.write(bytez)
                pipe.flush()

    def deal_with_stdout(process, sink):
        for bytez in process.stdout:
            sink.write(bytez)
            sink.flush()

    args = [
        "openssl", "enc", "-d",
        "-kfile", keypath, f"-{cipher}", "-md", digest,
        "-bufsize", "1048576",
    ]
    logger.info(f"decrypting: {args}")

    logger.info(f"Decrypting stream...")
    try:
        process = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, env=form_subprocess_environ())

        # threading.Thread(target=deal_with_stdout, args=[process, sink]).start()
        # for bytez in source:
        #     process.stdin.write(bytez)
        #     process.stdin.flush()

        threading.Thread(target=pump_input, args=[process.stdin, source]).start()
        # import sys
        # sink = sys.stdout.buffer
        # for bytez in process.stdout:
        #    # sink.write(bytez)
        #    # sink.flush()
        while True:
            bytez = process.stdout.read()
            # logger.debug(bytez)
            if not bytez:
                return
            yield bytez
        # for bytez in process.stdout:
        #     logger.debug(bytez)
        #     yield bytez
        # yield from process.stdout
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

    def __init__(self, service):
        super().__init__(service)
        logger.info(f"EncryptionMiddlewareService init for {service}")

    # def init_metadata(self):
    #     if self.metadata is not None:
    #         return

    #     # TODO: implement
    #     file_list = self.service.search_by_name(EncryptionMiddlewareService.MIDDLEWARE_FILENAME)
    #     files = file_list.results()

    #     if len(files) > 1:
    #         raise RuntimeError(ERROR_MULTIPLE_REMOTE_FILES.format(self.service))

    #     if not files:
    #         logger.debug(f"creating metadata")
    #         self.metadata = create_metadata()
    #         self.update_metadata()
    #     else:
    #         logger.debug(f"loading metadata")
    #         self.load_metadata(files[0])

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
        logger.trace(f"Loaded metadata: {self.metadata}")

        # TODO: some sane way for crypto to manage metadata version (or just combine the files...?)

    def upload(self, request, encryption):
        if encryption is None:
            logger.info(f"Uploading unencrypted file: {request}")
            return self.service.upload(request)

        # TODO: remove metadata when file is deleted
        keypath = KEYPATH
        cipher = encryption["cipher"]
        digest = encryption["digest"]

        logger.info(f"Uploading encrypted file: {request}")
        with encrypt(request, keypath, cipher, digest) as encrypted_tempfile:
            request.path = encrypted_tempfile.name
            receipt = self.service.upload(request)

        return receipt

    def download(self, request, encryption):
        if encryption is None:
            logger.info(f"Downloading unencrypted file: {request}")
            return self.service.download(request)

        keypath = KEYPATH
        cipher = encryption["cipher"]
        digest = encryption["digest"]

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

    def stream(self, request, encryption):
        if encryption is None:
            logger.info(f"Streaming unencrypted file: {request}")
            return self.service.stream(request)

        # global TEST_SESH
        # if request.id not in TEST_SESH:
        #     TEST_SESH[request.id] = {"ebuff": None, "pbuff": None}

        keypath = KEYPATH
        cipher = encryption["cipher"]
        digest = encryption["digest"]

        logger.info(f"Streaming encrypted file: {request}")
        temp_request = models.Request(
            id=request.id,
        )

        stream = self.service.stream(temp_request)

        return decrypt_stream(stream, keypath, cipher, digest)

    def stream_range(self, request, offset, length, encryption):
        if encryption is None:
            logger.info(f"Streaming unencrypted file: {request}")
            return self.service.stream_range(request, offset, length)

        logger.info(f"Streaming encrypted file: {request}")
        temp_request = models.Request(
            id=request.id,
        )

        if offset < 16:
            return self.stream_range_continuous(temp_request, offset, length, encryption=encryption)
        return self.stream_range_discontinuous(temp_request, offset, length, encryption=encryption)

    def stream_range_continuous(self, request, offset, length, encryption):
        keypath = KEYPATH
        cipher = encryption["cipher"]
        digest = encryption["digest"]

        import math
        BLOCK_SIZE = 16

        blocks_needed = int(math.ceil((offset + length) / BLOCK_SIZE))

        skip = 0
        count = (blocks_needed + 2) * BLOCK_SIZE

        stream = self.service.stream_range(request, skip, count)
        out_stream = decrypt_stream(stream, keypath, cipher, digest)

        remaining = length
        first = True
        for bytez in out_stream:
            # print(f"\tremaining={remaining}")
            if first:
                # print(f"\ttrimming {bytez}")
                bytez = bytez[(offset % 16):]
                # print(f"\tto {bytez}")
                first = False

            if len(bytez) >= remaining:
                yield bytez[:remaining]
                remaining -= remaining
                break

            yield bytez
            remaining -= len(bytez)

    def stream_range_discontinuous(self, request, offset, length, encryption):
        keypath = KEYPATH
        cipher = encryption["cipher"]
        digest = encryption["digest"]

        import itertools
        import math
        logger.debug(f"Getting CBC salt...")
        BLOCK_SIZE = 16

        start_block = offset // BLOCK_SIZE
        blocks_needed = int(math.ceil((offset + length) / BLOCK_SIZE) - start_block)

        global TEST_SESH
        try:
            salt = TEST_SESH[request.id]
        except KeyError:
            salt = [next(self.service.stream_range(request, 0, 16))]
            TEST_SESH[request.id] = salt

        skip = (start_block) * BLOCK_SIZE
        count = (blocks_needed + 2) * BLOCK_SIZE

        data = self.service.stream_range(request, skip, count)

        stream = itertools.chain(salt, data)
        out_stream = decrypt_stream(stream, keypath, cipher, digest)

        remaining = length
        first = True
        for bytez in out_stream:
            # print(f"\tremaining={remaining}")
            if first:
                # print(f"\ttrimming {bytez}")
                bytez = bytez[(offset % 16) + 16:]
                # print(f"\tto {bytez}")
                first = False

            if len(bytez) >= remaining:
                # print(f"\tend")
                yield bytez[:remaining]
                remaining -= remaining
                break

            yield bytez
            remaining -= len(bytez)
