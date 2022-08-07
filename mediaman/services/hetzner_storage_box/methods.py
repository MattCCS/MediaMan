
import pathlib
import subprocess

from mediaman.core import logtools

logger = logtools.new_logger(__name__)


def parse_du_human_bytes(human_bytes):
    import re
    units = {"B": 0, "K": 1, "M": 2, "G": 3, "T": 4}
    human_bytes_regex = r"(?P<cap>[\d\._]+)(\s+)?(?P<unit>\D+)"
    try:
        m = re.match(human_bytes_regex, human_bytes.strip())
        cap = float(m["cap"].replace("_", ""))
        cap *= (1000 ** units[m["unit"]])
        return int(cap)
    except (KeyError, ValueError, TypeError) as exc:
        raise RuntimeError(f"Couldn't parse du human bytes: {human_bytes}", exc)


def execute_command(config, command_string):
    identity_file_path = config["IDENTITY_FILE_PATH"]
    username_and_hostname = config["USERNAME_AND_HOSTNAME"]
    port_number = config["PORT_NUMBER"]

    ssh_command = [
        "ssh",
        "-i", str(identity_file_path),
        username_and_hostname,
        "-p", str(port_number),
        "-C", command_string,
    ]
    ssh_command_string = " ".join(ssh_command)
    logger.debug(f"{ssh_command_string=}")

    output = subprocess.check_output(ssh_command_string, shell=True, stderr=subprocess.PIPE)
    logger.trace(f"{output=}")

    return output


def scp(config, destination_folder, request):
    identity_file_path = config["IDENTITY_FILE_PATH"]
    username_and_hostname = config["USERNAME_AND_HOSTNAME"]
    port_number = config["PORT_NUMBER"]

    destination_path = str(pathlib.Path(destination_folder) / request.id)
    dest = f"/home/{destination_path}"

    scp_command = [
        "scp",
        "-i", str(identity_file_path),
        "-P", str(port_number),
        request.path,
        f"{username_and_hostname}:{dest}",
    ]
    scp_command_string = " ".join(scp_command)

    # TODO: redirect output to log
    subprocess.run(scp_command_string, shell=True, stderr=subprocess.PIPE)


def sftp_download(config, destination_folder, request):
    identity_file_path = config["IDENTITY_FILE_PATH"]
    username_and_hostname = config["USERNAME_AND_HOSTNAME"]
    port_number = config["PORT_NUMBER"]

    destination_path = str(pathlib.Path(destination_folder) / request.id)
    dest = f"/home/{destination_path}"

    sftp_command = [
        "sftp",
        "-i", str(identity_file_path),
        "-P", str(port_number),
        f"{username_and_hostname}:{dest}",
        request.path,
    ]
    sftp_command_string = " ".join(sftp_command)

    # TODO: redirect output to log
    subprocess.run(sftp_command_string, shell=True, stderr=subprocess.PIPE)


#######################################

def require_destination_path(destination):  # str -> str
    assert destination
    logger.warning("hetzner_storage_box.require_destination_path is not yet implemented!")
    # path = pathlib.Path(destination)
    # assert path.exists()
    # assert path.is_absolute()
    return destination


def extractor(ls_line):  # str -> dict
    (permissions, links, user, group, size, month, day, time, filename) = ls_line.split()
    return {
        "is_dir": (permissions[0] == "d"),
        "name": filename,
        "size": int(size),
    }


def ls(config, path):  # list[str]
    ls_command_string = f"ls -Alf /home/{path}"
    output = execute_command(config, ls_command_string)
    return [
        line for line in output.decode("utf-8").strip().split("\n")
        if not line.startswith("total ")
    ]


def list_files(config, destination_path):  # list[dict]
    logger.debug(f"listing files in {repr(destination_path)}")
    unfiltered_files = list(map(
        extractor, ls(config, destination_path)
    ))
    files = [
        f for f in unfiltered_files
        if not (f["is_dir"] or f["name"].startswith("."))
    ]
    logger.trace(f"files = {files}")
    logger.debug(f"files: {len(files)}")
    return files


# def list_file(destination_path, file_id):
#     path = pathlib.Path(destination_path / file_id)
#     if not path.exists():
#         raise FileNotFoundError()  # TODO: raise custom error

#     return extractor(path)


def search_by_name(config, destination_path, file_name):
    logger.debug(f"searching for {repr(file_name)} in {repr(destination_path)}")
    out = (data for data in list_files(config, destination_path) if data["name"] == file_name)
    out = list(out)
    logger.debug(f"out = {out}")
    return out


# def exists(destination_path, file_id):
#     return (destination_path / file_id).exists()


def upload(config, destination_folder, request):
    scp(config, destination_folder, request)
    return {
        "id": request.id,
    }


def download(config, destination_path, request):
    # TODO: check for overwriting?
    sftp_download(config, destination_path, request)
    return {
        "id": request.id,
        "path": request.path,
    }


# def stream(destination_path, request):
#     source_file_path = destination_path / request.id
#     written = 0
#     with open(source_file_path, "rb") as infile:
#         data = infile.read(WRITE_BUFFER)
#         while data:
#             yield data
#             written += len(data)
#             logger.info(f"Wrote {written / 1_000_000:.2f} MB...")
#             data = infile.read(WRITE_BUFFER)


def stream_range(config, destination_folder, request, offset, length):
    destination_path = str(pathlib.Path(destination_folder) / request.id)

    dd_command = [
        "dd",
        "ibs=1",
        f"if=/home/{destination_path}",  # TODO: spaces in request.id?
        f"skip={offset}",
        f"count={length}",
    ]
    dd_command_string = " ".join(dd_command)

    output = execute_command(config, dd_command_string)
    yield output


def capacity(destination_folder, quota, config):
    absolute_destination_folder = f"/home/{destination_folder}"
    root_folder = f"/home/"

    du_command_string = f"du -h -d 0 {absolute_destination_folder}"
    df_command_string = f"df"

    du_output = execute_command(config, du_command_string)
    usage_human = du_output.decode("utf-8").split("\t", 1)[0].strip()

    df_output = execute_command(config, df_command_string).decode("utf-8")
    (block_line, capacity_line) = df_output.strip().split("\n")
    blocksize = int(block_line.split()[1].replace("-blocks", ""))
    blocks = int(capacity_line.split()[1])
    capacity_blocks = df_output.strip().split("\n", 2)[1].split()[1]

    return {
        "used": parse_du_human_bytes(usage_human),
        "quota": quota,
        "total": blocksize * blocks,
    }


# def remove(destination_path, file_id):
#     path = pathlib.Path(destination_path / file_id)
#     logger.debug(f"Removing file at '{path}' ...")

#     assert path.is_absolute()
#     if not path.exists():
#         raise FileNotFoundError()  # TODO: raise custom error

#     os.remove(path)
#     return {
#         "id": file_id,
#     }
