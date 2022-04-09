class FileExport:
    def __init__(self, download_url: str, mime_type: str, backup_file_path: str):
        self.download_url = download_url
        self.mime_type = mime_type
        self.backup_file_path = backup_file_path
