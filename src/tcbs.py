import os
import numpy as np 
import pandas as pd
from pathlib import Path
import re
from datetime import datetime


DRIVE_STORE = os.environ['AICV_DRIVE']


def list_TCBS_transaction_history() -> list[str]:
    """Return list TCBS transaction history files in default Drive location"""
    return [os.path.join(DRIVE_STORE,i) for i in os.listdir(DRIVE_STORE)]


def read_TCBS_transaction_file(filepath: str) -> pd.DataFrame:
    """Return pd.DataFrame content of transaction file"""
    filepath = Path(filepath)
    ext = filepath.suffix
    if (ext == '.xlsx') or (ext == '.xls'):
        f_content = pd.read_excel(filepath)
        return f_content
    print('Inapproriate or Unsupported file format')
    return None


def extract_export_date(df: pd.DataFrame) -> datetime:
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


def sort_transaction_files() -> dict:
    files = list_TCBS_transaction_history()
    export_map = {}
    for f in files:
        ct = read_TCBS_transaction_file(f)
        export_datetime = None
        if ct is not None:
            export_datetime = extract_export_date(ct)
        export_map[f] = export_datetime
    sort_map = {k: v for k, v in sorted(export_map.items(), key=lambda item: item[1])}
    return sort_map


def get_latest_transaction_file() -> str:
    sort_files = sort_transaction_files()
    if len(sort_files) > 0:
        return list(sort_files.keys())[0]
    print('No transaction file found')
    return None

def export_transaction_table(filepath:str) -> pd.DataFrame:
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
    print(reread_df.info())
    return reread_df


def get_latest_transaction_table():
    latest_file = get_latest_transaction_file()
    if latest_file is not None:
        
        table = export_transaction_table(latest_file)