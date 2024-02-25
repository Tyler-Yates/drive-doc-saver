import os
import shutil
from typing import List

from drivedocsaver.src.constants import EXPECTED_EMAIL_FILE_NAME
from drivedocsaver.src.drive_client import DriveClient
from drivedocsaver.src.drive_file import DriveFile
from drivedocsaver.src.file_util import get_file_export

TRASH_PATH = ".trash"


def backup_files(
    drive_client: DriveClient,
    drive_files: List[DriveFile],
    backup_path: str,
):
    processed_drive_file_paths = set()
    files_downloaded = []
    files_moved_to_trash = []
    file_name_conflicts = []
    for drive_file in drive_files:
        file_export = get_file_export(backup_path, drive_file)

        # Google allows multiple files in the same folder with the same name
        if file_export.backup_file_path in processed_drive_file_paths:
            print(f"Two Google documents with the same file name in the same folder: {file_export.backup_file_path}")
            file_name_conflicts.append(file_export.backup_file_path)
            continue

        processed_drive_file_paths.add(file_export.backup_file_path)

        modified_time_for_file_we_have = None
        if os.path.exists(file_export.backup_file_path):
            modified_time_for_file_we_have = int(os.path.getmtime(file_export.backup_file_path))

        if modified_time_for_file_we_have is None:
            print(f"Backing up file '{file_export.backup_file_path}'...", end="")
            drive_client.download_file(file_export, drive_file)
            files_downloaded.append(file_export.backup_file_path)
            print("Done")
        elif abs(modified_time_for_file_we_have - drive_file.modified_unix_timestamp) <= 1:
            print(f"File '{drive_file.file_path}{drive_file.file_name}' already backed up.")
        else:
            print(
                f"File exists locally but is an old version (or changed locally). "
                f"Moving '{file_export.backup_file_path}' to trash."
            )
            _move_file_to_trash(backup_path, file_export.backup_file_path)
            files_moved_to_trash.append(file_export.backup_file_path)
            drive_client.download_file(file_export, drive_file)
            files_downloaded.append(file_export.backup_file_path)

    # Look for existing files that are no longer in Google Drive
    for root, dir_names, file_names in os.walk(backup_path):
        if TRASH_PATH in root:
            continue

        for file_name in file_names:
            if EXPECTED_EMAIL_FILE_NAME == file_name:
                continue

            backup_file_path = os.path.join(root, file_name)
            if backup_file_path not in processed_drive_file_paths:
                print(f"Found file on disk that is no longer in Google Drive: {backup_file_path}")
                _move_file_to_trash(backup_path, backup_file_path)
                files_moved_to_trash.append(backup_file_path)

    # Delete empty directories
    walk = list(os.walk(backup_path))
    for path, _, _ in walk[::-1]:
        if len(os.listdir(path)) == 0:
            print(f"Removing empty directory {path}")
            os.rmdir(path)

    # Print out files that we moved to trash:
    if len(files_moved_to_trash) > 0:
        print("\nFiles moved to trash:")
    for file_path in files_moved_to_trash:
        print(f"'{file_path}'.")

    # Print out files that we downloaded:
    if len(files_downloaded) > 0:
        print("\nFiles downloaded:")
    for file_path in files_downloaded:
        print(f"'{file_path}'.")

    # Print out files with the same name:
    if len(file_name_conflicts) > 0:
        print("\nFiles with name collision:")
    for file_path in file_name_conflicts:
        print(f"'{file_path}'.")


def _move_file_to_trash(backup_path: str, file_path: str):
    trash_path = os.path.join(backup_path, TRASH_PATH)
    trash_file_path = os.path.join(trash_path, file_path.replace(f"{backup_path}{os.path.sep}", ""))
    num = 1
    while os.path.exists(trash_file_path):
        base_trash_file_path = os.path.join(trash_path, file_path.replace(f"{backup_path}{os.path.sep}", ""))
        file_path_parts = base_trash_file_path.rpartition(".")
        trash_file_path = file_path_parts[0] + f"_{num}" + f".{file_path_parts[-1]}"
        num += 1

    print(f"Moving file to {trash_file_path}")

    os.makedirs(os.path.dirname(trash_file_path), exist_ok=True)
    shutil.move(file_path, trash_file_path)
