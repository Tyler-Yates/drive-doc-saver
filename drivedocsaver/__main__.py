import os.path
import sys
from typing import List

from drivedocsaver.src.drive_client import DriveClient
from drivedocsaver.src.drive_file import DriveFile
from drivedocsaver.src.file_util import get_file_export

CLIENT_SECRETS_FILE_NAME = "client_secrets.json"
BACKUP_FILE_NAME = "liked_videos.json"


def backup_files(
    drive_client: DriveClient,
    drive_files: List[DriveFile],
    backup_path: str,
):
    for drive_file in drive_files:
        file_export = get_file_export(backup_path, drive_file)

        modified_time_for_file_we_have = None
        if os.path.exists(file_export.backup_file_path):
            modified_time_for_file_we_have = int(os.path.getmtime(file_export.backup_file_path))

        if modified_time_for_file_we_have == drive_file.modified_unix_timestamp:
            print(f"No modifications for file '{drive_file.file_path}{drive_file.file_name}'. Skipping.")
        else:
            print(f"Backing up file '{drive_file.file_path}{drive_file.file_name}'...", end="")
            drive_client.download_file(file_export, drive_file)
            print("Done")


def main():
    if len(sys.argv) == 1:
        backup_path = ""
    elif len(sys.argv) == 2:
        backup_path = sys.argv[1]
    else:
        print("Incorrect number of arguments.")
        sys.exit(1)

    print(f"Backing up to location '{backup_path}'")
    drive_client = DriveClient(CLIENT_SECRETS_FILE_NAME)

    drive_files = drive_client.get_google_doc_files()

    print(f"Found {len(drive_files)} files to process...")

    backup_files(drive_client, drive_files, backup_path)


if __name__ == "__main__":
    main()
