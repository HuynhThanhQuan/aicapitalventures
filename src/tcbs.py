import os
import numpy as np 
import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import gdrive
from tcbs_exception import *

DRIVE_STORE = os.environ['AICV_DRIVE']
VERIFIED_RECORD = os.path.join(DRIVE_STORE, 'Verified_records.xlsx')


def __list_TCBS_transaction_history() -> list[str]:
    """Return list TCBS transaction history files in default Drive location"""
    return [os.path.join(DRIVE_STORE,i) for i in os.listdir(DRIVE_STORE) if 'TCBS_transaction_history' in i]


def __read_TCBS_transaction_file(filepath: str) -> pd.DataFrame:
    """Return pd.DataFrame content of transaction file"""
    filepath = Path(filepath)
    ext = filepath.suffix
    if (ext == '.xlsx') or (ext == '.xls'):
        f_content = pd.read_excel(filepath)
        return f_content
    print('Inapproriate or Unsupported file format')
    return None


def __extract_export_date(df: pd.DataFrame) -> datetime:
    first_col = df.iloc[:,0]
    cond_values = first_col.str.contains('Ngày xuất báo cáo').fillna(False)
    row_index = cond_values[cond_values==True].index
    statement = df.iloc[row_index,0].values[0]
    time_p = r'(\d+)h(\d+)'
    date_p = r'(\d+)/(\d+)/(\d+)'
    time_export = re.findall(time_p, statement)[0]
    date_export = re.findall(date_p, statement)[0]
    correct_form = f'{date_export[2]}-{date_export[1]}-{date_export[0]} {time_export[0]}:{time_export[1]}'
    export_datetime = datetime.strptime(f'{correct_form}', "%Y-%m-%d %H:%M")
    return export_datetime


def __sort_transaction_files() -> dict:
    files = __list_TCBS_transaction_history()
    export_map = {}
    for f in files:
        ct = __read_TCBS_transaction_file(f)
        export_datetime = None
        if ct is not None:
            export_datetime = __extract_export_date(ct)
        export_map[f] = export_datetime
    sort_map = {k: v for k, v in sorted(export_map.items(), key=lambda item: item[1])}
    return sort_map


def __get_latest_transaction_file() -> str:
    sort_files = __sort_transaction_files()
    if len(sort_files) > 0:
        return list(sort_files.keys())[0]
    print('No transaction file found')
    return None


def __export_corrected_transaction_table(filepath:str) -> pd.DataFrame:
    df = pd.read_excel(filepath)
    # Find Ma CP index
    first_col = df.iloc[:,1]
    cond_values = first_col.str.contains('Ngày GD').fillna(False)
    # row_index = cond_values[cond_values==True].index.values[0]
    row_index = cond_values[cond_values==True].index.values[0]
    df_below = df.iloc[row_index+1:]
    table_cond  = df_below.iloc[:,0].fillna('NoValue').astype(str).apply(lambda x: len(x) <= 3)
    lower_index = table_cond[table_cond==False].index + 1
    skiprows_index = list(range(row_index+1)) + (lower_index.tolist())
    # Reread table with found row_index
    reread_df = pd.read_excel(filepath,skiprows=skiprows_index)
    return reread_df


def get_latest_transaction_table() -> pd.DataFrame:
    latest_file = __get_latest_transaction_file()
    if latest_file is not None:
        table = __export_corrected_transaction_table(latest_file)
        if table is not None:
            table = __correct_data_format(table)
            return table
    return None


def __correct_data_format(df:pd.DataFrame) -> pd.DataFrame:
    if 'Ngày GD' in df.columns:
        df['Ngày GD'] = pd.to_datetime(df['Ngày GD'].str.strip(), format='%d/%m/%Y')
    return df


def __generate_verified_records_from_TCBS_history_transaction(df:pd.DataFrame) -> pd.DataFrame:
    verified_record_df = df.copy()
    for i in verified_record_df.columns:
        verified_record_df[i] = verified_record_df[i].astype(str)
    verified_record_df.insert(0, 'Khách hàng', [None] * len(df))
    verified_record_df.to_excel(VERIFIED_RECORD)
    return verified_record_df


def upload_verified_records():
    """From latest corrected transaction table, upload it into drive for manual verification"""
    df = get_latest_transaction_table()
    if df is None:
        raise TCBSTransactionHistoryNotFound
    
    # Search verified records in drive
    files = gdrive.search_verified_records()
    verified_record_df = None
    if len(files) == 0:
        # New verified records
        verified_record_df = __generate_verified_records_from_TCBS_history_transaction(df)
        gdrive.upload_verified_records_gdrive(VERIFIED_RECORD)
        return verified_record_df
    else:
        # TODO: Download, read, compare with current df 
        # If current df has new transactions then add them into Verified_records and replace it on drive
        pass