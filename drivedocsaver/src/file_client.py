import os
import pickle
from typing import Dict

from drivedocsaver.src.drive_file import DriveFile

FILE_RECORD_PICKLE_FILE_NAME = "file_records.pickle"


# TODO handle files that get deleted from Google Drive. Do we delete them from local?
# TODO also save file path so if files are moved we can detect that
class FileClient:
    def __init__(self, backup_file_location: str):
        self.backup_file_location = backup_file_location
        self.file_record_dict = self._read_file_record()

    def backup_drive_file(self, drive_file: DriveFile):
        pass

    def _save_file_record(self):
        with open(FILE_RECORD_PICKLE_FILE_NAME, "wb") as handle:
            pickle.dump(self.file_record_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def _read_file_record() -> Dict[str, str]:
        if os.path.exists(FILE_RECORD_PICKLE_FILE_NAME):
            with open(FILE_RECORD_PICKLE_FILE_NAME, "rb") as handle:
                print("Found existing file record. Loading.")
                return pickle.load(handle)
        else:
            print("No file record found. Creating new.")
            return dict()
