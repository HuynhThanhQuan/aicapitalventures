import os

import pandas as pd

from . import analyser as alz
from ..google import credential, drive
from ..security.tcbs import ops



def startup():
    drive.download_TCBS_transaction_history()
    ops.upload_reviewed_verified_records()


def run_TCBS_analysis():
    TCBS_txn_fp = os.path.join(os.environ['AICV_DATABASE_DRIVE'], 'Review_Verified_records.xlsx')
    TCBS_data = pd.read_excel(TCBS_txn_fp, index_col=0)
    alz.get_analyser(security='TCBS').analyze(TCBS_data)


def export_report():
    alz.get_default_analyser().export_summary_report()