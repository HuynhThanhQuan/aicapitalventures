import pandas as pd
from datetime import datetime
import capital
import customer as cust
import report_analysis as rpa


class SecurityCompanyNotImplementedError(Exception):
    pass

class BaseAnalyzer:
    def __init__(self):
        pass

    def analyze(self, table:pd.DataFrame):
        pass

class TCBSAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.capital_extractor = capital.CapitalExtractor()

    def analyze(self, table):
        if table is None:
            return None
        # correct table formats
        table['Ngày GD'] = pd.to_datetime(table['Ngày GD'], format='%Y-%m-%d')
        table['Số hiệu lệnh'] = table['Số hiệu lệnh'].astype(str)
        # Group customers
        customer_data_groups = table.groupby('Khách hàng')
        return self.analyze_per_customer(customer_data_groups)

    def analyze_per_customer(self, customer_data_groups):
        for customer_name, customer_txn_data in customer_data_groups:
            customer_capital = self.capital_extractor.get_deposit_data(customer_name)
            # Analyze and get full data info of Customer
            customer_info = cust.CustomerLifetime(customer_name, capital_history=customer_capital, transaction_history=customer_txn_data)
            rpa.export_report(customer_info.total_assets_value)

def get_analyzer(security:str) -> BaseAnalyzer:
    if security == 'TCBS':
        return TCBSAnalyzer()
    else:
        raise SecurityCompanyNotImplementedError