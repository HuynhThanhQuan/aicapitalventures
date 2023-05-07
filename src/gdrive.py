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
from googleapiclient.http import MediaFileUpload
from gdrive_exception import *


os.environ['AICV_DRIVE'] = os.path.join(os.environ['AICV'], 'database', 'drive')

DRIVE_LOCAL_STORE = os.environ['AICV_DRIVE']
DRIVE_REMOTE_ID_STORE = None


def get_remote_AICV_folderID():
    global DRIVE_REMOTE_ID_STORE
    """Search file in drive location"""
    try:
        service = build('drive', 'v3', credentials=credential.get_read_only_credentials())
        files = []
        page_token = None
        while True:
            response = service.files().list(q="name contains 'AICapitalVentures' and mimeType='application/vnd.google-apps.folder'",
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
    if len(files) == 0:
        raise AICapitalVenturesRemoteNotFound
    elif len(files) > 1:
        raise AICapitalVenturesRemoteDuplicated
    else:
        DRIVE_REMOTE_ID_STORE = files[0]['id']


get_remote_AICV_folderID()


def search_transaction_history_files() -> list[dict]:
    """Search file in drive location"""
    try:
        service = build('drive', 'v3', credentials=credential.get_read_only_credentials())
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


def search_verified_records() -> list[dict]:
    """Search file in drive location"""
    try:
        service = build('drive', 'v3', credentials=credential.get_read_only_credentials())
        files = []
        page_token = None
        while True:
            query_statement = f"name = 'Verified_records.xlsx' and parents in '{DRIVE_REMOTE_ID_STORE}' and trashed=false"
            response = service.files().list(q=query_statement,
                                            spaces='drive',
                                            fields='nextPageToken, '
                                                   'files(id, name, mimeType, parents, createdTime)',
                                            pageToken=page_token).execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

    except HttpError as error:
        print(F'An error occurred: {error}')
        files = None
    return files


def download_blob_file(file_id:str, saved_file:str) -> io.FileIO:
    try:
        service = build('drive', 'v3', credentials=credential.get_read_only_credentials())
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


def download_TCBS_transaction_history() -> list[io.FileIO]:
    files = search_transaction_history_files()
    files_info = []
    for i, f in enumerate(files):
        txn_file = os.path.join(DRIVE_LOCAL_STORE, f'TCBS_transaction_history_{i}.xlsx')
        files_info.append(download_blob_file(f['id'], txn_file))
    return files_info


def upload_verified_records_gdrive(filepath:str): 
    """Upload file with conversion
    Returns: ID of the file uploaded
    """
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=credential.get_edit_credentials())

        file_metadata = {
            'name': 'Verified_records.xlsx',
            'parents': [DRIVE_REMOTE_ID_STORE],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        media = MediaFileUpload(filepath, mimetype='application/vnd.google-apps.spreadsheet',resumable=True)
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File with ID: "{file.get("id")}" has been uploaded.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    return file.get('id')