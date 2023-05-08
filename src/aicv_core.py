import pandas as pd
from datetime import datetime
import capital


class SecurityCompanyNotImplementedError(Exception):
    pass


class BaseAnalyzer:
    def __init__(self):
        pass

    def analyze(self, table:pd.DataFrame):
        pass

class TCBSAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.capital = capital.CustomerCapital()

    def analyze(self, table):
        if table is None:
            return None
        # correct table formats
        table['Ngày GD'] = pd.to_datetime(table['Ngày GD'], format='%Y-%m-%d')
        table['Số hiệu lệnh'] = table['Số hiệu lệnh'].astype(str)
        # Group customers
        customers_data = table.groupby('Khách hàng')
        return table


def get_analyzer(security:str) -> BaseAnalyzer:
    if security == 'TCBS':
        return TCBSAnalyzer()
    else:
        raise SecurityCompanyNotImplementedError