
import aicv_core
import aicv_pipeline

"""
This is the system piple of AI Capital Ventures, including 3 mains steps:
1. Verification
    1.1 Data synchronize
        External: exporter must down it from TCBS Invest manually and upload it to Drive
        Download all available TCBS transaction history 
        Get latest data by sort in export date
        Correct data type format
        Add manually insertion section for auditor
        Upload corrected TCBS transaction history into Drive
    1.2 Audit & Review
        1.2.1 Check missing transaction
        1.2.2 Replace the latest data in GDrive
        1.2.3 Wait for manual review
2. Insight
    2.1 Intepretation
    2.2 Explanation
3. Visualization
    3.1 Plotting
    3.2 Demostration
"""

def run(mode=None):
    """
    Run AI Capital Venture pipeline includes:
    1. Startup
    2. Run TCBS analysis
    3. Run report

    Input: mode: (None is production mode, 'debug' to run debug mode)
    """
    # 1. Verification
    aicv_pipeline.startup(mode)
    # 2. Insight
    aicv_pipeline.run_TCBS_analysis()
