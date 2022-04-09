import os

from drivedocsaver.src.drive_file import DriveFile
from drivedocsaver.src.file_util import (
    get_file_export,
    MIME_TYPES_TO_PREFERRED_EXPORT_TYPE,
    MIME_TYPES_TO_FILE_EXTENSION,
)


class TestFileUtil:
    def test_get_file_export(self):
        export_links = {
            "bad-type": "url1",
            "application/vnd.oasis.opendocument.text": "url2",
        }
        drive_file = DriveFile(
            "123",
            "file",
            "My Drive/test",
            "application/vnd.google-apps.document",
            export_links,
            "2022-04-01T23:18:52.128Z",
            10,
        )
        backup_path = "backup"
        file_export = get_file_export(backup_path, drive_file)
        assert file_export.backup_file_path == os.path.join(
            backup_path, drive_file.file_path, f"{drive_file.file_name}.odt"
        )
        assert file_export.mime_type == "application/vnd.oasis.opendocument.text"
        assert file_export.download_url == "url2"

    def test_mime_to_extension(self):
        # We need to ensure that every export type has an associated file extension
        for mime_type, export_types in MIME_TYPES_TO_PREFERRED_EXPORT_TYPE.items():
            for export_type in export_types:
                assert MIME_TYPES_TO_FILE_EXTENSION[export_type]
