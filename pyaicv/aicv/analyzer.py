"""
Comments
"""

# Standard
import logging

# Third party
import pandas as pd

# Local app
import capital
import customer as cust
import report_analysis as rpa
import gdrive
from aicv_exception import *


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


DEFAULT_ANALYZER = None



class BaseAnalyzer:
    def __init__(self):
        pass

    def analyze(self, table:pd.DataFrame):
        pass

class TCBSAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.capital_extractor = capital.CapitalExtractor()
        self.customer_reports = {}

    def analyze(self, table):
        if table is None:
            return None
        # correct table formats
        table['Ngày GD'] = pd.to_datetime(table['Ngày GD'], format='%Y-%m-%d')
        table['Số hiệu lệnh'] = table['Số hiệu lệnh'].astype(str)
        # Group customers
        customer_data_groups = table.groupby('Khách hàng')
        self.analyze_per_customer(customer_data_groups)

    def analyze_per_customer(self, customer_data_groups):
        for customer_name, customer_txn_data in customer_data_groups:
            logger.debug(f'Analyze {customer_name} assets')
            customer_capital = self.capital_extractor.get_deposit_data(customer_name)
            # Analyze and get full data info of Customer
            customer_info = cust.CustomerLifetime(customer_name, capital_history=customer_capital, transaction_history=customer_txn_data)
            cust_report = rpa.export_total_asset_value_report(customer_info.total_assets_value)
            self.customer_reports[customer_name] = cust_report

    def export_summary_report(self):
        # Store local summary report
        rpa.export_summary_report(self.customer_reports)
        gdrive.update_summary_report()


def get_analyzer(security:str) -> BaseAnalyzer:
    global DEFAULT_ANALYZER
    logger.info(f'Set {security} Analyzer as default')
    if security == 'TCBS':
        DEFAULT_ANALYZER = TCBSAnalyzer()
        return DEFAULT_ANALYZER
    else:
        raise SecurityCompanyNotImplementedError(f"Security {security} is not inplemented, please choose other security firm")


def get_default_analyzer() -> BaseAnalyzer:
    global DEFAULT_ANALYZER
    return DEFAULT_ANALYZER