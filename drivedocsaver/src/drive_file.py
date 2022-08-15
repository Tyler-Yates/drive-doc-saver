import calendar
import os.path
import re
from typing import Dict

from dateutil import parser


class DriveFile:
    def __init__(
        self,
        file_id: str,
        file_name: str,
        file_path: str,
        mime_type: str,
        export_links: Dict[str, str],
        modified: str,
        version: int,
    ):
        self.file_id = file_id
        self.file_name = self._slugify_file_name(file_name)
        self.file_path = self._slugify_file_path(
            file_path.lstrip("/").lstrip("\\").replace("/", os.path.sep).replace("\\", os.path.sep)
        )
        self.mime_type = mime_type
        self.export_links = export_links
        self.modified = modified
        self.modified_unix_timestamp = int(calendar.timegm((parser.parse(self.modified).timetuple())))
        self.version = version

    @staticmethod
    def _slugify_file_name(file_name: str) -> str:
        value = str(file_name)
        value = value.replace(":", " -")
        return re.sub(r"[^\w\s.-]", "", value)

    @staticmethod
    def _slugify_file_path(file_name: str) -> str:
        value = str(file_name)
        value = value.replace(":", " -")
        return re.sub(r"[^\w\s/\\.-]", "", value)
