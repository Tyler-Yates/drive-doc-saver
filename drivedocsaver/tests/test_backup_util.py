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

    def test_backup_files_trash_already_exists(self):
        drive_client = mock.Mock()
        with tempfile.TemporaryDirectory() as backup_path:
            # Create a test file that does not exist in Google Drive
            temp_file_name = "temp.txt"
            tmp_file_path = os.path.join(backup_path, temp_file_name)
            with open(tmp_file_path, mode="w") as temp_file:
                temp_file.write("test")

            expected_trash_location_1 = os.path.join(backup_path, TRASH_PATH, temp_file_name)
            expected_trash_location_2 = os.path.join(backup_path, TRASH_PATH, "temp_1.txt")

            # Create two files in the trash that will conflict with the file above
            os.makedirs(os.path.dirname(expected_trash_location_1), exist_ok=True)
            with open(expected_trash_location_1, mode="w") as temp_file:
                temp_file.write("bob1")
            with open(expected_trash_location_2, mode="w") as temp_file:
                temp_file.write("bob2")

            # The backup should move the file to the trash and auto-rename
            backup_files(drive_client, [], backup_path)

            files_in_backup = set()
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_in_backup.add(file_path)

            # The file we created should have moved to the trash and the existing two files in the trash should remain
            assert expected_trash_location_1 in files_in_backup
            assert expected_trash_location_2 in files_in_backup
            assert len(files_in_backup) == 3

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

            backup_files(drive_client, [drive_file], backup_path)

            # We should not make a call to download the file
            drive_client.download_file.assert_not_called()

            # The modified file should move to the trash
            files_in_backup = []
            for root, dirs, files in os.walk(backup_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_in_backup.append(file_path)

            assert 1 == len(files_in_backup)
            assert (TRASH_PATH in files_in_backup[0]) and (drive_file.file_name in files_in_backup[0])
