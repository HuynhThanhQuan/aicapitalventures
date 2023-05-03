import os
import setup
import credential


if __name__=='__main__':
    print(os.environ.get('AICV'))
    print(os.environ['AICV_KEY_GDRIVE_CRED'])
    print(os.environ['AICV_KEY_GDRIVE_TOKEN'])
    print(credential.get_read_only_credentials())