import os
from typing import List

from drivedocsaver.src.drive_file import DriveFile

from drivedocsaver.src.file_export import FileExport

# References:
# https://developers.google.com/drive/api/v3/mime-types
# https://developers.google.com/drive/api/guides/ref-export-formats?hl=en
MIME_TYPES_TO_PREFERRED_EXPORT_TYPE = {
    "application/vnd.google-apps.document": ["application/vnd.oasis.opendocument.text", "application/pdf"],
    "application/vnd.google-apps.spreadsheet": ["application/vnd.oasis.opendocument.spreadsheet", "text/csv"],
    "application/vnd.google-apps.presentation": ["application/vnd.oasis.opendocument.presentation", "application/pdf"],
    "application/vnd.google-apps.drawing": ["image/svg+xml", "image/png"],
}

MIME_TYPES_TO_FILE_EXTENSION = {
    "application/vnd.oasis.opendocument.text": "odt",
    "application/pdf": "pdf",
    "application/vnd.oasis.opendocument.spreadsheet": "ods",
    "text/csv": "csv",
    "application/vnd.oasis.opendocument.presentation": "otp",
    "image/svg+xml": "svg",
    "image/png": "png",
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
