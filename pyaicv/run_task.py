"""
"""


import setup_aicv
setup_aicv.startup()


def run_tcbs_report():
    from aicv import tasks
    tasks.report_TCBS_customer_total_assets()