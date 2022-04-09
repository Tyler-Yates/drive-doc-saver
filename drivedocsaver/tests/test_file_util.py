import os

from drivedocsaver.src.file_util import (
    get_file_export,
    MIME_TYPES_TO_PREFERRED_EXPORT_TYPE,
    MIME_TYPES_TO_FILE_EXTENSION,
)
from drivedocsaver.tests.constants import DRIVE_FILE_1


class TestFileUtil:
    def test_get_file_export(self):
        backup_path = "backup"
        drive_file = DRIVE_FILE_1
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
