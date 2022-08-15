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
