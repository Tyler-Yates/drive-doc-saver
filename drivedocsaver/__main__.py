import os.path
import shutil
import sys
from typing import List

from drivedocsaver.src.drive_client import DriveClient
from drivedocsaver.src.drive_file import DriveFile
from drivedocsaver.src.file_util import get_file_export

TRASH_PATH = ".trash"

CLIENT_SECRETS_FILE_NAME = "client_secrets.json"
BACKUP_FILE_NAME = "liked_videos.json"


def backup_files(
    drive_client: DriveClient,
    drive_files: List[DriveFile],
    backup_path: str,
):
    processed_drive_file_paths = set()
    for drive_file in drive_files:
        file_export = get_file_export(backup_path, drive_file)
        processed_drive_file_paths.add(file_export.backup_file_path)

        modified_time_for_file_we_have = None
        if os.path.exists(file_export.backup_file_path):
            modified_time_for_file_we_have = int(os.path.getmtime(file_export.backup_file_path))

        if modified_time_for_file_we_have == drive_file.modified_unix_timestamp:
            print(f"No modifications for file '{drive_file.file_path}{drive_file.file_name}'. Skipping.")
        else:
            print(f"Backing up file '{drive_file.file_path}{drive_file.file_name}'...", end="")
            drive_client.download_file(file_export, drive_file)
            print("Done")

    # Look for existing files that are no longer in Google Drive
    for root, dir_names, file_names in os.walk(backup_path):
        if TRASH_PATH in root:
            continue

        for file_name in file_names:
            backup_file_path = os.path.join(root, file_name)
            if backup_file_path not in processed_drive_file_paths:
                print(f"Found file on disk that is no longer in Google Drive: {backup_file_path}")
                _move_file_to_trash(backup_path, backup_file_path)

    # Delete empty directories
    walk = list(os.walk(backup_path))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            print(f"Removing empty directory {path}")
            os.rmdir(path)


def _move_file_to_trash(backup_path: str, file_path: str):
    trash_path = os.path.join(backup_path, TRASH_PATH)
    trash_file_path = os.path.join(trash_path, file_path.replace(f"{backup_path}/", ""))

    os.makedirs(os.path.dirname(trash_file_path))
    shutil.move(file_path, trash_file_path)


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
