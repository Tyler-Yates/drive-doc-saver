import os.path
import sys

from drivedocsaver.src.backup_util import backup_files
from drivedocsaver.src.constants import CLIENT_SECRETS_FILE_NAME, EXPECTED_EMAIL_FILE_NAME
from drivedocsaver.src.drive_client import DriveClient


def main():
    if len(sys.argv) == 1:
        backup_path = ""
    elif len(sys.argv) == 2:
        backup_path = sys.argv[1]
    else:
        print("Incorrect number of arguments.")
        sys.exit(1)

    expected_email_address = _get_expected_email(backup_path)

    print(f"Backing up to location '{backup_path}'")
    drive_client = DriveClient(CLIENT_SECRETS_FILE_NAME, expected_email_address=expected_email_address)

    if expected_email_address is None:
        expected_email_path = os.path.join(backup_path, EXPECTED_EMAIL_FILE_NAME)
        with open(expected_email_path, "w") as expected_email_file:
            expected_email_file.write(drive_client.get_user_email())

    drive_files = drive_client.get_google_doc_files()

    print(f"Found {len(drive_files)} files to process...")

    backup_files(drive_client, drive_files, backup_path)


def _get_expected_email(backup_path: str) -> str:
    expected_email = None
    expected_email_path = os.path.join(backup_path, EXPECTED_EMAIL_FILE_NAME)
    if os.path.exists(expected_email_path):
        with open(expected_email_path, mode="r") as expected_email_file:
            expected_email = expected_email_file.readline().strip()

    print(f"Expected email for path {backup_path!r}: {expected_email!r}")
    return expected_email


if __name__ == "__main__":
    main()
