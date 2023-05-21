import pandas as pd
import os
import logging
from . import utils


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



def export_total_asset_value_report(data: pd.DataFrame) -> dict:
    date_rp = data.copy()
    date_rp = data.groupby('date')['TotalAssets'].last().dropna()
    week_rp = date_rp.copy().reset_index()
    week_rp['week'] = week_rp['date'].dt.isocalendar().week
    week_rp = week_rp.groupby('week')['TotalAssets'].last()
    month_rp = date_rp.copy().reset_index()
    month_rp['month'] = month_rp['date'].dt.month
    month_rp = month_rp.groupby('month')['TotalAssets'].last()
    return {
        'full': data,
        'date': date_rp,
        'week': week_rp,
        'month': month_rp
    }


def analyze_customer_performance(data: pd.DataFrame) -> pd.DataFrame:
    perf_report = data.copy().to_frame().reset_index()
    perf_report['diff'] = perf_report['TotalAssets'].diff()
    perf_report['pct_change'] = perf_report['TotalAssets'].pct_change()
    return perf_report.fillna(0)


def export_summary_report(data: dict) -> pd.DataFrame:
    summary_file = os.path.join(os.environ['AICV_DATABASE_LOCAL_REPORT'], 'SummaryReport.xlsx')
    summary_df = None
    for cust_name, report_type_dict in data.items():
        perf_report = analyze_customer_performance(report_type_dict['date'])
        # flatten perf_report
        perf_report['customer_name'] = cust_name
        perf_report = perf_report.rename(columns={'TotalAssets': 'total_assets'})
        perf_report = perf_report[['customer_name', 'date', 'total_assets', 'diff', 'pct_change']]
        # Export customer's performance report
        perf_report_fp = os.path.join(os.environ['AICV_DATABASE_LOCAL_REPORT'], 'PerformanceReport_' + cust_name + '.xlsx')
        utils.convert_strformat_to_save(perf_report).to_excel(perf_report_fp)
        logger.debug(f'Exported Performance Report file of {cust_name} at {perf_report_fp}')
        if summary_df is None:
            summary_df = perf_report.copy()
        else:
            summary_df = pd.concat([summary_df, perf_report])
    # summary_df = summary_df.fillna(0)
    if summary_df is not None:
        # summary_df = summary_df.pivot(index='date', columns='customer_name', values=['total_assets', 'diff','pct_change'])
        utils.convert_strformat_to_save(summary_df).to_excel(summary_file)
        logger.debug(f'Exported Summary report file at {summary_file}')
    else:
        logger.error('Unable to export Summary Report, please check it')
    return summary_df