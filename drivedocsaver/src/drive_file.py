from typing import Dict


class DriveFile:
    def __init__(
        self, file_id: str, file_name: str, file_path: str, mime_type: str, export_links: Dict[str, str], modified: str
    ):
        self.file_id = file_id
        self.file_name = file_name
        self.file_path = file_path
        self.mime_type = mime_type
        self.export_links = export_links
        self.modified = modified
