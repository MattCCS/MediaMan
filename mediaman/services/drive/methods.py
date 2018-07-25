
import os

import apiclient.discovery
import apiclient.http
import googleapiclient
import httplib2
import oauth2client.client
import oauth2client.file


OAUTH2_SCOPE = "https://www.googleapis.com/auth/drive"


CLIENT_SECRETS = os.environ.get("GOOGLE_CLIENT_SECRETS", None)
CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS", None)


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


def files(drive):
    return drive.files().list().execute()


def exists(drive, file_id):
    try:
        drive.files().get(fileId=file_id).execute()
        return True
    except googleapiclient.errors.HttpError as exc:
        if exc.resp["status"] == "404":
            return False
        raise exc


def put(drive, file_id, file_path):
    media_body = apiclient.http.MediaFileUpload(
        file_path,
        mimetype="application/octet-stream",  # NOTE: this is optional
        resumable=True
    )
    # The body contains the metadata for the file.
    body = {
        "title": file_id,
        "description": "",  # TODO: remove the blank description?
    }

    # Perform the request and print the result.
    receipt = drive.files().insert(body=body, media_body=media_body).execute()
    return receipt


def get(drive, file_id):
    return drive.files().get(fileId=file_id).execute()
