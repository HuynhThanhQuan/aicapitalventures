import os
import numpy as np 
import pandas as pd
from pathlib import Path
import logging
import re
from datetime import datetime

from .tcbs_exception import *
from . import capital
from . import customer as cust
from . import transaction


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# LOCAL_DRIVE_STORE = os.environ['AICV_DATABASE_DRIVE']
# VERIFIED_RECORDS = os.path.join(LOCAL_DRIVE_STORE, 'Verified_records.xlsx')
# DRIVE_VERIFIED_RECORDS = os.path.join(LOCAL_DRIVE_STORE, 'Drive_Verified_records.xlsx')
# REVIEWED_VERIFIED_RECORDS = os.path.join(LOCAL_DRIVE_STORE, 'Review_Verified_records.xlsx')


class TCBSOperationMangement:
    def __init__(self):
        self.data = None
        self.tcb_txn_management = transaction.TCBSTransactionHistoryManagement()
        self.customer_capital = capital.CustomerCapital()

    def __check_data(self):
        if self.data is None:
            drive.download_TCBS_transaction_history()

    def get_all_customer_info(self):
        self.__check_data()
        filepath = self.upload_reviewed_verified_records()
        self.data = pd.read_excel(filepath, index_col=0)
        self.data['Ngày GD'] = pd.to_datetime(self.data['Ngày GD'], format='%Y-%m-%d')
        self.data['Số hiệu lệnh'] = self.data['Số hiệu lệnh'].astype(str)
        self.tcb_txn_management.write_from_drive(self.data)
        return self.data

    def get_customer_transaction_history_data(self, customer_name):
        return self.tcb_txn_management.get(customer_name).get_transaction_data()

    def get_customer_info(self, customer_name):
        customer_capital = self.customer_capital.get_deposit_data(customer_name)
        customer_txn_data = self.get_customer_transaction_history_data(customer_name)
        customer_info = cust.CustomerLifetime(customer_name, capital_history=customer_capital, transaction_history=customer_txn_data)
        return customer_info

    def upload_reviewed_verified_records(self) -> str:
        """From latest corrected transaction table, upload it into drive for manual verification
        TCBS transaction history -> Verified_records.xlsx
        Drive: Verified_records.xlsx -> Drive_Verified_records.xlsx
        Verified_records.xlsx compare with Drive_Verified_records.xlsx -> Review_Verified_records.xlsx
        """
        logger.info('Get latest transaction table data')
        df = get_latest_transaction_table()
        if df is None:
            raise TCBSTransactionHistoryNotFound('Unable to find TCB transaction history')
        
        # Search verified records in drive
        logger.info('Get Verified_records in Drive')
        record_files = drive.search_verified_records()
        reviewed_verfied_records_fp = None
        if len(record_files) == 0:
            # New verified records
            __generate_verified_records_from_TCBS_history_transaction(df)
            reviewed_verfied_records_fp = VERIFIED_RECORDS
        else:
            if len(record_files) > 1:
                raise TCBSTransactionHistoryDuplicated
            
            # Download & read this record
            record = record_files[0]
            f_info = drive.download_verified_record(record['id'], DRIVE_VERIFIED_RECORDS)
            drive_vrecords = pd.read_excel(f_info.name, index_col=0)
            logger.debug(f'Verified_record (drive) has {len(drive_vrecords)} records')

            logger.info('Compare TCB txn data (latest) with Verified_records (drive) to get different of "Số hiệu lệnh & KL khớp"')
            # Merge(compare) with current df on Số hiệu lệnh and KL khớp, merge outer 
            df['Số hiệu lệnh'] = df['Số hiệu lệnh'].astype(str).str.strip()
            drive_vrecords['Số hiệu lệnh'] = drive_vrecords['Số hiệu lệnh'].astype(str).str.strip()
            merged_df = drive_vrecords[['Khách hàng', 'Số hiệu lệnh', 'KL khớp']].merge(df, how='outer', left_on=['Số hiệu lệnh','KL khớp'], right_on=['Số hiệu lệnh','KL khớp'])
            merged_df = merged_df.sort_values(by='Ngày GD')
            merged_df = merged_df.reset_index(drop=True)
            merged_df = merged_df[drive_vrecords.columns]
            # Format to upload drive
            for c in merged_df.columns:
                merged_df[c] = merged_df[c].astype(str)
            merged_df.to_excel(REVIEWED_VERIFIED_RECORDS)
            reviewed_verfied_records_fp = REVIEWED_VERIFIED_RECORDS
            logger.debug(f'Reviewing verified records is saved locally at {reviewed_verfied_records_fp}')
            
            # Replace the old one
            logger.info('Replace the Verified_records (drive) to the updated one')
            drive.delete_drive_file(record['id'])

        if reviewed_verfied_records_fp is None or not os.path.exists(reviewed_verfied_records_fp):
            raise ReviewedVerifiedRecordsNotFound
        drive.upload_verified_records_drive(reviewed_verfied_records_fp)
        logger.info('Reviewing verified records is opened for manual assessment')
        return reviewed_verfied_records_fp


TCBS_OPS = TCBSOperationMangement()


def __list_TCBS_transaction_history() -> list[str]:
    """Return list TCBS transaction history files in local Drive storage"""
    tcb_files = [os.path.join(LOCAL_DRIVE_STORE,i) for i in os.listdir(LOCAL_DRIVE_STORE) if 'TCBS_transaction_history' in i]
    logger.debug(f'Found {len(tcb_files)} TCB transaction files in local storage')
    return tcb_files


def __read_TCBS_transaction_file(filepath: str) -> pd.DataFrame:
    """Return pd.DataFrame content of transaction file"""
    filepath = Path(filepath)
    ext = filepath.suffix
    if (ext == '.xlsx') or (ext == '.xls'):
        f_content = pd.read_excel(filepath)
        return f_content
    raise UnsupportedFileFormat('Inapproriate or Unsupported file format')


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
    raise TCBTransactionHistoryNotFound('No transaction file found')


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
            logger.debug(f'Latest TCB transaction table has {len(table)} records')
            return table
    return None


def __correct_data_format(df:pd.DataFrame) -> pd.DataFrame:
    if 'Ngày GD' in df.columns:
        df['Ngày GD'] = pd.to_datetime(df['Ngày GD'].str.strip(), format='%d/%m/%Y')
    return df


def __generate_verified_records_from_TCBS_history_transaction(df:pd.DataFrame) -> pd.DataFrame:
    logger.info('Generate Verified_records from latest TCB txn data')
    verified_record_df = df.copy()
    for i in verified_record_df.columns:
        verified_record_df[i] = verified_record_df[i].astype(str)
    verified_record_df.insert(0, 'Khách hàng', [None] * len(df))
    verified_record_df.to_excel(VERIFIED_RECORDS)
    return verified_record_df

    
def get_all_customer_info():
    return TCBS_OPS.get_all_customer_info()

def get_customer_info(customer_name):
    return TCBS_OPS.get_customer_info(customer_name)