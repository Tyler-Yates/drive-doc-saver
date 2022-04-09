from drivedocsaver.src.drive_file import DriveFile

EXPORT_LINKS_1 = {
    "bad-type": "url1",
    "application/vnd.oasis.opendocument.text": "url2",
}
DRIVE_FILE_1 = DriveFile(
    "123",
    "file",
    "My Drive/test",
    "application/vnd.google-apps.document",
    EXPORT_LINKS_1,
    "2022-04-01T23:18:52.128Z",
    10,
)
