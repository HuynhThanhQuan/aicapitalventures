import os

# Set initial setup for credential, and token location
os.environ['AICV_KEY_GDRIVE_CRED'] = os.path.join(os.environ['AICV'], 'key', 'gdrive', 'credentials.json')
os.environ['AICV_KEY_GDRIVE_TOKEN'] = os.path.join(os.environ['AICV'], 'key', 'gdrive', 'token.json')
