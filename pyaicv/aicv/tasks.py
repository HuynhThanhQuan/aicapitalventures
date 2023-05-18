from . import pipeline

def report_TCBS_customer_total_assets():
    pipeline.set_security_firm('TCBS')
    pipeline.run_analysis()
    pipeline.export_report()
