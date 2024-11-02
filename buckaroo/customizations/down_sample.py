import pandas as pd
import numpy as np
from pandas._libs.tslibs import timezones
from pandas.core.dtypes.dtypes import DatetimeTZDtype

def is_col_dt_safe(col_or_index):
    if isinstance(col_or_index.dtype, DatetimeTZDtype):
        dt = col_or_index.dtype
        if timezones.is_utc(dt.tz):
            return True
        elif hasattr(dt.tz, 'zone'):
            return True
        return False
    return True

def is_dataframe_datetime_safe(df):
    for col in df:
        if not is_col_dt_safe(df[col]):
            return False
    if not is_col_dt_safe(df.index):
        return False
    return True

def fix_df_dates(df):
    for col in df:
        if not is_col_dt_safe(df[col]):
            print("col", col)
            df[col] = df[col].tz_convert('UTC')
    if not is_col_dt_safe(df.index):
        df.index = df.index.tz_convert('UTC')
    return df

class DuplicateColumnsException(Exception):
    pass


def check_and_fix_df(df):
    if not df.columns.is_unique:
        raise DuplicateColumnsException("Your dataframe has duplicate columns. Buckaroo requires distinct column names")
    if not is_dataframe_datetime_safe(df):
        print("your dataframe has a column or index with a datetime series without atimezone.  Setting a default UTC timezone to proceed with display. https://github.com/paddymul/buckaroo/issues/277")
        return fix_df_dates(df)
    return df

def get_outlier_idxs(ser):
    if not pd.api.types.is_numeric_dtype(ser.dtype):
        return []
    outlier_idxs = []
    outlier_idxs.extend(ser.nlargest(5).index)
    outlier_idxs.extend(ser.nsmallest(5).index)
    return outlier_idxs


def polars_sample(df, sample_size=500, include_outliers=False):
    return df.sample(min(len(df), sample_size))

def sample(df, sample_size=500, include_outliers=False):
    # sampling is a very poor places for this, it should come in an explicit check step.
    # but for now, this will work
    df = check_and_fix_df(df)

    include_outliers = False
    if len(df) <= sample_size:
        return df

    try:
        import polars
        if isinstance(df, polars.DataFrame):
            return polars_sample(df, sample_size, include_outliers)
    except ImportError:
        pass
    sdf = df.sample(np.min([sample_size, len(df)]))
    if True:
        return sdf
    #non_unique indexes are very slow
    if include_outliers and sdf.index.is_unique:
        outlier_idxs = []
        for col in df.columns:
            outlier_idxs.extend(get_outlier_idxs(df[col]) )
        outlier_idxs.extend(sdf.index)
        uniq_idx = np.unique(outlier_idxs)
        return df.loc[uniq_idx]
    return sdf

