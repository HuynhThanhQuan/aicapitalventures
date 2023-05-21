import os
import numpy as np 
import pandas as pd
from pathlib import Path
import logging
import re
from datetime import datetime
import yaml

from .tcbs_exception import *
from . import capital
from . import customer as cust
from . import transaction as txn
from .download import Downloader

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# LOCAL_DRIVE_STORE = os.environ['AICV_DATABASE_DRIVE']
# VERIFIED_RECORDS = os.path.join(LOCAL_DRIVE_STORE, 'Verified_records.xlsx')
# DRIVE_VERIFIED_RECORDS = os.path.join(LOCAL_DRIVE_STORE, 'Drive_Verified_records.xlsx')
# REVIEWED_VERIFIED_RECORDS = os.path.join(LOCAL_DRIVE_STORE, 'Review_Verified_records.xlsx')

def check_available_reviewed_data(method):
    def wrapper(self, *args, **kwargs):
        # Check if the data is available.
        if self.data is None:
            filepath = self.downloader.get_latest_reviewed_data()
            self.data = pd.read_excel(filepath)
        # Get the data.
        result = method(self, *args, **kwargs)
        return result
    return wrapper


class TCBSOperationMangement:
    def __init__(self):
        self.data = None  # ReviewedData
        self.downloader = Downloader()  # This should be name DataTransfer include (Downloader & Uploader)
        self.tcb_txn_management = txn.TCBSTransactionHistoryManagement()
        self.customer_capital = capital.CustomerCapital()

    @check_available_reviewed_data
    def get_all_customer_info(self) -> pd.DataFrame:
        if self.data is not None:
            self.data['Ngày GD'] = pd.to_datetime(self.data['Ngày GD'], format='%Y-%m-%d')
            self.data['Số hiệu lệnh'] = self.data['Số hiệu lệnh'].astype(str)
            self.tcb_txn_management.write_from_drive(self.data)
        return self.data

    @check_available_reviewed_data
    def get_customer_info(self, customer_name) -> pd.DataFrame:
        customer_capital = self.customer_capital.get_deposit_data(customer_name)
        customer_txn_data = self.__get_customer_transaction_history_data(customer_name)
        customer_info = cust.CustomerLifetime(customer_name, capital_history=customer_capital, transaction_history=customer_txn_data)
        return customer_info

    def upload_reviewed_data(self):
        return self.downloader.upload_reviewed_data()

    def __get_customer_transaction_history_data(self, customer_name):
        return self.tcb_txn_management.get(customer_name).get_transaction_data()

    # def merge_conflict_reviewed_data_between_local_and_drive(self):
    #     logger.info('Get latest transaction table data')
    #     df = get_latest_transaction_table()
    #     if df is None:
    #         raise TCBSTransactionHistoryNotFound('Unable to find TCB transaction history')
        
    #     # Search verified records in drive
    #     logger.info('Get Verified_records in Drive')
    #     record_files = drive.search_verified_records()
    #     reviewed_verfied_records_fp = None
    #     if len(record_files) == 0:
    #         # New verified records
    #         __generate_verified_records_from_TCBS_history_transaction(df)
    #         reviewed_verfied_records_fp = VERIFIED_RECORDS
    #     else:
    #         if len(record_files) > 1:
    #             raise TCBSTransactionHistoryDuplicated
            
    #         # Download & read this record
    #         record = record_files[0]
    #         f_info = drive.download_verified_record(record['id'], DRIVE_VERIFIED_RECORDS)
    #         drive_vrecords = pd.read_excel(f_info.name, index_col=0)
    #         logger.debug(f'Verified_record (drive) has {len(drive_vrecords)} records')

    #         logger.info('Compare TCB txn data (latest) with Verified_records (drive) to get different of "Số hiệu lệnh & KL khớp"')
    #         # Merge(compare) with current df on Số hiệu lệnh and KL khớp, merge outer 
    #         df['Số hiệu lệnh'] = df['Số hiệu lệnh'].astype(str).str.strip()
    #         drive_vrecords['Số hiệu lệnh'] = drive_vrecords['Số hiệu lệnh'].astype(str).str.strip()
    #         merged_df = drive_vrecords[['Khách hàng', 'Số hiệu lệnh', 'KL khớp']].merge(df, how='outer', left_on=['Số hiệu lệnh','KL khớp'], right_on=['Số hiệu lệnh','KL khớp'])
    #         merged_df = merged_df.sort_values(by='Ngày GD')
    #         merged_df = merged_df.reset_index(drop=True)
    #         merged_df = merged_df[drive_vrecords.columns]
    #         # Format to upload drive
    #         for c in merged_df.columns:
    #             merged_df[c] = merged_df[c].astype(str)
    #         merged_df.to_excel(REVIEWED_VERIFIED_RECORDS)
    #         reviewed_verfied_records_fp = REVIEWED_VERIFIED_RECORDS
    #         logger.debug(f'Reviewing verified records is saved locally at {reviewed_verfied_records_fp}')
            
    #         # Replace the old one
    #         logger.info('Replace the Verified_records (drive) to the updated one')
    #         drive.delete_drive_file(record['id'])

    #     if reviewed_verfied_records_fp is None or not os.path.exists(reviewed_verfied_records_fp):
    #         raise ReviewedVerifiedRecordsNotFound
    #     drive.upload_verified_records_drive(reviewed_verfied_records_fp)
    #     logger.info('Reviewing verified records is opened for manual assessment')
    #     return reviewed_verfied_records_fp


TCBS_OPS = TCBSOperationMangement()
