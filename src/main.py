import os
import setup
import credential
import gdrive
import tcbs


if __name__=='__main__':
    # print(os.environ.get('AICV'))
    # print(os.environ['AICV_KEY_GDRIVE_CRED'])
    # print(os.environ['AICV_KEY_GDRIVE_TOKEN'])
    # print(credential.get_read_only_credentials())
    # print(gdrive.search_transaction_history_files())
    # print(gdrive.download_TCBS_transaction_history())
    # f = tcbs.list_TCBS_transaction_history()[0]
    print(tcbs.get_latest_transaction_table())