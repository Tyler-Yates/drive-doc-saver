import os.path
import random
import tempfile
from unittest import mock

from drivedocsaver.src.backup_util import backup_files, TRASH_PATH
from drivedocsaver.tests.temporary_directory import TemporaryDirectory


class TestBackupUtil:
    def test_backup_files_trash(self):
        drive_client = mock.Mock()
        with TemporaryDirectory() as backup_path:
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
