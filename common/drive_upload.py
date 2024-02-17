import os
from datetime import datetime

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive


def gdrive_authenticate(gdrive_secrets, client_secrets):
    gauth = GoogleAuth()

    # Specify the path to your client secrets file
    gauth.DEFAULT_SETTINGS['client_config_file'] = client_secrets
    gauth.LoadCredentialsFile(gdrive_secrets)  # Try to load saved client credentials
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved credentials
        gauth.Authorize()
    gauth.SaveCredentialsFile()

    drive = GoogleDrive(gauth)
    return drive


def gdrive_update_file(drive, file_id, local_path, new_remote_name):
   file_drive = drive.CreateFile({'id': file_id, 'title': new_remote_name})
   file_drive.SetContentFile(local_path)
   file_drive.Upload()

