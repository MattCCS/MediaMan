"""
Class to manage a Service connection to Google Drive.
"""

import os

import httplib2
import apiclient.discovery
import apiclient.http
import oauth2client.client
import oauth2client.file

from mediaman.services import service


OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'


class DriveService(service.AbstractService):

    def __init__(self):
        self.drive_service = None

    def authenticate(self):
        CLIENT_SECRETS = os.environ.get("GOOGLE_CLIENT_SECRETS", None)
        CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS", None)

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
        self.drive_service = apiclient.discovery.build("drive", "v2", http=http)

    def files(self):
        return self.drive_service.files().list().execute()

    def exists(self, file_id):
        raise NotImplementedError()

    def put(self, file_id, file_path):
        raise NotImplementedError()

    def data(self, file_id):
        raise NotImplementedError()

    def metadata(self, file_id):
        raise NotImplementedError()
