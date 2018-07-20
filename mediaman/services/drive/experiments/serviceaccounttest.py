# service account basic example
import googleapiclient
from apiclient.discovery import build

drive = build("drive", "v3")
drive.files().list().execute()

file_metadata = {'name': 'test.txt'}
media = googleapiclient.http.MediaFileUpload("test.txt")
file_receipt = drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
file_receipt

drive.files().list().execute()
