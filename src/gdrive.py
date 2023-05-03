#
#
#
#
#
# Google Workspace & Google Drive supported MIME types: https://developers.google.com/drive/api/guides/mime-types

import io
import os
import credential
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

CREDS = credential.get_read_only_credentials()


os.environ['AICV_DRIVE'] = os.path.join(os.environ['AICV'], 'database', 'drive')

DRIVE_STORE = os.environ['AICV_DRIVE']


def search_transaction_history_files():
    """Search file in drive location
    """
    try:
        service = build('drive', 'v3', credentials=CREDS)
        files = []
        page_token = None
        while True:
            response = service.files().list(q="name contains 'Lịch sử giao dịch cổ phiếu_Huỳnh Thanh Quan' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'",
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name, mimeType)',
                                            pageToken=page_token).execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None
    return files


def download_blob_file(file_id, saved_file):
    try:
        service = build('drive', 'v3', credentials=CREDS)
        request = service.files().get_media(fileId=file_id)
        file = io.FileIO(saved_file, 'wb')
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(F'Download file {os.path.basename(saved_file)} {int(status.progress() * 100)}%')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    return file


def download_TCBS_transaction_history():
    files = search_transaction_history_files()
    files_info = []
    for i, f in enumerate(files):
        txn_file = os.path.join(DRIVE_STORE, f'TCBS_{i}.xlsx')
        files_info.append(download_blob_file(f['id'], txn_file))
    return files_info