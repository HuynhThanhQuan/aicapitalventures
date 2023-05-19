"""
Comments
"""

# Standard
import logging

# Third party
import pandas as pd

# Local app
from pyaicv.security import factory
from .exception import *
from . import report_analysis as rpa
from . import drive


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


DEFAULT_ANALYSER = None


class BaseAnalyser:
    def __init__(self):
        pass

    def analyse(self):
        pass

    def check_data(self):
        pass


class TCBSAnalyser(BaseAnalyser):
    def __init__(self):
        self.customer_reports = {}

    def run_analysis_full_database(self):
        # Request all customer data table of Security
        all_cust_info = factory.get_active_security().get_all_customer_info()
        if all_cust_info is None:
            return None
        table = all_cust_info.copy()
        for customer_name in table['Khách hàng'].unique():
            logger.debug(f'Analyze {customer_name} assets')
            customer_info = self.get_customer_info(customer_name)
            cust_report = rpa.export_total_asset_value_report(customer_info.total_assets_value)
            self.customer_reports[customer_name] = cust_report
        logger.debug(f'Completed full Analysis with {len(self.customer_reports)} customers')

    def get_customer_info(self, customer_name):
        return factory.get_active_security().get_customer_info(customer_name)

    def export_summary_report(self):
        # Store local summary report
        summary_df = rpa.export_summary_report(self.customer_reports)
        if summary_df is not None:
            drive.update_values()


def get_default_analyser() -> BaseAnalyser:
    global DEFAULT_ANALYSER
    return DEFAULT_ANALYSER


def set_security_analyser(security_module:str) -> BaseAnalyser:
    global DEFAULT_ANALYSER
    if security_module.NAME == 'TCBS':
        DEFAULT_ANALYSER = TCBSAnalyser()
        logger.info(f'Set {security_module.NAME}_Analyser as default')
        return DEFAULT_ANALYSER
    else:
        raise SecurityCompanyNotImplementedError(f"Security {security_module.name} is not inplemented, please select other security firm")


def run_full_analysis():
    DEFAULT_ANALYSER.run_analysis_full_database()


def export_summary_report():
    DEFAULT_ANALYSER.export_summary_report()