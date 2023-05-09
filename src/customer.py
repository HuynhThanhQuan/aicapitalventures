import pandas as pd
from datetime import datetime, timedelta


class CustomerCapitalInvalidError(Exception):
    pass


class CustomerCapitalHistoryInvalidError(CustomerCapitalInvalidError):
    pass


class CustomerTransactionHistoryInvalidError(Exception):
    pass


""" 
Classes to manage all data of per customer

Customer                    : init and manage customer objects (CustomerTotalAsset, CustomerLifetime, Customer360 (to-be-dev)...)
CustomerLifeTime            : init the lifetime of customer in AICV
CustomerTotalAsset          : total assets including (CustomerCapital, CustomerStockAsset, CustomerCashAsset)
CustomerCapital             : contain capital_history,
CustomerCashAsset           : track and calculate cash remaining
CustomerStockAsset          : contain transaction_history, stock-investments, 
"""

class Customer:
    def __init__(self, full_name, capital_history, transaction_history):
        print(full_name)
        self.full_name=full_name
        self.lifetime = CustomerLifetime(full_name, capital_history, transaction_history)
        self.total_asset = self.lifetime.infer_total_asset()
        

class CustomerTotalAsset:
    def __init__(self, full_name):
        pass


class CustomerCapital:
    def __init__(self, full_name, capital_detail):
        self.full_name = full_name
        self.capital_detail = capital_detail
        self.analyze()

    def verify_data(self):
        if self.capital_detail is None:
            CustomerCapitalInvalidError
        self.capital_detail = self.capital_detail.copy()

    def calculate_accumulative_capital(self):
        # Fill 0 amount for other dates
        self.capital_detail['Amount'] = self.capital_detail['Amount'].fillna(0)

        # Calculate accumulative capital, return a dataframe 
        # NOTE: this dataframe can have different length to capital_detail
        lifetime = self.capital_detail['date'].unique()
        acc_capital_series = []
        for date in lifetime:
            data_df = self.capital_detail[self.capital_detail['date']==date]
            type_order_total_amount = data_df.groupby('Type')['Amount'].sum()
            type_order_total_amount.to_dict()
            curr_net_capital = type_order_total_amount.get('DEPOSIT', 0) - type_order_total_amount.get('WITHDRAWAL', 0)
            if date == self.first_deposit_date:
                # Initial capital
                acc_capital_series.append(curr_net_capital)
            else:
                # Accumulate everyday
                prev_acc_capital = acc_capital_series[-1]
                curr_acc_capital = prev_acc_capital + curr_net_capital
                acc_capital_series.append(curr_acc_capital)
        self.capital_accumulative = pd.DataFrame({'date': lifetime, 'AccCapital': acc_capital_series})

    def analyze(self):
        self.verify_data()
        self.first_deposit_date = self.capital_detail[self.capital_detail['Type'] == 'DEPOSIT']['date'].min()

        # Calculate accumulate capital
        self.calculate_accumulative_capital()


class CustomerStockAsset:
    def __init__(self, full_name, transaction_detail):
        self.full_name = full_name
        self.transaction_detail = transaction_detail
        self.analyze()

    def verify_data(self):
        if self.transaction_detail is None:
            CustomerTransactionHistoryInvalidError
        self.stock_asset = self.transaction_detail.copy()

    def shorten_transactions_intraday(self, txns_intraday):
        trade_intraday = {}
        trade_groups = txns_intraday.groupby('Giao dịch')
        for trade, txns in trade_groups:
            txn_dict = txns.groupby('Mã CP')['KL khớp'].sum().to_dict()
            trade_intraday[trade] = txn_dict
        return trade_intraday

    def convert_transaction2assets_intraday(self, transactions):
        net_stock_assets = {}
        for trade, txns in transactions.items():
            if trade == 'Mua':
                for sticker, vol in txns.items():
                    net_stock_assets[sticker] = net_stock_assets.get(sticker, 0) + vol
            elif trade == 'Bán':
                for sticker, vol in txns.items():
                    net_stock_assets[sticker] = net_stock_assets.get(sticker, 0) - vol
        return net_stock_assets

    def calculate_stock_assets_intraday(self, curr_net_txn, prev_asset):
        net_stock_assets = prev_asset.copy()
        for trade, txns in curr_net_txn.items():
            if trade == 'Mua':
                for sticker, vol in txns.items():
                    net_stock_assets[sticker] = net_stock_assets.get(sticker, 0) + vol
            elif trade == 'Bán':
                for sticker, vol in txns.items():
                    net_stock_assets[sticker] = net_stock_assets.get(sticker, 0) - vol
        
        # Removed sticker with zero asset
        removed_stickers = [k for k, v in net_stock_assets.items() if v == 0]
        for sticker in removed_stickers:
            del net_stock_assets[sticker]

        # Change format to int
        for k in net_stock_assets.keys():
            net_stock_assets[k] = int(net_stock_assets[k])
        return net_stock_assets

    def calculate_accumulative_stock_assets(self):
        # Calculate accumulative stock assets, return a dataframe 
        # NOTE: this dataframe can have different length to stock_assets
        lifetime = self.stock_asset['date'].unique()
        first_date = self.stock_asset['date'].min()
        first_txn_date = self.stock_asset['Ngày GD'].min()
        acc_stock_assets = []
        for date in lifetime:
            curr_data_df = self.stock_asset[self.stock_asset['date']==date]
            curr_net_stock_txn = self.shorten_transactions_intraday(curr_data_df)
            if date < first_txn_date:
                acc_stock_assets.append(None)
            elif date == first_txn_date:
                acc_stock_assets.append(self.convert_transaction2assets_intraday(curr_net_stock_txn))
            else:
                prev_acc_stock_assets = acc_stock_assets[-1]
                curr_acc_stock_assets = self.calculate_stock_assets_intraday(curr_net_stock_txn, prev_acc_stock_assets)
                acc_stock_assets.append(curr_acc_stock_assets)
        self.stock_assets_accumulative = pd.DataFrame({'date': lifetime, 'AccStockAssets': acc_stock_assets})

    def analyze(self):
        self.verify_data()
        self.calculate_accumulative_stock_assets()
        

class CustomerCashAsset:
    def __init__(self, full_name):
        pass


class CustomerLifetime:
    def __init__(self, full_name, capital_history, transaction_history):
        self.full_name = full_name
        self.capital_history=capital_history
        self.transaction_history=transaction_history
        self.analyze()

    def verify_data(self):
        if self.capital_history is None or len(self.capital_history) == 0:
            raise CustomerCapitalHistoryInvalidError
        if self.transaction_history is None or len(self.transaction_history) == 0:
            raise CustomerTransactionHistoryInvalidError

    def analyze(self):
        self.verify_data()

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

        # Customer date lifetime
        self.lifetime_table = pd.DataFrame()
        self.lifetime_table['date'] = pd.date_range(start=self.first_deposit_date, end=self.current_system_date, freq='D')
        self.lifetime_table['year'] = self.lifetime_table['date'].dt.year
        self.lifetime_table['month'] = self.lifetime_table['date'].dt.month
        self.lifetime_table['day'] = self.lifetime_table['date'].dt.day
        self.lifetime_table['weekday'] = self.lifetime_table['date'].dt.weekday
        self.lifetime_table['quarter'] = self.lifetime_table['date'].dt.quarter

    def infer_total_asset(self) -> CustomerTotalAsset:
        # Spread capital data in long format 
        capital_detail = self.lifetime_table.copy()
        capital_detail = capital_detail.merge(self.capital_history[['Order Time', 'Type', 'Amount']], how='left', left_on='date', right_on='Order Time')
        capital_detail = capital_detail.drop(columns=['Order Time'])
        # Init obj capital
        cust_capital = CustomerCapital(self.full_name, capital_detail)

        # Spread transaction data in long format 
        transaction_detail = self.lifetime_table.copy()
        transaction_detail = transaction_detail.merge(self.transaction_history, how='left', left_on='date', right_on='Ngày GD')
        transaction_detail = transaction_detail.drop(columns=['Khách hàng'])
        # Init stock capital
        cust_stock = CustomerStockAsset(self.full_name, transaction_detail)
        return CustomerTotalAsset(self.full_name)
