import os
from pathlib import Path
from datetime import datetime
import gdrive
import pandas as pd


DRIVE_STORE = os.environ['AICV_DRIVE']

class CapitalExtractor:
    def __init__(self):
        self.download_capital_data()
        self.read()

    def download_capital_data(self):
        mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        saved_file = os.path.join(DRIVE_STORE, 'Capital.xlsx')
        response = gdrive.search_capital_file()
        self.file_io = gdrive.download_Docs_Editor_file(response['id'], mimeType=mimeType, saved_file=saved_file)

    def read(self):
        self.data = pd.read_excel(self.file_io.name)
        # Correct format
        self.data['Order Time'] = pd.to_datetime(self.data['Order Time'], format="%Y-%m-%d")
        self.data['Amount'] = self.data['Amount'].astype(int)

    def __get_data(self,customer_name:str) -> pd.DataFrame:
        """Private method"""
        return self.data[self.data['Investor'] == customer_name]

    def get_total_initial_capital(self, customer_name:str) -> int:
        return self.__get_data(customer_name)['Amount'].sum()

    def get_deposit_data(self, customer_name:str) -> pd.DataFrame:
        """Public method"""
        return self.__get_data(customer_name)


