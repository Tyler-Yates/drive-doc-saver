import os
import pickle
import re
from typing import Optional

import google_auth_httplib2
import google_auth_oauthlib.flow
import googleapiclient.discovery
import httplib2
import requests
from google.auth.credentials import Credentials
from google.auth.exceptions import RefreshError

from drivedocsaver.src.drive_file import DriveFile

MAX_RESULTS = 500

CREDENTIALS_FILE = "credentials.pickle"

API_SERVICE_NAME = "drive"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

FILES_LIST_FIELDS = "nextPageToken,files(kind,id,name,trashed,mimeType,parents,exportLinks,modifiedTime)"

# Reference: https://developers.google.com/drive/api/v3/mime-types
MIME_TYPES_TO_PREFERRED_EXPORT_TYPE = {
    "application/vnd.google-apps.document": ["application/vnd.oasis.opendocument.text", "application/pdf"],
    "application/vnd.google-apps.spreadsheet": ["application/vnd.oasis.opendocument.spreadsheet", "text/csv"],
}


class DriveClient:
    def __init__(self, client_secrets_file_name: str):
        self.file_id_to_path = dict()

        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        self.credentials: Optional[Credentials] = None

        # See if the credentials are already saved locally
        if os.path.exists(CREDENTIALS_FILE):
            print("Loading credentials from file...")
            with open(CREDENTIALS_FILE, mode="rb") as credentials_file:
                self.credentials = pickle.load(credentials_file)

        # Try to refresh the token first
        self.refresh_token()

        # If we do not have credentials then we need to fetch them from scratch
        if not self.credentials or not self.credentials.valid:
            # Get credentials and create an API client
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file_name, SCOPES)
            self.credentials = flow.run_local_server()

            # Save the credentials for the next run
            with open(CREDENTIALS_FILE, "wb") as f:
                print("Saving Credentials for future use...")
                pickle.dump(self.credentials, f)

        # Create the Drive client
        self.gdrive = googleapiclient.discovery.build(API_SERVICE_NAME, API_VERSION, credentials=self.credentials)

    def refresh_token(self):
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            # We have expired credentials so we can just refresh them
            print("Refreshing access token...")
            http = httplib2.Http()
            request = google_auth_httplib2.Request(http)
            try:
                self.credentials.refresh(request)
            except RefreshError:
                print("Refresh token has expired. Must generate a new one.")

    def get_file_path(self, file_id: str):
        # We can safely assume only one parent: https://developers.google.com/drive/api/v3/ref-single-parent
        response = self.gdrive.files().get(fileId=file_id, fields="parents").execute()
        parent_id_list = response.get("parents", [None])
        return self._get_file_path(parent_id_list[0])

    def _get_file_path(self, file_id):
        if file_id is None:
            return "/"

        if file_id in self.file_id_to_path:
            return self.file_id_to_path[file_id]

        file_response = self.gdrive.files().get(fileId=file_id, fields="name,parents").execute()
        file_name = file_response["name"].replace(os.path.sep, "|")
        parent_id_list = file_response.get("parents", [None])

        file_path = self._get_file_path(parent_id_list[0]) + file_name + os.path.sep
        self.file_id_to_path[file_id] = file_path
        return file_path

    @staticmethod
    def _get_filename_from_response(response) -> str:
        # TODO better error handling
        return re.findall('filename="(.+)"', response.headers.get("Content-Disposition"))[0]

    def _download_file(self, file_url: str, drive_file: DriveFile, backup_location: str):
        # Tokens are very short-lived so we need to refresh ours
        self.refresh_token()

        response = requests.get(
            file_url, allow_redirects=True, headers={"Authorization": f"Bearer {self.credentials.token}"}
        )
        file_name = self._get_filename_from_response(response)
        file_path_without_leading_slash = drive_file.file_path.lstrip(os.path.sep)

        backup_folder = os.path.join(backup_location, file_path_without_leading_slash)
        os.makedirs(backup_folder, exist_ok=True)

        with open(os.path.join(backup_folder, file_name), "wb") as output_file:
            output_file.write(response.content)

    def download_file(self, drive_file: DriveFile, backup_location: str):
        preferred_export_types = MIME_TYPES_TO_PREFERRED_EXPORT_TYPE.get(drive_file.mime_type, [])
        for preferred_export_type in preferred_export_types:
            if preferred_export_type in drive_file.export_links.keys():
                file_url = drive_file.export_links[preferred_export_type]
                self._download_file(file_url, drive_file, backup_location)
                return

        raise ValueError("Could not find acceptable MIME type to download as!")

    def get_google_doc_files(self):
        google_doc_files = []
        for mime_type in MIME_TYPES_TO_PREFERRED_EXPORT_TYPE.keys():
            google_doc_files.extend(self._get_google_doc_files(mime_type))
        return google_doc_files

    def _get_google_doc_files(self, mime_type: str):
        google_doc_files = []
        request = self.gdrive.files().list(
            fields=FILES_LIST_FIELDS, pageSize=MAX_RESULTS, q=f"mimeType='{mime_type}' and 'me' in owners"
        )
        response = request.execute()

        while response is not None:
            for file_json in response["files"]:
                file_id = file_json["id"]
                file_name = file_json["name"]
                mime_type = file_json["mimeType"]
                file_path = self.get_file_path(file_id)
                export_links = file_json["exportLinks"]
                modified_time = file_json["modifiedTime"]

                print(f"Found file '{file_path}{file_name}' with MIME type {mime_type}")
                google_doc_files.append(
                    DriveFile(file_id, file_name, file_path, mime_type, export_links, modified_time)
                )
            if response.get("nextPageToken"):
                response = (
                    self.gdrive.files()
                    .list(
                        fields=FILES_LIST_FIELDS,
                        pageSize=MAX_RESULTS,
                        pageToken=response["nextPageToken"],
                        q=f"mimeType='{mime_type}' and 'me' in owners",
                    )
                    .execute()
                )
            else:
                response = None

        return google_doc_files
