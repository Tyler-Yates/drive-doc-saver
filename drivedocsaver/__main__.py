import sys
from typing import List

from drivedocsaver.src.drive_client import DriveClient
from drivedocsaver.src.drive_file import DriveFile

CLIENT_SECRETS_FILE_NAME = "client_secrets.json"
BACKUP_FILE_NAME = "liked_videos.json"


def backup_files(drive_client: DriveClient, drive_files: List[DriveFile], backup_file_location: str):
    for drive_file in drive_files:
        print(f"Backing up file '{drive_file.file_path}{drive_file.file_name}'...")
        drive_client.download_file(drive_file, backup_file_location)
        print("Done\n")


def main():
    if len(sys.argv) == 1:
        backup_file_location = ""
    elif len(sys.argv) == 2:
        backup_file_location = sys.argv[1]
    else:
        print("Incorrect number of arguments.")
        sys.exit(1)

    print(f"Backing up to location '{backup_file_location}'")
    drive_client = DriveClient(CLIENT_SECRETS_FILE_NAME)

    drive_files = drive_client.get_google_doc_files()

    print(f"Found {len(drive_files)} files to process...")
    backup_files(drive_client, drive_files, backup_file_location)


if __name__ == "__main__":
    main()
