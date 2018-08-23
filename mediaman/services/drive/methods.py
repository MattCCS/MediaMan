
import io

import apiclient.discovery
import apiclient.http
import googleapiclient
import httplib2
import oauth2client.client
import oauth2client.file

from mediaman import config


OAUTH2_SCOPE = "https://www.googleapis.com/auth/drive"


CLIENT_SECRETS = config.load("GOOGLE_CLIENT_SECRETS")
CREDENTIALS = config.load("GOOGLE_CREDENTIALS")
DESTINATION = config.load("GOOGLE_DESTINATION")


def ensure_directory(drive):
    print("[ ] Ensuring Google Drive destination...")

    if not DESTINATION:
        # TODO: use logging library
        print("[+] No directory specified.  Using top-level directory.")
        return None

    folders = drive.files().list(
        q=f"title='{DESTINATION}' and mimeType='application/vnd.google-apps.folder'",
        fields="items(id)",
    ).execute()["items"]

    if folders:
        assert len(folders) == 1
        folder_id = folders[0]["id"]
        print(f"[+] Directory found ({folder_id}).")
        return folder_id

    metadata = {
        'title': DESTINATION,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.files().insert(
        body=metadata,
        fields='id',
    ).execute()
    folder_id = folder["id"]
    print(f"[+] Directory created ({folder_id}).")

    return folder["id"]


def authenticate():
    global CLIENT_SECRETS, CREDENTIALS
    assert CLIENT_SECRETS or CREDENTIALS

    credentials = None
    if CREDENTIALS:
        storage = oauth2client.file.Storage(CREDENTIALS)
        credentials = storage.get()

    if credentials is None:
        # Perform OAuth2.0 authorization flow.
        flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
        flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
        authorize_url = flow.step1_get_authorize_url()
        print("Go to the following link in your browser: " + authorize_url)
        code = input("Enter verification code: ").strip()
        credentials = flow.step2_exchange(code)

    if CREDENTIALS:
        storage.put(credentials)

    # Create an authorized Drive API client.
    http = httplib2.Http()
    credentials.authorize(http)
    service = apiclient.discovery.build("drive", "v2", http=http)
    return service


def list_files(drive, folder_id=None):
    if folder_id:
        return drive.children().list(folderId=folder_id).execute()
    return drive.files().list().execute()


def list_file(drive, file_id, folder_id=None):
    if folder_id:
        return drive.children().get(childId=file_id, folderId=folder_id).execute()
    return drive.files().get(fileId=file_id).execute()


def exists(drive, file_id, folder_id=None):
    try:
        list_file(drive, file_id, folder_id=folder_id)
        return True
    except googleapiclient.errors.HttpError as exc:
        if exc.resp["status"] == "404":
            return False
        raise exc


def upload(drive, source_file_path, destination_file_name, folder_id=None):
    # NOTE:  This method is idempotent.

    media_body = apiclient.http.MediaFileUpload(
        source_file_path,
        mimetype="application/octet-stream",  # NOTE: this is optional
        resumable=True,
    )

    # The body contains the metadata for the file.
    body = {
        "title": destination_file_name,
        "description": "",  # TODO: remove the blank description?
    }

    if folder_id:
        body["parents"] = [{"id": folder_id}]

    # Decide whether to create or update.
    files = list_by_name(drive, destination_file_name, folder_id=folder_id)

    if len(files) == 1:
        file_id = files[0]["id"]
        return upload_update(drive, body, media_body, file_id, folder_id=folder_id)

    if len(files) > 1:
        print("[!] Warning: multiple files exist with this name ({destination_file_name})!  Can't safely replace one!")

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


def download(drive, source_file_name, destination_file_path, folder_id=None):
    local_fd = io.FileIO(destination_file_path, "wb")

    request = drive.files().get_media(fileId=source_file_name)
    media_request = apiclient.http.MediaIoBaseDownload(local_fd, request)

    while True:
        try:
            (download_progress, done) = media_request.next_chunk()
        except apiclient.errors.HttpError as error:
            raise

        if download_progress:
            print(f"[ ] Downloading... {download_progress.progress():.2%}")

        if done:
            print("[+] Download complete.")
            break

    return {
        "id": source_file_name,
        "path": destination_file_path,
    }


def list_by_name(drive, file_name, folder_id=None):
    if folder_id:
        request = drive.children().list(
            folderId=folder_id,
            q=f"title='{file_name}'",
            fields="items(id)",
        )
    else:
        request = drive.files().list(
            q=f"title='{file_name}'",
            fields="items(id)",
        )

    files = request.execute()["items"]
    return files
