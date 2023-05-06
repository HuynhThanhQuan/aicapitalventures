#
# Please refer this OAuth 2.0 Scopes for Google APIs: https://developers.google.com/identity/protocols/oauth2/scopes
#
#
#
#

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Set initial setup for credential, and token location
os.environ['AICV_KEY_GDRIVE_CRED'] = os.path.join(os.environ['AICV'], 'key', 'gdrive', 'client_secret.json')
os.environ['AICV_KEY_GDRIVE_TOKEN'] = os.path.join(os.environ['AICV'], 'key', 'gdrive', 'token.json')


SCOPE_EDIT = 'https://www.googleapis.com/auth/drive'
SCOPE_READONLY = 'https://www.googleapis.com/auth/drive.readonly'
SCOPE_METADATA = 'https://www.googleapis.com/auth/drive.metadata'


CRED_FILE = os.environ['AICV_KEY_GDRIVE_CRED']
TOKEN_FILE = os.environ['AICV_KEY_GDRIVE_TOKEN']


def get_read_only_credentials() -> Credentials:
    return get_credentials([SCOPE_READONLY])


def get_credentials(scopes) -> Credentials:
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    creds = None
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
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds
