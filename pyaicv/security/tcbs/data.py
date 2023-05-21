import os
import sys
import pandas as pd


class TCBSData:
    pass


class TCBSExcelData(TCBSData):
    def __init__(self):
        self.filepath = None
        self.data = None

    def __get_safe_data(self):
        if self.data is None:
            if os.path.exists(self.filepath):
                self.data = pd.read_excel(self.filepath, index_col=0)
        else:
            if not os.path.exists(self.filepath):
                self.data.to_excel(self.filepath)
        return self.data

    def get_data(self):
        return self.__get_safe_data()


class ReviewedData(TCBSExcelData):
    __annotation = "Review Data by manually"
    def __init__(self, local_store, suffix=''):
        self.local_store = local_store
        self.suffix = suffix
        self.filepath = os.path.join(local_store, f'ReviewedData{suffix}.xlsx')
        self.data = None


class RemoteAggregatedData(TCBSExcelData):
    __annotation = "Remote Parties-Aggregated Data"
    def __init__(self, local_store):
        self.local_store = local_store
        self.filepath = os.path.join(local_store, 'RemoteAggregatedData.xlsx')
        self.data = None


class ReviewDataVersion:
    def __init__(self, local_store):
        self.local_store = local_store
        self.local = ReviewedData(local_store, '_local')
        self.remote = ReviewedData(local_store, '_remote')
        self.merge = ReviewedData(local_store, '_merge')

    def solve_conflicts(self):
        data1 = self.local.get_data()
        data2 = self.remote.get_data()
        assert data1 is not None and isinstance(data1, pd.DataFrame)
        if data2 is not None and isinstance(data2, pd.DataFrame):

            conflict_cols =['Số hiệu lệnh', 'KL khớp']

            data1['Số hiệu lệnh'] = data1['Số hiệu lệnh'].astype(str).str.strip()
            data2['Số hiệu lệnh'] = data2['Số hiệu lệnh'].astype(str).str.strip()
            data1['KL khớp'] = data1['KL khớp'].astype(int)
            data2['KL khớp'] = data2['KL khớp'].astype(int)

            merged = data2[['Số hiệu lệnh', 'KL khớp']].merge(data1, how='outer', left_on=conflict_cols, right_on=conflict_cols)
            merged = merged.sort_values(by='Ngày GD')
            merged = merged.reset_index(drop=True)
            merged = merged[data2.columns]
        else:
            merged = data1
            self.merge.data = merged.copy()
            self.merge.get_data().to_excel(self.merge.filepath)
