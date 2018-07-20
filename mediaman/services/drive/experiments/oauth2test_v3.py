import os
import pprint

import httplib2
import apiclient.discovery
import apiclient.http
import oauth2client.client
import oauth2client.file

# OAuth 2.0 scope that will be authorized.
# Check https://developers.google.com/drive/scopes for all available scopes.
OAUTH2_SCOPE = 'https://www.googleapis.com/auth/drive'

# Location of the client secrets.
# CLIENT_SECRETS = 'client_secrets.json'
CLIENT_SECRETS = os.environ["GOOGLE_CLIENT_SECRETS"]

# Path to the file to upload.
FILENAME = 'test.txt'

# Metadata about the file.
MIMETYPE = 'text/plain'
TITLE = 'My New Text Document'
DESCRIPTION = 'A shiny new text document about hello world.'


storage = oauth2client.file.Storage("a_credentials_file")
credentials = storage.get()

if credentials is None:
    # Perform OAuth2.0 authorization flow.
    flow = oauth2client.client.flow_from_clientsecrets(CLIENT_SECRETS, OAUTH2_SCOPE)
    flow.redirect_uri = oauth2client.client.OOB_CALLBACK_URN
    authorize_url = flow.step1_get_authorize_url()
    print('Go to the following link in your browser: ' + authorize_url)
    code = input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage.put(credentials)

# Create an authorized Drive API client.
http = httplib2.Http()
credentials.authorize(http)
drive_service = apiclient.discovery.build('drive', 'v2', http=http)

# Insert a file. Files are comprised of contents and metadata.
# MediaFileUpload abstracts uploading file contents from a file on disk.
media_body = apiclient.http.MediaFileUpload(
    FILENAME,
    mimetype=MIMETYPE,
    resumable=True
)
# The body contains the metadata for the file.
body = {
    'title': TITLE,
    'description': DESCRIPTION,
}

# Perform the request and print the result.
new_file = drive_service.files().insert(body=body, media_body=media_body).execute()
pprint.pprint(new_file)
