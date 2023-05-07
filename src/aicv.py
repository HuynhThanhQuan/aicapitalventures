import os
import setup
import credential
import gdrive
import tcbs

import aicv_core
import aicv_pipeline

"""
This is the system piple of AI Capital Ventures, including 3 mains steps:
1. Verification
    1.1 Data synchronize
        1.1.1 Synchronize TCBS transaction history
            1.1.1.1 Download latest TCBS transaction history
                1.1.1.1.1 Download all TCBS transaction history files
                1.1.1.1.2 Sort datetime in order
            1.1.1.2 Correct data type format
            1.1.1.3 Add manually insertion section for owner
        1.1.2 Verify TCBS transaction history
            1.1.2.1 Upload corrected TCBS transaction history into Drive
            1.1.2.2 Wait for manual verification
2. Insight
    2.1 Intepretation
    2.2 Explanation
3. Visualization
    3.1 Plotting
    3.2 Demostration
"""

def run():
    # 1. Verification
    gdrive.download_TCBS_transaction_history()
    tcbs.upload_verified_records()
