import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

TOKEN_FILE_PATH = "gdrive_secrets.json"


def authenticate_drive():
    gauth = GoogleAuth()

    # Check if the token file exists
    if os.path.exists(TOKEN_FILE_PATH):
        gauth.LoadCredentialsFile(TOKEN_FILE_PATH)
    else:
        gauth.LocalWebserverAuth()
        # Save the credentials to a file for future use
        gauth.SaveCredentialsFile(TOKEN_FILE_PATH)

    drive = GoogleDrive(gauth)
    return drive


# Function to upload a new version of the file to Google Drive
def update_drive_file(drive, file_id, local_file_path):
    file_drive = drive.CreateFile({'id': file_id})
    file_drive.SetContentFile(local_file_path)
    file_drive.Upload()


def update_fash_cards_gdrive():
    file_id = "1nSz20dpnDIetmNATmfs-es25ZA8N3xTx"
    local_file_path = "flashcards.apkg"
    # Authenticate with Google Drive
    drive = authenticate_drive()
    # Update the file on Google Drive with a new version
    update_drive_file(drive, file_id, local_file_path)
