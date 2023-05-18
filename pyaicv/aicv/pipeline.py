import os

import pandas as pd

from pyaicv.security import factory as sec_factory

from . import analyser as als


def set_security_firm(security):
    sec_factory.set(security)

def run_analysis():
    als.get_analyser(sec_factory.get_active_security())
    drive.download_TCBS_transaction_history()
    

def export_report():
    alz.get_default_analyser().export_summary_report()

    # 
    # ops.upload_reviewed_verified_records()




# def run_TCBS_analysis():
#     TCBS_txn_fp = os.path.join(os.environ['AICV_DATABASE_DRIVE'], 'Review_Verified_records.xlsx')
#     TCBS_data = pd.read_excel(TCBS_txn_fp, index_col=0)
#     alz.get_analyser(security='TCBS').analyze(TCBS_data)


