#
# Please refer this OAuth 2.0 Scopes for Google APIs: https://developers.google.com/identity/protocols/oauth2/scopes
# Default token will be READ-ONLY credentials to ensure the compromised actions that could affect the data
# Token of EDIT credentials will not be saved, instead using directly and release after using it
#
#

import os
import shutil
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Set initial setup for credential, and token location
os.environ['AICV_KEY_GDRIVE'] = os.path.join(os.environ['AICV'], 'key', 'gdrive')

SCOPE_EDIT = 'https://www.googleapis.com/auth/drive'
SCOPE_READONLY = 'https://www.googleapis.com/auth/drive.readonly'
SCOPE_METADATA = 'https://www.googleapis.com/auth/drive.metadata'


GDRIVE = os.environ['AICV_KEY_GDRIVE']
TOKEN_FILE = os.path.join(GDRIVE, 'token.json')

# TOKEN MANAGEMENT
class TokenManagement:
    def __init__(self):
        self.default_cred = None
        self.init_setup()

    def init_setup(self):
        self.cred_file = os.path.join(os.environ['AICV_KEY_GDRIVE'], 'client_secret.json')
        self.default_token_file = os.path.join(os.environ['AICV_KEY_GDRIVE'], 'token.json')
        self.temp_token_file = os.path.join(os.environ['AICV_KEY_GDRIVE'], 'temp_token.json')

    def init_temp_token_memories(self):
        self.token_id = {}          # mapping tokenID and Credential object, dict(str:Credentials)
        self.token_file = {}        # mapping tokenID and saved file json, dict(str:str)
        self.expired_time = {}      # mapping tokenID and expired time, dict(str: datetime.datetime)
        self.scope = {}             # mapping scope and tokenID, dict(str:str)

    def prune_expired_tokens(self):
        current = datetime.now()
        for k, v in self.expired_time.items():
            if v < current:
                self.delete_token_id(k)

    def delete_token_id(self, id):
        if self.token_id[id] is not None:
            os.remove(self.token_id[id])

    def get(self,):
        self.prune_expired_tokens()

    def _request_new_token(self, scopes):
        flow = InstalledAppFlow.from_client_secrets_file(self.cred_file, scopes)
        creds = flow.run_local_server(port=0)
        return creds

    def get_default_token(self):
        default_scopes = [SCOPE_READONLY]
        # Reclaim default token
        if os.path.exists(self.default_token_file):
            self.default_cred = Credentials.from_authorized_user_file(self.default_token_file, default_scopes)
        # Check valid token
        if not self.default_cred or not self.default_cred.valid:
            # Check expired token
            if self.default_cred and self.default_cred.expired and self.default_cred.refresh_token:
                self.default_cred.refresh(Request())
            else:
                # request new token with refresh token
                self.default_cred = self._request_new_token(default_scopes)
        return self.default_cred



def get_credentials(scopes, reset_token=False, saved=False) -> Credentials:
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    creds = None
    if reset_token is False:
        # Reuse token
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            if saved:
                with open(TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
    else:
        # Bypass old token and download new token
        flow = InstalledAppFlow.from_client_secrets_file(CRED_FILE, scopes)
        creds = flow.run_local_server(port=0)
        if saved:
            with open(TOKEN_FILE, 'w') as token:
                token.write(creds.to_json())
    return creds


def get_read_only_credentials() -> Credentials:
    return get_credentials([SCOPE_READONLY], reset_token=False, saved=True)


def get_edit_credentials() -> Credentials:
    return get_credentials([SCOPE_EDIT], reset_token=True,saved=False)
