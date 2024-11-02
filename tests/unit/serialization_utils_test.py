import pytest
import pandas as pd
from buckaroo.serialization_utils import df_to_obj
from pandas.core.dtypes.dtypes import DatetimeTZDtype


def test_df_to_obj():
    named_index_df = pd.DataFrame(
        dict(names=['one', 'two', 'three'],
             values=[1, 2, 3])).set_index('names')

    serialized_df = df_to_obj(named_index_df, {})
    assert serialized_df['data'][0]['names'] == 'one'

from pandas._libs.tslibs import timezones
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
    df.to_json(orient='table')
    return df

dt_strs = ['2024-06-24 09:32:00-04:00', '2024-06-24 09:33:00-04:00', '2024-06-24 09:34:00-04:00']
dt_series = pd.Series(pd.to_datetime(dt_strs).values)
dt_series_with_tz = pd.Series(pd.to_datetime(dt_strs).tz_convert('UTC').values)

dt_index_series = pd.Series(pd.to_datetime(dt_strs))
dt_index_series_with_tz = pd.Series(pd.to_datetime(dt_strs).tz_convert('UTC'))

dt_index = pd.DatetimeIndex(pd.to_datetime(dt_strs))
dt_index_with_tz = pd.DatetimeIndex(pd.to_datetime(dt_strs).tz_convert('UTC'))

def test_is_col_dt_safe():
    # it works for non dt series
    assert is_col_dt_safe(pd.Series(dt_strs)) == True
    assert is_col_dt_safe(pd.Index(dt_strs)) == True
    assert is_col_dt_safe(pd.RangeIndex(0, 3)) == True
    #no tz
    assert is_col_dt_safe(dt_series) == True
    assert is_col_dt_safe(dt_index_series) == False
    assert is_col_dt_safe(dt_index_series_with_tz) == True
    assert is_col_dt_safe(dt_series_with_tz) == True
    assert is_col_dt_safe(dt_index) == False
    assert is_col_dt_safe(dt_index_with_tz) == True

def test_is_dataframe_datetime_safe():
    assert is_dataframe_datetime_safe(pd.DataFrame({'a':dt_strs})) == True
    assert is_dataframe_datetime_safe(pd.DataFrame({'a':dt_series})) == True
    assert is_dataframe_datetime_safe(pd.DataFrame({'a':dt_index_series})) == False
    assert is_dataframe_datetime_safe(pd.DataFrame({'a':dt_index_series_with_tz})) == True
    assert is_dataframe_datetime_safe(pd.DataFrame({'a':dt_series_with_tz})) == True
    assert is_dataframe_datetime_safe(pd.DataFrame({'a':dt_strs}, index=dt_index)) == False
    assert is_dataframe_datetime_safe(pd.DataFrame({'a':dt_strs}, index=dt_index_with_tz)) == True

def test_check_and_fix_df():
    def recheck(df):
        return is_dataframe_datetime_safe(check_and_fix_df(df))
    
    assert recheck(pd.DataFrame({'a':dt_strs})) == True
    assert recheck(pd.DataFrame({'a':dt_series})) == True
    assert recheck(pd.DataFrame({'a':dt_series_with_tz})) == True
    assert recheck(pd.DataFrame({'a':dt_strs}, index=dt_index)) == True
    assert recheck(pd.DataFrame({'a':dt_strs}, index=dt_index_with_tz)) == True

    with pytest.raises(DuplicateColumnsException):
        check_and_fix_df(pd.DataFrame([['a', 'b'], [1,2]], columns = [1,1]))
    
# def test_int_overflow_validation():
#     value=float('nan')
#     class Model(BaseModel):
#         a: int
#     Model(a=3)
#     with pytest.raises(ValidationError) as exc_info:
#         Model(a=value)
#     assert exc_info.value.errors(include_url=False) == [
#         {'type': 'finite_number', 'loc': ('a',), 'msg': 'Input should be a finite number',
#          'input': value
#          }]
