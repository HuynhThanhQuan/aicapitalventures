import pandas as pd
import os
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


LOCAL_REPORT_STORAGE = os.environ['AICV_REPORT']


def export_total_asset_value_report(data: pd.DataFrame) -> dict:
    date_rp = data.copy()
    date_rp = data.groupby('date')['TotalAssets'].last().dropna()
    week_rp = date_rp.copy().reset_index()
    # week_rp['date'] = pd.to_datetime(week_rp['date']) - pd.to_timedelta(7, unit='d')
    # #calculate sum of values, grouped by week
    # week_rp = week_rp.groupby([pd.Grouper(key='date', freq='W')])['TotalAssets'].last()
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
    summary_df = None
    for cust_name, report_type_dict in data.items():
        perf_report = analyze_customer_performance(report_type_dict['date'])
        # flatten perf_report
        perf_report['customer_name'] = cust_name
        perf_report = perf_report.rename(columns={'TotalAssets': 'total_assets'})
        perf_report = perf_report[['customer_name', 'date', 'total_assets', 'diff', 'pct_change']]

        if summary_df is None:
            summary_df = perf_report.copy()
        else:
            summary_df = pd.concat([summary_df, perf_report])
    # summary_df = summary_df.fillna(0)
    if summary_df is not None:
        summary_df = summary_df.pivot(index='date', columns='customer_name', values=['total_assets', 'diff','pct_change'])
    logger.debug(f'Summary report\n{summary_df}')
    return summary_df