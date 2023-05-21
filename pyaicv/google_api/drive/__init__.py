"""
Google Workspace & Google Drive supported MIME types: https://developers.google.com/drive/api/guides/mime-types
"""

import io
import os
import logging

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload

from pyaicv.google_api.drive.exception import *
from pyaicv.google_api import credential


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# DRIVE_LOCAL_STORE = os.environ['AICV_DATABASE_DRIVE']
# DRIVE_REMOTE_ID_STORE = None


# def fetch_remote_AICV_folderID():
#     global DRIVE_REMOTE_ID_STORE
#     """Search file in drive location"""
#     try:
#         service = build('drive', 'v3', credentials=credential.get_read_only_credentials())
#         files = []
#         page_token = None
#         while True:
#             response = service.files().list(q="name contains 'AICapitalVentures' and mimeType='application/vnd.google-apps.folder'",
#                                             spaces='drive',
#                                             fields='nextPageToken, '
#                                                    'files(id, name, mimeType)',
#                                             pageToken=page_token).execute()
#             files.extend(response.get('files', []))
#             page_token = response.get('nextPageToken', None)
#             if page_token is None:
#                 break
#     except HttpError as error:
#         logger.exception(F'An error occurred: {error}')
#         files = None
#     if len(files) == 0:
#         raise AICapitalVenturesRemoteNotFound("Unable to fetch AI Capital Ventures on Drive store")
#     elif len(files) > 1:
#         raise AICapitalVenturesRemoteDuplicated("Found more than 1 AI Capital Ventures repository")
#     else:
#         DRIVE_REMOTE_ID_STORE = files[0]['id']
#         logger.debug(f'AI Capital Ventures Drive ID: {DRIVE_REMOTE_ID_STORE}')


# fetch_remote_AICV_folderID()



"""
Service functions
"""

def search(query_statement, spaces='drive', fields='nextPageToken,files(id, name, mimeType)', page_token=None) -> list[dict]:
    try:
        service = build('drive', 'v3', credentials=credential.get_read_only_credentials())
        files = []
        page_token = page_token
        while True:
            response = service.files().list(
                q=query_statement,
                spaces=spaces,
                fields=fields,
                pageToken=page_token).execute()
            files.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
    except HttpError as error:
        logger.exception(F'An error occurred: {error}')
        files = None
    return files


def delete_drive_file(file_id:str):
    try:
        service = build('drive', 'v3', credentials=credential.get_edit_credentials())
        request = service.files().delete(fileId=file_id).execute()
        logger.info(f'Deleted file with ID "{file_id}"')
    except HttpError as error:
        logger.exception(F'An error occurred: {error}')


def download_blob_file(file_id:str, saved_file:str) -> io.FileIO:
    try:
        service = build('drive', 'v3', credentials=credential.get_read_only_credentials())
        request = service.files().get_media(fileId=file_id)
        file = io.FileIO(saved_file, 'wb')
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.debug(F'Download file "{os.path.basename(saved_file)}" -> {int(status.progress() * 100)}% with file-id: {file_id}')
    except HttpError as error:
        logger.exception(F'An error occurred: {error}')
        file = None
    return file


def download_DocEditor_file(file_id:str, mimeType:str, saved_file:str):
    try:
        service = build('drive', 'v3', credentials=credential.get_read_only_credentials())
        request = service.files().export_media(fileId=file_id, mimeType=mimeType)
        file = io.FileIO(saved_file, 'wb')
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.debug(F'Download Doc file "{os.path.basename(saved_file)}" -> {int(status.progress() * 100)}% with file-id: {file_id}')
    except HttpError as error:
        logger.exception(F'An error occurred: {error}')
        file = None
    return file



def upload_DocEditor_file(filepath:str, mimeType:str, metadata:dict, resumable=True, fields='id'):
    try:
        service = build('drive', 'v3', credentials=credential.get_edit_credentials())
        media = MediaFileUpload(filepath, mimetype=mimeType,resumable=resumable)
        file = service.files().create(body=metadata, media_body=media, fields=fields).execute()
        logger.info(F'File with ID "{file.get("id")}" has been uploaded.')
    except HttpError as error:
        logger.exception(F'An error occurred: {error}')
        file = None
    return file


"""
"""

# def download_verified_record(id, saved_file):
#     file_info = download_Docs_Editor_file(id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', saved_file=saved_file)
#     return file_info


# def search_verified_records() -> list[dict]:
#     query_statement = f"name = 'Verified_records.xlsx' and parents in '{DRIVE_REMOTE_ID_STORE}' and trashed=false"
#     fields = 'nextPageToken, files(id, name, mimeType, parents, createdTime)'
#     files = search(query_statement, fields=fields)
#     if len(files) > 0:
#         logger.debug(f'Searched "Verified_records.xlsx" with IDs {[f["id"] for f in files]} in Drive')
#     return files


def search_capital_file() -> list[dict]:
    query_statement = f"name = 'Capital' and parents in '{DRIVE_REMOTE_ID_STORE}' and trashed=false"
    fields = 'nextPageToken, files(id, name, mimeType, parents, createdTime)'
    files = search(query_statement, fields=fields)
    if len(files) > 0:
        logger.debug(f'Searched "Capital" with IDs {[f["id"] for f in files]} in Drive')
    return files[0]




