import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import vnstock

class CustomerCapitalInvalidError(Exception):
    pass


class CustomerCapitalHistoryInvalidError(CustomerCapitalInvalidError):
    pass


class CustomerTransactionHistoryInvalidError(Exception):
    pass


# """ 
# Classes to manage all data of per customer

# Customer                    : init and manage customer objects (CustomerTotalAsset, CustomerLifetime, Customer360 (to-be-dev)...)
# CustomerLifetime            : init the lifetime of customer in AICV
# CustomerTotalAsset          : total assets including (CustomerCapital, CustomerStockAsset, CustomerCashAsset)
# CustomerCapital             : contain capital_history,
# CustomerCashAsset           : track and calculate cash remaining
# CustomerStockAsset          : contain transaction_history, stock-investments, 
# CustomerStockValueAsset     : stock-value at market
# """

# class Customer:
#     def __init__(self, full_name, capital_history, transaction_history):
#         print(full_name)
#         self.full_name=full_name
#         self.lifetime = CustomerLifetime(full_name, capital_history, transaction_history)
#         self.total_asset = self.lifetime.infer_total_asset()
        

# class CustomerTotalAsset:
#     def __init__(self, full_name):
#         pass


# class CustomerCapital:
#     def __init__(self, full_name, capital_detail):
#         self.full_name = full_name
#         self.capital_detail = capital_detail
#         self.analyze()

#     def verify_data(self):
#         if self.capital_detail is None:
#             CustomerCapitalInvalidError
#         self.capital_detail = self.capital_detail.copy()

#     def calculate_accumulative_capital(self):
#         # Fill 0 amount for other dates
#         self.capital_detail['Amount'] = self.capital_detail['Amount'].fillna(0)

#         # Calculate accumulative capital, return a dataframe 
#         # NOTE: this dataframe can have different length to capital_detail
#         lifetime = self.capital_detail['date'].unique()
#         acc_capital_series = []
#         for date in lifetime:
#             data_df = self.capital_detail[self.capital_detail['date']==date]
#             type_order_total_amount = data_df.groupby('Type')['Amount'].sum()
#             type_order_total_amount.to_dict()
#             curr_net_capital = type_order_total_amount.get('DEPOSIT', 0) - type_order_total_amount.get('WITHDRAWAL', 0)
#             if date == self.first_deposit_date:
#                 # Initial capital
#                 acc_capital_series.append(curr_net_capital)
#             else:
#                 # Accumulate everyday
#                 prev_acc_capital = acc_capital_series[-1]
#                 curr_acc_capital = prev_acc_capital + curr_net_capital
#                 acc_capital_series.append(curr_acc_capital)
#         self.capital_accumulative = pd.DataFrame({'date': lifetime, 'AccCapital': acc_capital_series})

#     def analyze(self):
#         self.verify_data()
#         self.first_deposit_date = self.capital_detail[self.capital_detail['Type'] == 'DEPOSIT']['date'].min()

#         # Calculate accumulate capital
#         self.calculate_accumulative_capital()


# class CustomerStockAsset:
#     def __init__(self, full_name, transaction_detail):
#         self.full_name = full_name
#         self.transaction_detail = transaction_detail
#         self.analyze()

#     def verify_data(self):
#         if self.transaction_detail is None:
#             CustomerTransactionHistoryInvalidError

#     def shorten_transactions_intraday(self, txns_intraday):
#         trade_intraday = {}
#         trade_groups = txns_intraday.groupby('Giao dịch')
#         for trade, txns in trade_groups:
#             txn_dict = txns.groupby('Mã CP')['KL khớp'].sum().to_dict()
#             trade_intraday[trade] = txn_dict
#         return trade_intraday

#     def convert_transaction2assets_intraday(self, transactions):
#         net_stock_assets = {}
#         for trade, txns in transactions.items():
#             if trade == 'Mua':
#                 for sticker, vol in txns.items():
#                     net_stock_assets[sticker] = net_stock_assets.get(sticker, 0) + vol
#             elif trade == 'Bán':
#                 for sticker, vol in txns.items():
#                     net_stock_assets[sticker] = net_stock_assets.get(sticker, 0) - vol
#         return net_stock_assets

#     def calculate_stock_assets_intraday(self, curr_net_txn, prev_asset):
#         net_stock_assets = prev_asset.copy()
#         for trade, txns in curr_net_txn.items():
#             if trade == 'Mua':
#                 for sticker, vol in txns.items():
#                     net_stock_assets[sticker] = net_stock_assets.get(sticker, 0) + vol
#             elif trade == 'Bán':
#                 for sticker, vol in txns.items():
#                     net_stock_assets[sticker] = net_stock_assets.get(sticker, 0) - vol
        
#         # Removed sticker with zero asset
#         removed_stickers = [k for k, v in net_stock_assets.items() if v == 0]
#         for sticker in removed_stickers:
#             del net_stock_assets[sticker]

#         # Change format to int
#         for k in net_stock_assets.keys():
#             net_stock_assets[k] = int(net_stock_assets[k])
#         return net_stock_assets

#     def calculate_accumulative_stock_assets(self):
#         # Calculate accumulative stock assets, return a dataframe 
#         # NOTE: this dataframe can have different length to stock_assets
#         lifetime = self.transaction_detail['date'].unique()
#         first_date = self.transaction_detail['date'].min()
#         first_txn_date = self.transaction_detail['Ngày GD'].min()
#         acc_stock_assets = []
#         for date in lifetime:
#             curr_data_df = self.transaction_detail[self.transaction_detail['date']==date]
#             curr_net_stock_txn = self.shorten_transactions_intraday(curr_data_df)
#             """
#             For days before first transaction, value will be None to indicate no value prior to the first transaction was made
#             For days after first transaction, asset could be zero so value of asset is indicated as empty dictionary
#             """
#             if date < first_txn_date:
#                 acc_stock_assets.append(None)
#             elif date == first_txn_date:
#                 acc_stock_assets.append(self.convert_transaction2assets_intraday(curr_net_stock_txn))
#             else:
#                 prev_acc_stock_assets = acc_stock_assets[-1]
#                 curr_acc_stock_assets = self.calculate_stock_assets_intraday(curr_net_stock_txn, prev_acc_stock_assets)
#                 acc_stock_assets.append(curr_acc_stock_assets)
#         self.stock_assets = pd.DataFrame({'date': lifetime, 'AccStockAssets': acc_stock_assets})

#     def calculate_stock_values(self):
#         self.stock_value_assets = CustomerStockValueAsset(self.full_name, self.transaction_detail, self.stock_assets)

#     def analyze(self):
#         self.verify_data()
#         self.calculate_accumulative_stock_assets()
#         self.calculate_stock_values()


# class CustomerStockValueAsset:
#     def __init__(self,full_name,transaction_detail,stock_assets):
#         self.full_name = full_name
#         self.transaction_detail = transaction_detail
#         self.stock_assets = stock_assets
#         self.analyze()

#     def verify_data(self):
#         if self.transaction_detail is None:
#             CustomerTransactionHistoryInvalidError

#     def analyze(self):
#         self.verify_data()
#         self.calculate_stock_values()

#     def calculate_stock_values_intraday(self, row):
#         stock_assets = row['AccStockAssets']
#         stock_values = np.nan
#         if stock_assets:
#             stock_values = 0
#             for symbol, vol in stock_assets.items():
#                 market_value = row[f'CloseMarket_{symbol}']
#                 stock_values += vol * market_value
#         return stock_values
        
#     def calculate_stock_values(self):
#         self.table = self.stock_assets.copy()
#         start_date = (self.stock_assets['date'].min()-timedelta(days=1)).strftime('%Y-%m-%d')
#         end_date = self.stock_assets['date'].max().strftime('%Y-%m-%d')
#         # get list of investment symbol
#         symbols = []
#         for sa in self.stock_assets['AccStockAssets'].tolist():
#             if sa:
#                 symbols.extend(list(sa.keys()))
#         symbols = set(symbols)
#         # Get market values
#         for s in symbols:
#             symbol_stock_data = stock.vnstock.stock_historical_data(symbol=s, start_date=start_date, end_date=end_date)
#             symbol_stock_data = symbol_stock_data[['TradingDate', 'Close']]
#             symbol_stock_data = symbol_stock_data.rename(columns={'TradingDate': 'date', 'Close': f'CloseMarket_{s}'})
#             self.table = self.table.merge(symbol_stock_data,how='left', left_on='date', right_on='date')

#         # Calculate stock_value_assets
#         self.table['StockValueAssets'] = self.table.apply(lambda row: self.calculate_stock_values_intraday(row), axis=1)

# class CustomerCashAsset:
#     def __init__(self, full_name, capital, stock_assets):
#         self.full_name = full_name
#         self.capital = capital
#         self.stock_assets = stock_assets
#         self.stock_value_assets = stock_assets.stock_value_assets.table
#         self.analyze()

#     def verify_data(self,):
#         if self.capital is None:
#             CustomerCapitalInvalidError

#     def analyze(self):
#         self.verify_data()
#         self.calculate_transaction_net_values()
#         self.calculate_cash()

#     def calculate_transaction_net_value_intraday(self, txn_intraday):
#         """
#         Buy stock is a minus operation to capital
#         Sell stock is a plus operation to capital
#         """
#         net_value_intraday = 0
#         trade_values = txn_intraday.groupby('Giao dịch')['Giá trị khớp (VND)'].sum().to_dict()
#         for trade, total in trade_values.items():
#             if trade == 'Mua':
#                 net_value_intraday -= total
#             elif trade == 'Bán':
#                 net_value_intraday += total
#         return net_value_intraday

#     def calculate_transaction_net_values(self):
#         capital_acc = self.capital.capital_accumulative
#         txn_detail = self.stock_assets.transaction_detail
#         stock_asset_acc = self.stock_assets.stock_assets

#         lifetime = capital_acc['date']
#         first_date = lifetime.min()
#         net_values_intraday = []
#         for date in lifetime:
#             txn_intraday = txn_detail[txn_detail['date']==date]
#             net_value_intraday = self.calculate_transaction_net_value_intraday(txn_intraday)
#             net_values_intraday.append(net_value_intraday)

#         self.cash_assets = pd.DataFrame(
#             {
#                 'date': lifetime, 
#                 'AccCapital': capital_acc['AccCapital'], 
#                 'NetTxnIntraday':  net_values_intraday})
    
#     def calculate_cash(self,):
#         # print(self.cash_assets)
#         # print(self.stock_value_assets)
#         merge_df = self.cash_assets.merge(self.stock_value_assets, how='left', left_on='date', right_on='date')
#         merge_df.insert(1, 'weekday', merge_df['date'].dt.weekday, )
#         print(merge_df)

class CustomerLifetime:
    def __init__(self, full_name, capital_history, transaction_history):
        print(full_name)
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

        self.infer_total_asset()

    def get_activity_time(self, x):
        if not pd.isna(x['TxnDatetime']):
            return pd.to_datetime(x['TxnDatetime'], format='%Y-%m-%d %H:%M:%S.%f')
        if not pd.isna(x['Order Time']):
            return pd.to_datetime(x['Order Time'], format='%Y-%m-%d %H:%M:%S.%f')
        return pd.to_datetime(x['date'], format='%Y-%m-%d %H:%M:%S.%f')

    def infer_total_asset(self):
        # Spread capital data in long format 
        capital_detail = self.lifetime_table.copy()
        capital_detail = capital_detail.merge(self.capital_history[['Order Time', 'Type', 'Amount']], how='left', left_on='date', right_on='Order Time')
        # capital_detail = capital_detail.drop(columns=['Order Time'])

        # Spread transaction data in long format 
        transaction_detail = self.transaction_history.copy()
        transaction_detail = transaction_detail.drop(columns=['Khách hàng', 'KL đặt', 'Giá đặt (VND)', 'Phí (VND)', 'Thuế (VND)', 'Giá vốn', 'Lãi lỗ (VND)', 'Kênh GD', 'Trạng thái', 'Loại lệnh'])
        transaction_detail['TxnTime'] = transaction_detail['Số hiệu lệnh'].astype(str).apply(lambda x:int(x[-6:]))
        transaction_detail['TxnDatetime'] = transaction_detail['Ngày GD'] + transaction_detail['TxnTime'].apply(lambda x: timedelta(milliseconds=x))
        transaction_detail = pd.merge(self.lifetime_table, transaction_detail, how='left', left_on='date', right_on='Ngày GD')

        # Concat together to return all tracking activities data
        cust_tracking_act = pd.concat([capital_detail, transaction_detail])
        # cust_tracking_act['TxnDatetime'] = cust_tracking_act[['date', 'TxnDatetime']]
        
        cust_tracking_act['ActivityTime'] = cust_tracking_act.apply(lambda x: self.get_activity_time(x), axis=1)
        cust_tracking_act['ActivityTime_str'] = cust_tracking_act['ActivityTime'].apply(lambda x: x.strftime(format='%Y-%m-%d %H:%M:%S.%f') if not pd.isna(x) else None)
        # cust_tracking_act = cust_tracking_act.sort_values('ActivityTime').reset_index(drop=True)
        print(cust_tracking_act)
        cust_tracking_act.to_excel(f'{self.full_name}_test.xlsx')



    #     lifetime = cust_tracking_act['date'].unique()
    #     # Calculate stock-assets per day, return acc-stock-assets 
    #     stock_assets_intraday = []
    #     for date in lifetime:
    #         curr_data = cust_tracking_act[cust_tracking_act['date'] == date]
    #         if date == lifetime.min():
    #             prev = self.calculate_stock_assets_intraday(curr_data, None)
    #         else:
    #             prev = self.calculate_stock_assets_intraday(curr_data, prev)
    #         stock_assets_intraday.append(prev)
    #     acc_stock_assets = pd.DataFrame({'date': lifetime, 'AccStockAssets': stock_assets_intraday})

    #     # Get unique stickers
    #     stickers = []
    #     for tmp in stock_assets_intraday:
    #         stickers.extend(list(tmp.keys()))
    #     unique_stickers = set(stickers)
    #     # Create sticker_columns
    #     for s in unique_stickers:
    #         acc_stock_assets[s] = 0
    #     # Get simple version of acc-stock-assets
    #     for idx, d in acc_stock_assets['AccStockAssets'].items():
    #         for s, v in d.items():
    #             acc_stock_assets.at[idx,s]=v

    #     # Get market data
    #     market = pd.DataFrame({'date': lifetime})
    #     start_date, end_date = (lifetime.min() - timedelta(days=1)).strftime('%Y-%m-%d'), lifetime.max().strftime('%Y-%m-%d')
    #     for s in unique_stickers:
    #         symbol_stock_data = vnstock.stock_historical_data(symbol=s, start_date=start_date, end_date=end_date)
    #         symbol_stock_data = symbol_stock_data[['TradingDate', 'Close']]
    #         symbol_stock_data = symbol_stock_data.rename(columns={'TradingDate': 'date', 'Close': f'{s}_MarketUnitValue'})
    #         market = market.merge(symbol_stock_data,how='left', left_on='date', right_on='date')

    #     stock_market_value = cust_tracking_act.merge(acc_stock_assets,how='left', left_on='date', right_on='date')
    #     stock_market_value = stock_market_value.merge(market,how='left', left_on='date', right_on='date')
    #     # Calculate StockAssetMarketValue
    #     for s in unique_stickers:
    #         stock_market_value[f'{s}_TotalMarketValue'] = stock_market_value[s] * stock_market_value[f'{s}_MarketUnitValue']
    #         stock_market_value[f'{s}_TotalMarketValue'] = stock_market_value[f'{s}_TotalMarketValue'].fillna(0)
    #     stock_market_value['StockAssetsMarketValue'] = sum([stock_market_value[f'{s}_TotalMarketValue'] for s in unique_stickers])
    #     print(stock_market_value)
    #     stock_market_value.to_excel(f'{self.full_name}_test.xlsx')

    #     # Calculate stock-assets-value
    #     stock_assets_value_intraday = []
    #     for date in lifetime:
    #         curr_data = stock_market_value[stock_market_value['date'] == date]
    #         stock_asset_value_intraday = self.calculate_stock_assets_value_intraday(curr_data)
    #         stock_assets_value_intraday.append(stock_asset_value_intraday)
    #     stock_assets_value_intraday = pd.DataFrame({'date': lifetime, 'StockAssetValue': stock_assets_value_intraday})
    #     print(stock_assets_value_intraday)
    #     stock_assets_value_intraday.to_excel(f'{self.full_name}_test1.xlsx')

    # def calculate_stock_assets_value_intraday(self, curr_data):
    #     print(curr_data)
    #     curr_stock_assets = curr_data['AccStockAssets'].copy()
    #     stock_assets_value_intraday = 0
    #     for i, txn in curr_data.iterrows():
    #         if txn['Giao dịch'] == 'Mua':
    #             stock_assets_value_intraday += txn['Giá trị khớp (VND)']
    #             # remaining assets
    #             if txn['Mã CP'] in curr_stock_assets.keys():
    #                 curr_stock_assets[txn['Mã CP']] -= txn['KL khớp']

    #     for s, v in txn['AccStockAssets'].items():
    #         stock_assets_value_intraday += v * txn[f'{s}_MarketUnitValue'] if not pd.isna(txn[f'{s}_MarketUnitValue']) else 0
    #     return stock_assets_value_intraday

    # def calculate_stock_assets_intraday(self, curr, prev=None):
    #     stock_assets_intraday = {}
    #     if prev is not None:
    #         stock_assets_intraday = prev.copy()

    #     for trade, trade_data in curr.groupby('Giao dịch'):
    #         records = trade_data[['Mã CP', 'KL khớp']].to_dict('records')
    #         for rec in records:
    #             sticker = rec['Mã CP']
    #             match_vol = int(rec['KL khớp'])
    #             if trade == 'Mua':
    #                 stock_assets_intraday[sticker] = stock_assets_intraday.get(sticker, 0) + match_vol
    #             elif trade == 'Bán':
    #                 stock_assets_intraday[sticker] = stock_assets_intraday.get(sticker, 0) - match_vol

    #     # Removed zero-assets
    #     removed_sticker = []
    #     for s, v in stock_assets_intraday.items():
    #         if v == 0:
    #             removed_sticker.append(s)
    #     for s in removed_sticker:
    #         del stock_assets_intraday[s]
    #     return stock_assets_intraday