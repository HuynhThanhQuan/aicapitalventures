import pandas as pd
from datetime import datetime, timedelta


class CustomerCapitalInvalidError(Exception):
    pass


class CustomerTransactionHistoryInvalidError(Exception):
    pass


class CustomerLifetime:
    def __init__(self, full_name, capital_history, transaction_history):
        self.full_name = full_name
        self.capital_history=capital_history
        self.transaction_history=transaction_history
        self.analyze()

    def analyze(self):
        if self.capital_history is None or len(self.capital_history) == 0:
            raise CustomerCapitalInvalidError
        if self.transaction_history is None or len(self.transaction_history) == 0:
            raise CustomerTransactionHistoryInvalidError
        
        # Get first deposit time
        col = 'Order Time'
        self.first_deposit_date = self.capital_history[self.capital_history[col]==self.capital_history[col].min()].iloc[0][col]
        # Get first transaction time
        col = 'Ngày GD'
        self.first_txn_date = self.transaction_history[self.transaction_history[col]==self.transaction_history[col].min()].iloc[0][col]
        self.last_txn_date = self.transaction_history[self.transaction_history[col]==self.transaction_history[col].max()].iloc[0][col]
        # Get curr date
        self.current_system_date = datetime.now()

        """
        There are important milestones of each customer is illustated below
        Total assets is depended on each duration

        1. first_deposit_date 
        |       total-asset = cash (100%)
        2. first_txn_date
        |       total-asset = cash + stock-assets
        3. last_txn_date
        |       total-asset = cash + stock-assets
        4. current_system_date
        """
        self.lifetime = pd.DataFrame()
        self.lifetime['date'] = pd.date_range(start=self.first_deposit_date, end=self.current_system_date, freq='D')
        self.lifetime['year'] = self.lifetime['date'].dt.year
        self.lifetime['month'] = self.lifetime['date'].dt.month
        self.lifetime['day'] = self.lifetime['date'].dt.day
        self.lifetime['weekday'] = self.lifetime['date'].dt.weekday
        self.lifetime['quarter'] = self.lifetime['date'].dt.quarter
        
        # Spread capital data in long format 
        self.capital_detail = self.lifetime.copy()
        self.capital_detail = self.capital_detail.merge(self.capital_history[['Order Time', 'Type', 'Amount']], how='left', left_on='date', right_on='Order Time')
        self.capital_detail = self.capital_detail.drop(columns=['Order Time'])
        # print(self.capital_detail)

        # Spread transaction data in long format 
        self.transaction_detail = self.lifetime.copy()
        self.transaction_detail = self.transaction_detail.merge(self.transaction_history, how='left', left_on='date', right_on='Ngày GD')
        self.transaction_detail = self.transaction_detail.drop(columns=['Khách hàng'])
        print(self.transaction_detail)