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


def check_available_reviewed_data(method):
    def wrapper(self, *args, **kwargs):
        # Check if the data is available.
        if self.data is None:
            self.data = self.downloader.get_latest_reviewed_data()
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


TCBS_OPS = TCBSOperationMangement()
