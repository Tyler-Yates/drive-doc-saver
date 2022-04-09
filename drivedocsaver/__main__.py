import sys

from drivedocsaver.src.backup_util import backup_files
from drivedocsaver.src.drive_client import DriveClient

CLIENT_SECRETS_FILE_NAME = "client_secrets.json"


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
