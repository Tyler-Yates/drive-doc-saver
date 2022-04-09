import calendar
import os.path
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
        self.file_name = file_name.replace(os.path.sep, "")
        self.file_path = file_path.lstrip("/").replace("/", os.path.sep)
        self.mime_type = mime_type
        self.export_links = export_links
        self.modified = modified
        self.modified_unix_timestamp = int(calendar.timegm((parser.parse(self.modified).timetuple())))
        self.version = version
