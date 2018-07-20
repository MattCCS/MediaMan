# MediaMan
MediaMan is a set of tools to manage the backing up of arbitrary media files
to various cloud services for long-term storage and occasional retrieval.

It places a heavy emphasis on confidentiality, simple storage and retrieval
(including bulk operations), heavy indexing, and user experience.


## Installation
TBD

## Try it out
TBD

## Usage
TBD

## License
TBD

## Personal Setup Guide
- https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python
```
pip:
$ pip3 install google-api-python-client
$ pip3 install oauth2client

bash:
$ GOOGLE_APPLICATION_CREDENTIALS="/Users/matthewcotton/Repos/MyRepos/MediaMan/mediaman/drive/credentials/serviceaccount/xxx.json" p


python:
>>> from apiclient.discovery import build
>>> drive = build("drive", "v3")
>>> drive.files().list().execute()
{'files': [{'id': '...',
            'kind': 'drive#file',
            'mimeType': 'application/pdf',
            'name': 'Getting started'}],
 'incompleteSearch': False,
 'kind': 'drive#fileList'}

>>> file_metadata = {'name': 'test.txt'}
>>> media = googleapiclient.http.MediaFileUpload("test.txt")
>>> file_receipt = drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
>>> file_receipt
{'id': '...'}

>>> drive.files().list().execute()
{'files': [{'id': '...',
            'kind': 'drive#file',
            'mimeType': 'text/plain',
            'name': 'test.txt'},
           {'id': '...',
            'kind': 'drive#file',
            'mimeType': 'application/pdf',
            'name': 'Getting started'}],
 'incompleteSearch': False,
 'kind': 'drive#fileList'}
```
