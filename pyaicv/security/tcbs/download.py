import os
import yaml
import logging
import io
import importlib
import pandas as pd
from pathlib import Path
from datetime import datetime
import re


from .data import ReviewDataVersion, RemoteAggregatedData


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AggregateFileNotFound(FileNotFoundError):
    pass


class TCBTransactionHistoryNotFound(FileNotFoundError):
    pass


class UnsupportedFileFormat(Exception):
    pass

class Downloader:
    def __init__(self, ):
        self.local_store = os.environ['AICV_DATABASE_LOCAL']
        self.reviewedDataVersion = ReviewDataVersion(self.local_store)
        self.aggregateData = RemoteAggregatedData(self.local_store)
        self.__connectDriveApi()

    def __read_spec(self):
        from . import config 
        self.tcbs_spec = config.SPECIFICATION.load_spec()

    def __connectDriveApi(self):
        self.drive_api = importlib.import_module('drive', package='google_api')

    def __warmup(self):
        sec_list_configs = yaml.safe_load(os.environ['AICV_SECURITY'])
        for sec_cfg in sec_list_configs:
            if sec_cfg['name'] == 'tcbs':
                self.security_cfg = sec_cfg.copy()
                self.remoteServers = self.security_cfg['metadata']['remoteServers']
                break

    def get_latest_reviewed_data(self):
        review_data = None
        # Check remote ver existed
        if not os.path.exists(self.reviewedDataVersion.remote.filepath):
            # If not search and download it
            files = self.__search_reviewed_data_in_Drive()
            if len(files) == 1:
                filedownload = self.__download_reviewed_data_in_Drive()
                if filedownload is not None:
                    review_data = self.reviewedDataVersion.remote.get_data()
            else:
                # If not valid remote ver, then create it from local with agg-data 
                self.get_latest_aggregated_data()
                self.__generate_ReviewedData_from_AggregatedData()
                review_data = self.reviewedDataVersion.local.get_data()
        else:
            # If exist, read it
            review_data = pd.read_excel(self.reviewedDataVersion.remote.filepath, index_col=0)
        return review_data

    def get_merge_reviewed_data(self):
        # local vs remote -> merge ver, this mer ver will be the final-ver 
        # download remote and prepare local ver
        # Download remote ver
        if self.__download_reviewed_data_in_Drive():
            self.reviewedDataVersion.remote.get_data()
        # Create local ver
        self.get_latest_aggregated_data()
        self.__generate_ReviewedData_from_AggregatedData()
        # Create merge ver
        self.reviewedDataVersion.solve_conflicts()

    def get_latest_aggregated_data(self):
        if not os.path.exists(self.aggregateData.filepath):
            self.__download_transaction_history_files()
            self.__aggregate_data()
        else:
            self.aggregateData.get_data()
        return self.aggregateData.filepath

    def upload_reviewed_data(self):
        self.__read_spec()
        self.get_merge_reviewed_data()
        filepath = self.reviewedDataVersion.merge.filepath
        name = self.tcbs_spec['metadata']['audit']['name']
        root = self.tcbs_spec['metadata']['audit']['root']
        mimeType='application/vnd.google-apps.spreadsheet'
        file_metadata = {
            'name': name,
            'parents': [root],
            'mimeType': mimeType
        }
        # Replace 
        # Delete the old ones, if possible
        files = self.__search_reviewed_data_in_Drive()
        for f in files:
            self.drive_api.delete_file(f['id'])
        # Upload new one
        print(filepath, mimeType, file_metadata)
        _id = self.drive_api.upload_DocEditor_file(filepath, mimeType=mimeType, metadata=file_metadata)
        return _id
        
    def __search_reviewed_data_in_Drive(self):
        self.__read_spec()
        fname = self.tcbs_spec['metadata']['audit']['name']
        folderRoot = self.tcbs_spec['metadata']['audit']['root']
        query_statement = f"name = '{fname}' and parents in '{folderRoot}' and trashed=false"
        files = self.drive_api.search(query_statement)
        if len(files) > 0:
            logger.debug(f'Searched "{fname}" with IDs {[f["id"] for f in files]} in Drive')
        return files

    def __download_reviewed_data_in_Drive(self):
        files = self.__search_reviewed_data_in_Drive()
        if len(files) ==1 :
            fileId = files[0]['id']
            fname = self.tcbs_spec['metadata']['audit']['name']
            mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            saved_file=self.reviewedDataVersion.remote.filepath
            return self.drive_api.download_DocEditor_file(fileId,mimeType,saved_file)
        else:
            return None
            
    def __connectRemoteServers(self):
        for serverInfo in self.remoteServers:
            if serverInfo['name'] == 'drive':
                serverInfo['downloader'] = GoogleDriveServerDownloader()
                serverInfo['local_store'] = serverInfo['downloader'].local_store
                
    def __download_transaction_history_files(self):
        self.__warmup()
        self.__connectRemoteServers()
        for serverInfo in self.remoteServers:
            serverInfo['downloader'].get_latest_update_data()
            serverInfo['filepath'] = serverInfo['downloader'].latest_file
            serverInfo['data'] = serverInfo['downloader'].latest_data

    def __aggregate_data(self):
        for serverInfo in self.remoteServers:
            data = serverInfo['data']
            if data is not None:
                if self.aggregateData.data is None:
                    self.aggregateData.data = data.copy()
                else:
                    self.aggregateData.data = pd.concat([self.aggregateData.data.copy(), data.copy()], ignore_index=True)
        if self.aggregateData.get_data() is not None:
            self.aggregateData.get_data().to_excel(self.aggregateData.filepath)

    def __generate_ReviewedData_from_AggregatedData(self) -> pd.DataFrame:
        logger.info('Generate ReviewData local data from latest aggregated data')
        reviewed_data = self.aggregateData.get_data().copy()
        for i in reviewed_data.columns:
            reviewed_data[i] = reviewed_data[i].astype(str)
        reviewed_data.insert(0, 'Khách hàng', [None] * len(reviewed_data))
        reviewed_data.to_excel(self.reviewedDataVersion.local.filepath)
        self.reviewedDataVersion.local.data = reviewed_data
        return self.reviewedDataVersion.local.get_data()


class GoogleDriveServerDownloader:
    def __init__(self):
        self.drive_api = importlib.import_module('drive', package='google_api')
        self.local_store = os.path.join(os.environ['AICV_DATABASE_LOCAL'], 'drive')
        if not os.path.exists(self.local_store):
            os.makedirs(self.local_store)
        self.latest_file = None
        self.latest_data = None

    def get_latest_update_data(self):
        return self.__get_latest_transaction_data()

    def __get_latest_transaction_data(self) -> pd.DataFrame:
        self.latest_file = self.__get_latest_transaction_file()
        if self.latest_file is not None:
            table = self.__export_corrected_transaction_table(self.latest_file)
            if table is not None:
                table = self.__correct_data_format(table)
                logger.debug(f'Latest TCB transaction table has {len(table)} records')
                self.latest_data = table
                return self.latest_data
        return None

    def __get_latest_transaction_file(self) -> str:
        sort_files = self.__sort_transaction_files()
        if len(sort_files) > 0:
            return list(sort_files.keys())[0]
        raise TCBTransactionHistoryNotFound('No transaction file found')

    def __sort_transaction_files(self) -> dict:
        fileInfos = self.__download_transaction_history_files()
        fileNames = [f.name for f in fileInfos]
        export_map = {}
        for f in fileNames:
            ct = self.__read_TCBS_transaction_file(f)
            export_datetime = None
            if ct is not None:
                export_datetime = self.__extract_export_date(ct)
            export_map[f] = export_datetime
        sort_map = {k: v for k, v in sorted(export_map.items(), key=lambda item: item[1])}
        return sort_map

    def __read_TCBS_transaction_file(self,filepath: str) -> pd.DataFrame:
        """Return pd.DataFrame content of transaction file"""
        filepath = Path(filepath)
        ext = filepath.suffix
        if (ext == '.xlsx') or (ext == '.xls'):
            f_content = pd.read_excel(filepath)
            return f_content
        raise UnsupportedFileFormat('Inapproriate or Unsupported file format')

    def __export_corrected_transaction_table(self, filepath:str) -> pd.DataFrame:
        df = pd.read_excel(filepath)
        # Find Ma CP index
        first_col = df.iloc[:,1]
        cond_values = first_col.str.contains('Ngày GD').fillna(False)
        # row_index = cond_values[cond_values==True].index.values[0]
        row_index = cond_values[cond_values==True].index.values[0]
        df_below = df.iloc[row_index+1:]
        table_cond  = df_below.iloc[:,0].fillna('NoValue').astype(str).apply(lambda x: len(x) <= 3)
        lower_index = table_cond[table_cond==False].index + 1
        skiprows_index = list(range(row_index+1)) + (lower_index.tolist())
        # Reread table with found row_index
        reread_df = pd.read_excel(filepath,skiprows=skiprows_index)
        return reread_df

    def __download_transaction_history_files(self) -> list[io.FileIO]:
        logger.info('Download all TCB transaction history')
        files = self.__search_transaction_history_files()
        files_info = []
        for i, f in enumerate(files):
            txn_file = os.path.join(self.local_store, f'TCBS_transaction_history_{i}.xlsx')
            files_info.append(self.drive_api.download_blob_file(f['id'], txn_file))
        return files_info

    def __search_transaction_history_files(self) -> list[dict]:
        query_statement = "name contains 'Lịch sử giao dịch cổ phiếu_Huỳnh Thanh Quan' and mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'"
        files = self.drive_api.search(query_statement)
        if len(files) > 0:
            logger.debug(f'Searched "Lịch sử giao dịch cổ phiếu_Huỳnh Thanh Quan" with IDs {[f["id"] for f in files]} in Drive')
        return files

    def __extract_export_date(self, df: pd.DataFrame) -> datetime:
        first_col = df.iloc[:,0]
        cond_values = first_col.str.contains('Ngày xuất báo cáo').fillna(False)
        row_index = cond_values[cond_values==True].index
        statement = df.iloc[row_index,0].values[0]
        time_p = r'(\d+)h(\d+)'
        date_p = r'(\d+)/(\d+)/(\d+)'
        time_export = re.findall(time_p, statement)[0]
        date_export = re.findall(date_p, statement)[0]
        correct_form = f'{date_export[2]}-{date_export[1]}-{date_export[0]} {time_export[0]}:{time_export[1]}'
        export_datetime = datetime.strptime(f'{correct_form}', "%Y-%m-%d %H:%M")
        return export_datetime

    def __correct_data_format(self, df:pd.DataFrame) -> pd.DataFrame:
        if 'Ngày GD' in df.columns:
            df['Ngày GD'] = pd.to_datetime(df['Ngày GD'].str.strip(), format='%d/%m/%Y')
        return df
