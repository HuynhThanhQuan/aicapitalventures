#
# Please refer this OAuth 2.0 Scopes for Google APIs: https://developers.google.com/identity/protocols/oauth2/scopes
# Default token will be READ-ONLY credentials to ensure the compromised actions that could affect the data
# Token of EDIT credentials will not be saved, instead using directly and release after using it
#
#

import os
import shutil
import json
from datetime import datetime
from credential_exception import *
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Set initial setup for credential, and token location
os.environ['AICV_KEY_GDRIVE'] = os.path.join(os.environ['AICV'], 'key', 'gdrive')

SCOPE_EDIT      = 'https://www.googleapis.com/auth/drive'
SCOPE_READONLY  = 'https://www.googleapis.com/auth/drive.readonly'
SCOPE_METADATA  = 'https://www.googleapis.com/auth/drive.metadata'


GDRIVE = os.environ['AICV_KEY_GDRIVE']
TOKEN_FILE = os.path.join(GDRIVE, 'token.json')

# TOKEN MANAGEMENT


class TokenMetadata:
    """Class to manage all tokens for editing creds"""
    def __init__(self, metadata_filepath, expiry_duration=3600):
        self.metadata_filepath=metadata_filepath
        self.expiry_duration=expiry_duration
        self.metadata_dir = os.path.dirname(metadata_filepath)
        self.format_datetime = '%Y-%m-%dT%H:%M:%S.%fZ'

    def init_empty_metadata(self):
        self.token_id = []                  
        self.file = {}                
        self.expiry = {}             
        self.scopes = {}                     
        self.metadata = {
            'token_id': [],
            'file': {},
            'expiry': {},
            'scopes': {}
        }
        return self.metadata

    def add_token(self, id:str, scopes:str):
        curr = datetime.now()
        self.token_id.append(id)
        self.file[id] = os.path.join(self.metadata_dir, id + '.json')
        self.expiry[id] = (curr + self.expiry_duration).strftime(self.format_datetime)
        self.scopes[id] = scopes

    def remove_token(self, id:str):
        self.token_id.remove(id)
        del self.file[id]
        del self.expiry[id]
        del self.scopes[id]

    def check_valid_token(self, id:str):
        if not id in self.token_id:
            return False
        curr = datetime.now()
        expired_time = datetime.strptime(self.expiry[id], self.format_datetime)
        if curr <= expired_time:
            return True
        return False

    def update(self):
        existed_tokens = self.token_id.copy()
        for id in existed_tokens:
            if not self.check_valid_token(id):
                self.remove_token(id)

    def get_valid_tokenids(self):
        self.update()
        return self.token_id

    def trace_tokenId(self, filepath:str):
        """Return a traced token id of filepath if token-id is added else None"""
        tokenid = os.path.basename(filepath)
        tokenid = tokenid.replace('.json', '')
        if tokenid in self.token_id:
            return tokenid
        return None

    def read_metadata(self):
        json_meta = json.loads(open(self.metadata_filepath, 'r'))
        self.token_id = json_meta['token_id']
        self.file = json_meta['file']
        self.expiry = json_meta['expiry']
        self.scopes = json_meta['scopes']

    def write_metadata(self):
        self.metadata = {
            'token_id': self.token_id,
            'file': self.file,
            'expiry': self.expiry,
            'scopes': self.scopes
        }
        with open(self.metadata_filepath,'w') as f:
            f.write(self.metadata)
        return self.metadata_filepath

    def write_empty_metadata(self):
        self.init_empty_metadata()
        return self.write_metadata()


class TokenManagement:
    def __init__(self, cache_duration=3600):
        self.default_credentials = None
        self.init_setup()
        self.init_token_cache(cache_duration=cache_duration)

    def init_setup(self):
        self.cred_file = os.path.join(os.environ['AICV_KEY_GDRIVE'], 'client_secret.json')
        self.default_token_file = os.path.join(os.environ['AICV_KEY_GDRIVE'], 'token.json')

    def init_token_cache(self, cache_duration):
        """Init token cache"""
        self.cache_store = os.path.join(GDRIVE, 'tmp')
        # Init cache
        if not os.path.exists(self.cache_store):
            os.mkdir(self.cache_store)
        self.cache_duration = cache_duration
        self.scan_token_cache()

    def scan_token_cache(self):
        # Init TokenMetadata inst to manage all tokens
        meta_filepath = os.path.join(self.cache_store, 'metadata.json')
        self.token_metadata = TokenMetadata(meta_filepath, expiry_duration=self.cache_duration)
        # List all token json files
        existing_token_files = [i for i in os.listdir(self.cache_store) if 'metadata.json' not in i]

        # If no metadata file then delete all existing token files 
        # and write empty metadata file
        if not os.path.exists(meta_filepath):
            for f in existing_token_files:
                os.remove(os.path.join(self.cache_store,f))
            self.token_metadata.write_empty_metadata()

        # Read token metadata
        self.token_metadata.read_metadata()

        # Remove all redundant token ids/files that not listed in metadata or not presented in cache storage
        metadata_tokenids = self.token_metadata.get_valid_tokenids()
        existing_tokenids = [i.replace('.json', '') for i in existing_token_files]
        removed_tokenids = (set(existing_tokenids) | set(metadata_tokenids)) - (set(existing_tokenids) & set(metadata_tokenids))
        for id in removed_tokenids:
            f = os.path.join(self.cache_store, id + '.json')
            os.remove(f)
            self.token_metadata.remove_token(id)
        
    def __request_new_token(self, scopes):
        flow = InstalledAppFlow.from_client_secrets_file(self.cred_file, scopes)
        creds = flow.run_local_server(port=0)
        return creds

    def __save_tmp_token(self, creds:Credentials):
        if creds is not None:
            token_filepath = os.path.join(self.cache_store, creds.token + '.json')
            with open(token_filepath, 'w') as token_file:
                token_file.write(creds.to_json())
            return token_filepath

    def get_default_credentials(self):
        default_scopes = [SCOPE_READONLY]
        # Reclaim default token
        if os.path.exists(self.default_token_file):
            self.default_credentials = Credentials.from_authorized_user_file(self.default_token_file)
        # Check valid token
        if not self.default_credentials or not self.default_credentials.valid:
            # Check expired token and refresh token
            if self.default_credentials and self.default_credentials.expired and self.default_credentials.refresh_token:
                # make request with refresh token
                self.default_credentials.refresh(Request())
            else:
                # request new token
                self.default_credentials = self.__request_new_token(default_scopes)
        return self.default_credentials

    def get_readonly_credentials(self):
        return self.get_default_credentials()

    def get_edit_credentials(self):
        edit_creds = None
        # Check if TokenMetadata contains valid token for editing creds
        valid_edit_tokens = self.token_metadata.get_valid_tokenids()
        if len(valid_edit_tokens) != 0:
            sel_token = valid_edit_tokens[0]
            edit_creds = Credentials.from_authorized_user_file(self.default_token_file)
        else:
            # Create edit token and store it
            scopes = [SCOPE_EDIT]
            edit_creds = self.__request_new_token(scopes)
            self.__save_tmp_token(edit_creds)
            self.token_metadata.add_token(edit_creds.token, scopes)
        if edit_creds is None:
            raise EditCredentialError
        return edit_creds

token_management = TokenManagement()


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
