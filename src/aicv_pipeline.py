import os
import setup
import credential
import gdrive
import tcbs
import pandas as pd
import aicv_core


def startup():
    gdrive.download_TCBS_transaction_history()
    tcbs.upload_reviewed_verified_records()


def run_TCBS_analysis():
    TCBS_txn_fp = os.path.join(os.environ['AICV_DATABASE_DRIVE'], 'Review_Verified_records.xlsx')
    TCBS_data = pd.read_excel(TCBS_txn_fp, index_col=0)
    aicv_core.get_analyzer(security='TCBS').analyze(TCBS_data)


def export_report():
    aicv_core.get_default_analyzer().export_summary_report()