import os

# Set initial setup for credential, and token location
os.environ['AICV_GDRIVE_CRED'] = os.path.join(os.environ['AICV'], 'key', 'gdrive', 'credentials.json')