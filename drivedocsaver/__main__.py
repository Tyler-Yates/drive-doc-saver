import os.path
import pickle
import sys
from typing import List, Dict

from drivedocsaver.src.drive_client import DriveClient
from drivedocsaver.src.drive_file import DriveFile

CLIENT_SECRETS_FILE_NAME = "client_secrets.json"
BACKUP_FILE_NAME = "liked_videos.json"

FILE_RECORD_PICKLE_FILE_NAME = "file_records.pickle"


def read_file_record() -> Dict[str, str]:
    if os.path.exists(FILE_RECORD_PICKLE_FILE_NAME):
        with open(FILE_RECORD_PICKLE_FILE_NAME, "rb") as handle:
            return pickle.load(handle)
    else:
        return dict()


def save_file_record(file_record_dict):
    with open(FILE_RECORD_PICKLE_FILE_NAME, "wb") as handle:
        pickle.dump(file_record_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)


def backup_files(
    drive_client: DriveClient,
    drive_files: List[DriveFile],
    backup_file_location: str,
    file_record_dictionary: Dict[str, str],
):
    for drive_file in drive_files:
        modified_time_for_file_we_have = file_record_dictionary.get(drive_file.file_id, "")

        if modified_time_for_file_we_have == drive_file.modified:
            print(f"No modifications for file '{drive_file.file_path}{drive_file.file_name}'. Skipping.")
        else:
            print(f"Backing up file '{drive_file.file_path}{drive_file.file_name}'...")
            drive_client.download_file(drive_file, backup_file_location)
            file_record_dictionary[drive_file.file_id] = drive_file.modified
            save_file_record(file_record_dictionary)
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

    file_record_dictionary = read_file_record()
    backup_files(drive_client, drive_files, backup_file_location, file_record_dictionary)
    save_file_record(file_record_dictionary)


if __name__ == "__main__":
    main()
