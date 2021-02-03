# Google Drive Setup Guide

## Create Local Path for OAuth Credentials
By default, this path is `~/.mediaman/credentials/drive`.

1. Create the `~/.mediaman/credentials/drive/client-secrets/` directory
2. Create the `~/.mediaman/credentials/drive/credentials/` directory


## Generate Google OAuth Credentials
1. Go to the [Google Developer Console](https://console.developers.google.com/apis/dashboard)

2. Create a "MediaMan" project
    1. From the project dropdown, hit **New Project**
    2. Name it "MediaMan" (or anything) and create it
    3. Select the new project (make sure it's active)

3. Add the **Google Drive API**
    1. Go to [APIs & Service > Library]
    2. Search for and add the **Google Drive API**

4. Add an OAuth Client ID
    1. Go to [APIs & Service > Credentials]
    2. Click [+ Create Credentials > OAuth client ID]
    3. Click **Configure Consent Screen**
    4. Choose "External" and click **Create**
    5. Under "App name" enter "MediaManApp" and fill your email in where asked
    6. Click **Save and Continue**
    7. Click **Add or Remove Scopes**
    8. Search for "Google Drive API" and choose the `.../auth/drive` scope
        - IT IS THUS VERY IMPORTANT THAT YOU PROTECT THESE CREDENTIALS.
        - `.../auth/drive.file` ?
    9. Click **Save and Continue**
    10. Add yourself as a Test User (your Gmail)
    10. Click **Save and Continue**
    11. Click **Back to Dashboard**

    1. Go to [APIs & Service > Credentials]
    2. Click [+ Create Credentials > OAuth client ID]
    3. Choose "Desktop app" and name it "MediaMan Desktop Client"
    4. Click **Create**

    5. Download the OAuth credentials as JSON (click the download icon)
    6. Move the JSON file to `~/.mediaman/credentials/drive/client-secrets/client-secret.json`

5. Authorize MediaMan to use the credentials
    1. Run `mm <service> list` for your Drive service
    2. Visit the link given after MediaMan asks "Go to the following link in your browser:"
    3. Choose the appropriate Google Account
    4. It will say "Google hasn't verified this app", hit **Continue**
    5. It will ask "Grant MediaManApp permission" to "See, edit, create, and delete all of your Google Drive files", click **Allow**
        - AGAIN, IS THUS VERY IMPORTANT THAT YOU PROTECT THESE CREDENTIALS.
    6. It will say "Confirm your choices", click **Allow**
    7. Copy the code it shows you, enter it at the "Enter verification code:" prompt MediaMan is showing
    8. MediaMan will create a new MediaMan folder in your Google Drive and report back 0 files.

