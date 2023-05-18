import numpy as np
import pandas as pd
# from pandas.api.types import is_datetime64_any_dtype

def convert_strformat_to_save(df):
    # pd_datetime_col = [i for i in df.columns if is_datetime64_any_dtype(i)]
    for c in df.select_dtypes(include=[np.datetime64]).columns:
        df[c] = df[c].astype(str)
    return df