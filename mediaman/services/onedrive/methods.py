import os
import requests
import json

directory = r"c:\temp\uploads"
data = {
    'grant_type': "client_credentials",
    'resource': "https://graph.microsoft.com",
    'client_id': '7917b34f-b545-4b2b-83b9-3384cfbe17a2',
    'client_secret': 'XXXXX',
}

URL = "https://login.windows.net/YOURTENANTDOMAINNAME/oauth2/token?api-version=1.0"
r = requests.post(url=URL, data=data)
j = json.loads(r.text)
TOKEN = j["access_token"]
URL = "https://graph.microsoft.com/v1.0/users/YOURONEDRIVEUSERNAME/drive/root:/fotos/HouseHistory"
headers = {
    'Authorization': "Bearer " + TOKEN,
}

r = requests.get(URL, headers=headers)
j = json.loads(r.text)

print("Uploading file(s) to " + URL)

for root, dirs, files in os.walk(directory):
    for filename in files:
        filepath = os.path.join(root, filename)
        print("Uploading " + filename + "....")
        fileHandle = open(filepath, 'rb')
        r = requests.put(URL + "/" + filename + ":/content", data=fileHandle, headers=headers)
        fileHandle.close()
        if r.status_code == 200 or r.status_code == 201:
            # remove folder contents
            print("succeeded, removing original file...")
            os.remove(os.path.join(root, filename))
print("Script completed")

# import onedrivesdk

# redirect_uri = 'http://localhost:8080/'
# client_secret = 'your_client_secret'
# client_id = 'your_client_id'
# api_base_url = 'https://api.onedrive.com/v1.0/'
# scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

# http_provider = onedrivesdk.HttpProvider()
# auth_provider = onedrivesdk.AuthProvider(
#     http_provider=http_provider,
#     client_id=client_id,
#     scopes=scopes)

# client = onedrivesdk.OneDriveClient(api_base_url, auth_provider, http_provider)
# auth_url = client.auth_provider.get_auth_url(redirect_uri)
# # Ask for the code
# print('Paste this URL into your browser, approve the app\'s access.')
# print('Copy everything in the address bar after "code=", and paste it below.')
# print(auth_url)
# code = input('Paste code here: ')

# client.auth_provider.authenticate(code, redirect_uri, client_secret)
