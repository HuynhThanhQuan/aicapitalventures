import os
import setup
import credential
import gdrive
import tcbs
import pandas as pd



def startup(mode=None):
    if mode=='debug':
        # Debug mode
        print('DEBUG MODE')
        
    else:
        # Prod mode
        print('PROD MODE')
        gdrive.download_TCBS_transaction_history()
        tcbs.upload_reviewed_verified_records()



def run_TCBS_analysis():
    TCBS_data = os.environ['AICV_TCBS_TRANSACTION_HISTORY']
    TCBS_data = pd.read_excel(TCBS_data, index_col=0)
    print(TCBS_data)