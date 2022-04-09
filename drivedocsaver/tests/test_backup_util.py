import os.path
import tempfile
from unittest import mock
from unittest.mock import ANY

from drivedocsaver.src.backup_util import backup_files, TRASH_PATH
from drivedocsaver.src.file_util import get_file_export
from drivedocsaver.tests.constants import DRIVE_FILE_1


class TestBackupUtil:
    def test_backup_files_trash(self):
        drive_client = mock.Mock()
        with tempfile.TemporaryDirectory() as backup_path:
            # Create a test file that does not exist in Google Drive
            temp_file_name = "temp.txt"
            tmp_file_path = os.path.join(backup_path, temp_file_name)
            with open(tmp_file_path, mode="w") as temp_file:
                temp_file.write("test")

            # The backup should move the file to the trash
            backup_files(drive_client, [], backup_path)

            files_in_backup = set()
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_in_backup.add(file_path)

            # The file we created should have moved to the trash
            assert {os.path.join(backup_path, TRASH_PATH, temp_file_name)} == files_in_backup

    def test_backup_files_normal(self):
        drive_client = mock.Mock()
        # Backup file that does not exist locally
        drive_file = DRIVE_FILE_1

        backup_files(drive_client, [drive_file], "backup")

        drive_client.download_file.assert_called_once_with(ANY, drive_file)

    def test_backup_files_local_modification(self):
        drive_client = mock.Mock()
        with tempfile.TemporaryDirectory() as backup_path:
            # Backup file that already exists locally with changes
            drive_file = DRIVE_FILE_1
            file_export = get_file_export(backup_path, drive_file)
            os.makedirs(os.path.dirname(file_export.backup_file_path), exist_ok=True)
            with open(file_export.backup_file_path, mode="w") as temp_file:
                temp_file.write("test")

            files_in_backup_start = set()
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_in_backup_start.add(file_path)

            backup_files(drive_client, [drive_file], backup_path)

            # We should not make a call to download the file
            drive_client.download_file.assert_not_called()

            # No files should change on disk
            files_in_backup_end = set()
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_in_backup_end.add(file_path)

            assert files_in_backup_start == files_in_backup_end
