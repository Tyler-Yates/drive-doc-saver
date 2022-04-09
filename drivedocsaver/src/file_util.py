import os
from typing import List

from drivedocsaver.src.drive_file import DriveFile

# Reference: https://developers.google.com/drive/api/v3/mime-types
from drivedocsaver.src.file_export import FileExport

MIME_TYPES_TO_PREFERRED_EXPORT_TYPE = {
    "application/vnd.google-apps.document": ["application/vnd.oasis.opendocument.text", "application/pdf"],
    "application/vnd.google-apps.spreadsheet": ["application/vnd.oasis.opendocument.spreadsheet", "text/csv"],
}

MIME_TYPES_TO_FILE_EXTENSION = {
    "application/vnd.oasis.opendocument.text": "odt",
    "application/pdf": "pdf",
    "application/vnd.oasis.opendocument.spreadsheet": "ods",
    "text/csv": "csv",
}


def get_file_export(backup_path: str, drive_file: DriveFile) -> FileExport:
    preferred_export_types: List[str] = MIME_TYPES_TO_PREFERRED_EXPORT_TYPE.get(drive_file.mime_type, [])
    for preferred_export_type in preferred_export_types:
        if preferred_export_type in drive_file.export_links.keys():
            file_extension = MIME_TYPES_TO_FILE_EXTENSION[preferred_export_type]
            backup_file_path = os.path.join(
                backup_path, drive_file.file_path, f"{drive_file.file_name}.{file_extension}"
            )
            download_url = drive_file.export_links[preferred_export_type]
            return FileExport(download_url, preferred_export_type, backup_file_path)

    raise ValueError("Could not find acceptable MIME type to download as!")
