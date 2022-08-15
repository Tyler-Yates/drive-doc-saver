import os.path

from drivedocsaver.src.drive_file import DriveFile


class TestDriveFile:
    def test_file_name_valid_1(self):
        file_name = "Test File"
        drive_file = DriveFile("id", file_name, "/path/", "mime", {}, "2022-01-01", 1)
        assert drive_file.file_name == file_name

    def test_file_name_valid_2(self):
        file_name = "myfile_test_2022"
        drive_file = DriveFile("id", file_name, "/path/", "mime", {}, "2022-01-01", 1)
        assert drive_file.file_name == file_name

    def test_file_name_invalid_1(self):
        file_name = "Test: With Colon"
        drive_file = DriveFile("id", file_name, "/path/", "mime", {}, "2022-01-01", 1)
        assert drive_file.file_name == "Test - With Colon"

    def test_file_name_invalid_2(self):
        file_name = "Test!?* With Punctuation"
        drive_file = DriveFile("id", file_name, "/path/", "mime", {}, "2022-01-01", 1)
        assert drive_file.file_name == "Test With Punctuation"

    def test_file_path_valid_1(self):
        file_path = "Test File"
        drive_file = DriveFile("id", "file", file_path, "mime", {}, "2022-01-01", 1)
        assert drive_file.file_path == file_path

    def test_file_path_valid_2(self):
        file_path_parts = ["Test Directory", "Bob"]
        file_path = "/" + "/".join(file_path_parts)
        drive_file = DriveFile("id", "file", file_path, "mime", {}, "2022-01-01", 1)
        assert drive_file.file_path == os.path.sep.join(file_path_parts)

    def test_file_path_valid_3(self):
        file_path_parts = ["Test Directory", "Bob"]
        file_path = "/" + "\\".join(file_path_parts)
        drive_file = DriveFile("id", "file", file_path, "mime", {}, "2022-01-01", 1)
        assert drive_file.file_path == os.path.sep.join(file_path_parts)

    def test_file_path_valid_4(self):
        file_path_parts = ["Test Directory", "Bob"]
        file_path = "\\" + "\\".join(file_path_parts)
        drive_file = DriveFile("id", "file", file_path, "mime", {}, "2022-01-01", 1)
        assert drive_file.file_path == os.path.sep.join(file_path_parts)

    def test_file_path_invalid_1(self):
        file_path = "Test: With Colon"
        drive_file = DriveFile("id", "file", file_path, "mime", {}, "2022-01-01", 1)
        assert drive_file.file_path == "Test - With Colon"

    def test_file_path_invalid_2(self):
        file_path = "Test!?* With Punctuation"
        drive_file = DriveFile("id", "file", file_path, "mime", {}, "2022-01-01", 1)
        assert drive_file.file_path == "Test With Punctuation"
