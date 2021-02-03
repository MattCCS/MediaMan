
import io
import logging
import os

import apiclient.discovery
import apiclient.http
import googleapiclient
import httplib2
import oauth2client.client
import oauth2client.file

from mediaman import logtools

logger = logtools.new_logger("mediaman.services.drive.methods")

# This suppresses warnings from googleapiclient, and
# prevents it from polluting the log files.
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)


OAUTH2_SCOPE = "https://www.googleapis.com/auth/drive"


def ensure_directory(drive, destination):
    logger.debug("[ ] Ensuring Google Drive destination...")

    if not destination:
        # TODO: use logging library
        logger.debug("[+] No directory specified.  Using top-level directory.")
        return None

    folders = drive.files().list(
        q=f"title='{destination}' and mimeType='application/vnd.google-apps.folder'",
        fields="items(id)",
    ).execute()["items"]

    if folders:
        assert len(folders) == 1
        folder_id = folders[0]["id"]
        logger.debug(f"[+] Directory found ({folder_id}).")
        return folder_id

    metadata = {
        'title': destination,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.files().insert(
        body=metadata,
        fields='id',
    ).execute()
    folder_id = folder["id"]
    logger.debug(f"[+] Directory created ({folder_id}).")

    return folder["id"]


def authenticate(client_secrets, credentials_path):
    assert client_secrets or credentials_path

    credentials = None
    if credentials_path:
        storage = oauth2client.file.Storage(credentials_path)
        credentials = storage.get()

    if credentials is None:
        # Perform OAuth2.0 authorization flow.
        flow = oauth2client.client.flow_from_clientsecrets(client_secrets, OAUTH2_SCOPE)
        flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
        authorize_url = flow.step1_get_authorize_url()
        print("Go to the following link in your browser: " + authorize_url)
        code = input("Enter verification code: ").strip()
        credentials = flow.step2_exchange(code)

    if credentials_path:
        storage.put(credentials)

    # Create an authorized Drive API client.
    http = httplib2.Http()
    credentials.authorize(http)
    service = apiclient.discovery.build("drive", "v2", http=http)
    return service


def xlist_files(drive, folder_id=None):
    # NOTE: any children() call to Drive returns Child objects, without names!
    if folder_id:
        # return drive.children().list(folderId=folder_id).execute()
        return drive.files().list(q=f"'{folder_id}' in parents").execute()
    return drive.files().list().execute()


def list_files(drive, folder_id=None):
    result = []
    page_token = None
    while True:
        try:
            param = {}
            if folder_id:
                param['q'] = f"'{folder_id}' in parents"
            if page_token:
                param['pageToken'] = page_token

            files = drive.files().list(**param).execute()

            result.extend(files['items'])
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        # except errors.HttpError as error:
        except Exception as error:
            print('An error occurred: %s' % error)

    logger.debug(len(result))
    return {"items": result}


def list_file(drive, file_id):
    return drive.files().get(fileId=file_id).execute()


def exists(drive, file_id, folder_id=None):
    # TODO: use folder_id param
    logger.warning("`folder_id` usage is not yet implemented in this method!")
    try:
        list_file(drive, file_id)
        return True
    except googleapiclient.errors.HttpError as exc:
        if exc.resp["status"] == "404":
            return False
        raise exc


def upload(drive, request, folder_id=None):
    # NOTE:  This method is idempotent iff no files are already duplicated.

    # TODO: experiment with chunk size for huge files
    media_body = apiclient.http.MediaFileUpload(
        request.path,
        mimetype="application/octet-stream",  # NOTE: this is optional
        resumable=True,
        # chunksize=1024 * 256
    )

    # The body contains the metadata for the file.
    body = {
        "title": request.id,
        "description": "",  # TODO: remove the blank description?
    }

    if folder_id:
        body["parents"] = [{"id": folder_id}]

    # Decide whether to create or update.
    files = search_by_name(drive, request.id, folder_id=folder_id)["items"]

    if len(files) == 1:
        file_id = files[0]["id"]
        return upload_update(drive, body, media_body, file_id, folder_id=folder_id)

    if len(files) > 1:
        logger.warning("[!] Warning: multiple files exist with this name ({request.id})!  Can't safely replace one!")

    return upload_create(drive, body, media_body, folder_id=folder_id)


def upload_create(drive, body, media_body, folder_id=None):
    # Perform the request and return the result.
    receipt = drive.files().insert(body=body, media_body=media_body).execute()
    return receipt


def upload_update(drive, body, media_body, file_id, folder_id=None):
    receipt = drive.files().update(
        newRevision=False,
        fileId=file_id,
        body=body,
        media_body=media_body,
    ).execute()
    return receipt


def download(drive, request, folder_id=None):
    local_fd = io.FileIO(request.path, "wb")

    http_request = drive.files().get_media(fileId=request.id)
    media_request = apiclient.http.MediaIoBaseDownload(local_fd, http_request)

    while True:
        try:
            (download_progress, done) = media_request.next_chunk()
        except apiclient.errors.HttpError as error:
            raise

        if download_progress:
            logger.debug(f"[ ] Downloading... {download_progress.progress():.2%}")

        if done:
            logger.debug("[+] Download complete.")
            break

    return {
        "id": request.id,
        "path": request.path,
    }


def stream(drive, request, folder_id=None):
    memory_fd = io.BytesIO()

    import sys
    http_request = drive.files().get_media(fileId=request.id)
    # http_request.headers["Range"] = "bytes=500-599"
    # print(vars(http_request))
    # return
    # sys.stderr.write("123")
    # sys.stderr.flush()
    media_request = apiclient.http.MediaIoBaseDownload(memory_fd, http_request)

    while True:
        try:
            (download_progress, done) = media_request.next_chunk()
            sys.stderr.write("4")
            sys.stderr.flush()

            sys.stderr.write(f"Progress={download_progress}, done={done}\n")
            sys.stderr.flush()
            memory_fd.seek(0)
            yield memory_fd.read()
            memory_fd.seek(0)
            memory_fd.truncate()
        except apiclient.errors.HttpError as error:
            raise

        if download_progress:
            logger.debug(f"[ ] Downloading... {download_progress.progress():.2%}")

        if done:
            logger.debug("[+] Download complete.")
            break


def stream_range(drive, request, folder_id=None, offset=0, length=0):
    memory_fd = io.BytesIO()

    http_request = drive.files().get_media(fileId=request.id)
    media_request = apiclient.http.MediaIoBaseDownload(memory_fd, http_request, start=offset, chunksize=max(65536, length))

    logger.trace("Requested: offset={offset}, length={length}\n")

    while True:
        try:
            (download_progress, done) = media_request.next_chunk()

            memory_fd.seek(0)
            data = memory_fd.read()
            memory_fd.seek(0)
            memory_fd.truncate()
        except apiclient.errors.HttpError as error:
            raise

        if download_progress:
            logger.debug(f"[ ] Downloading... {download_progress.progress():.2%}")
            remaining = length
            abs_read = (download_progress.resumable_progress - 1)
            rel_read = (abs_read - offset)
            if rel_read < remaining:
                logger.trace(f"abs_read={abs_read}\n")
                logger.trace(f"rel_read={rel_read}\n")
                logger.trace(f"remaining={remaining}\n")
                logger.trace(f"Streamed {rel_read / 1_000_000} MB...\n")
                yield data
                remaining -= len(data)
            else:
                logger.trace(f"abs_read={abs_read}\n")
                logger.trace(f"rel_read={rel_read}\n")
                logger.trace(f"remaining={remaining}\n")
                logger.trace(f"Finished: {rel_read / 1_000_000} MB...\n")
                yield data[:remaining]
                return

        if done:
            logger.debug("[+] Download complete.")
            break


def search_by_name(drive, file_name, folder_id=None):
    if folder_id:
        request = drive.files().list(
            q=f"title='{file_name}' and '{folder_id}' in parents",
            fields="items(id, fileSize)",
        )
    else:
        request = drive.files().list(
            q=f"title='{file_name}'",
            fields="items(id, fileSize)",
        )

    files = request.execute()
    return files


def capacity(drive, quota, folder_id=None):
    capacity_info = drive.about().get().execute()
    used = int(capacity_info.get("quotaBytesUsed"))
    total = int(capacity_info.get("quotaBytesTotal"))
    trashed = int(capacity_info.get("quotaBytesUsedInTrash"))

    return {
        "used": used,
        "quota": quota,
        "total": total,
        "trashed": trashed,
    }


def remove(drive, file_id):
    drive.files().delete(fileId=file_id).execute()
    return {
        "id": file_id,
    }
