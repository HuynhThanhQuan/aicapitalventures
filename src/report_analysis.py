import pandas as pd


def export_report(data):
    day_rp = data.copy()
    day_rp = data.groupby('date')['TotalAssets'].last().dropna()
    print(day_rp)
    week_rp = day_rp.copy().reset_index()
    # week_rp['date'] = pd.to_datetime(week_rp['date']) - pd.to_timedelta(7, unit='d')
    # #calculate sum of values, grouped by week
    # week_rp = week_rp.groupby([pd.Grouper(key='date', freq='W')])['TotalAssets'].last()
    week_rp['week'] = week_rp['date'].dt.isocalendar().week
    week_rp = week_rp.groupby('week')['TotalAssets'].last()
    print(week_rp)
    month_rp = day_rp.copy().reset_index()
    month_rp['month'] = month_rp['date'].dt.month
    month_rp = month_rp.groupby('month')['TotalAssets'].last()
    print(month_rp)