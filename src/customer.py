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
        self.infer_total_assets_value()

    def get_activity_time(self, x):
        if not pd.isna(x['TxnDatetime']):
            return pd.to_datetime(x['TxnDatetime'], format='%Y-%m-%d %H:%M:%S.%f')
        if not pd.isna(x['Order Time']):
            return pd.to_datetime(x['Order Time'], format='%Y-%m-%d %H:%M:%S.%f')
        return pd.to_datetime(x['date'], format='%Y-%m-%d %H:%M:%S.%f')

    def infer_total_assets_value(self):
        # Spread capital data in long format 
        capital_detail = self.lifetime_table.copy()
        capital_detail = capital_detail.merge(self.capital_history[['Order Time', 'Type', 'Amount']], how='left', left_on='date', right_on='Order Time')

        # Spread transaction data in long format 
        transaction_detail = self.transaction_history.copy()
        transaction_detail = transaction_detail.drop(columns=['Khách hàng', 'KL đặt', 'Giá đặt (VND)', 'Phí (VND)', 'Thuế (VND)', 'Giá vốn', 'Lãi lỗ (VND)', 'Kênh GD', 'Trạng thái', 'Loại lệnh'])
        transaction_detail['TxnTime'] = transaction_detail['Số hiệu lệnh'].astype(str).apply(lambda x:int(x[-6:]))
        transaction_detail['TxnDatetime'] = transaction_detail['Ngày GD'] + transaction_detail['TxnTime'].apply(lambda x: timedelta(milliseconds=x))
        transaction_detail = pd.merge(self.lifetime_table, transaction_detail, how='left', left_on='date', right_on='Ngày GD')

        # Concat together to return all tracking activities data
        cust_tracking_act = pd.concat([capital_detail, transaction_detail])
        cust_tracking_act['ActivityTime'] = cust_tracking_act.apply(lambda x: self.get_activity_time(x), axis=1)
        cust_tracking_act['ActivityTime_str'] = cust_tracking_act['ActivityTime'].apply(lambda x: x.strftime(format='%Y-%m-%d %H:%M:%S.%f') if not pd.isna(x) else None)
        cust_tracking_act = cust_tracking_act.sort_values('ActivityTime').reset_index(drop=True)

        # Get unique stickers
        unique_stickers = cust_tracking_act['Mã CP'].dropna().unique()

        # Get market data
        lifetime = cust_tracking_act['date'].unique()
        market = pd.DataFrame({'date': lifetime})
        start_date, end_date = (lifetime.min() - timedelta(days=1)).strftime('%Y-%m-%d'), lifetime.max().strftime('%Y-%m-%d')
        for s in unique_stickers:
            symbol_stock_data = vnstock.stock_historical_data(symbol=s, start_date=start_date, end_date=end_date)
            symbol_stock_data = symbol_stock_data[['TradingDate', 'Close']]
            symbol_stock_data = symbol_stock_data.rename(columns={'TradingDate': 'date', 'Close': f'{s}_MarketUnitValue'})
            market = market.merge(symbol_stock_data,how='left', left_on='date', right_on='date')

        stock_market_value = cust_tracking_act.merge(market,how='left', left_on='date', right_on='date')

        self.total_assets_value = self.calculate_asset_value(stock_market_value)
        # self.total_assets_value.to_excel(f'{self.full_name}_test.xlsx')

    def refresh_current_stock_asset(self, curr_asset):
        alter_records = []
        for record in curr_asset:
            alter_record = {
                'Sticker': record['Sticker'],
                'Vol': record['Vol']
            }
            alter_records.append(alter_record)
        if len(alter_records) > 0:
            alter_records = pd.DataFrame(alter_records)
            alter_records = alter_records.groupby('Sticker')['Vol'].sum().reset_index()
            alter_records = alter_records.to_dict('records')
            return alter_records
        return []

    def add_stock_asset(self,curr_asset, sticker, vol, price):
        # Refresh the last txn price
        curr_asset = self.refresh_current_stock_asset(curr_asset)
        record = {
            'Sticker': sticker,
            'Vol': vol,
            'Price': price
        }
        curr_asset.append(record)
        return curr_asset

    def remove_stock_asset(self,curr_asset, sticker, vol, price):
        curr_asset = self.refresh_current_stock_asset(curr_asset)
        for asset in curr_asset:
            if asset['Sticker'] == sticker:
                asset['Vol'] -= vol
        return curr_asset

    def get_stock_market_value(self, curr_asset, market_data):
        total_stock_value = 0
        for record in curr_asset:
            sticker = record['Sticker']
            vol = record['Vol']
            if 'Price' not in record.keys():
                market_uvalue = market_data[f'{sticker}_MarketUnitValue']
            else:
                market_uvalue = record['Price']
            market_total_value = vol * market_uvalue
            total_stock_value += market_total_value
        return total_stock_value

    def calculate_asset_value_intraday(self, curr_data, prev_data=None):
        cash, stock_value, total_assets = 0,0,0
        stock_assets = []
        
        if prev_data is not None:
            cash = prev_data['Cash']
            stock_value = prev_data['StockValue']
            stock_assets = prev_data['StockAssets'] if prev_data['StockAssets'] else []

        # Cash 
        if curr_data['Type'] == 'DEPOSIT':
            cash += curr_data['Amount']
        if curr_data['Type'] == 'WITHDRAWAL':
            cash -= curr_data['Amount']

        # Stock trade
        if curr_data['Giao dịch'] == 'Mua':
            cash -= curr_data['Giá trị khớp (VND)']
            stock_value += curr_data['Giá trị khớp (VND)']
            stock_assets = self.add_stock_asset(stock_assets, curr_data['Mã CP'], curr_data['KL khớp'], curr_data['Giá khớp (VND)'])

        if curr_data['Giao dịch'] == 'Bán':
            cash += curr_data['Giá trị khớp (VND)']
            stock_value -= curr_data['Giá trị khớp (VND)']
            stock_assets = self.remove_stock_asset(stock_assets, curr_data['Mã CP'], curr_data['KL khớp'], curr_data['Giá khớp (VND)'])
        
        if pd.isna(curr_data['Giao dịch']):
            stock_assets = self.refresh_current_stock_asset(stock_assets)

        stock_value = self.get_stock_market_value(stock_assets, curr_data)
        total_assets = stock_value + cash
        return cash, stock_value, stock_assets, total_assets

    def calculate_asset_value(self, acc_asset_value):
        acc_asset_value['Cash'] = 0
        acc_asset_value['StockAssets'] = None
        acc_asset_value['StockValue'] = 0
        acc_asset_value['TotalAssets'] = 0
        prev_data = None
        for idx, curr_row in acc_asset_value.iterrows():
            if idx == 0:
                cash, stock_value, stock_assets, total_assets = self.calculate_asset_value_intraday(curr_row)
                acc_asset_value.at[idx,'Cash'] = cash
                acc_asset_value.at[idx,'StockValue'] = stock_value
                acc_asset_value.at[idx,'StockAssets'] = stock_assets
                acc_asset_value.at[idx,'TotalAssets'] = total_assets
            else:
                prev_data = acc_asset_value.iloc[idx-1]
                cash, stock_value, stock_assets, total_assets = self.calculate_asset_value_intraday(curr_row, prev_data)
                acc_asset_value.at[idx,'Cash'] = cash
                acc_asset_value.at[idx,'StockValue'] = stock_value
                acc_asset_value.at[idx,'StockAssets'] = stock_assets
                acc_asset_value.at[idx,'TotalAssets'] = total_assets
        return acc_asset_value
