import pandas as pd
import numpy as np

from buckaroo.jlisp.lispy import s
from buckaroo.jlisp.configure_utils import configure_buckaroo
from .command_tests import assert_to_py_same_transform_df
from buckaroo.auto_clean.cleaning_commands import (
    to_bool, to_datetime, to_int, to_float,
    to_string)

same = assert_to_py_same_transform_df

def test_to_bool():
    base_df = pd.DataFrame({
        'mixed_bool':[True, False, 0, 1, pd.NA], 'b': [pd.NA] * 5})
    
    output_df = same(to_bool, [[s('to_bool'), s('df'), "mixed_bool"]], base_df)
    assert isinstance(output_df['mixed_bool'].dtype , pd.core.arrays.boolean.BooleanDtype)
    assert output_df['mixed_bool'].to_list() == [True, False, False, True, pd.NA]

def test_to_datetime():
    base_df = pd.DataFrame({
        'mixed_dates':['2021-02-03', '2022-05-07', 'asdf', pd.NA], 'b': [pd.NA] * 4})
    
    output_df = same(to_datetime, [[s('to_datetime'), s('df'), "mixed_dates"]], base_df)
    assert pd.api.types.is_datetime64_any_dtype(output_df['mixed_dates'])
    assert output_df['mixed_dates'].to_list() == [
        pd.Timestamp('2021-02-03'), pd.Timestamp('2022-05-07'), pd.NaT, pd.NaT]

def test_to_int():
    base_df = pd.DataFrame({
        'mixed_ints':['3', '4', '3.', 'asdf', pd.NA], 'b': [pd.NA] * 5})
    
    output_df = same(to_int, [[s('to_int'), s('df'), "mixed_ints"]], base_df)
    pd.testing.assert_series_equal(
        output_df['mixed_ints'],
        pd.Series([3,4,3, pd.NA, pd.NA], dtype='UInt8', name='mixed_ints'))

def test_to_float():
    base_df = pd.DataFrame({
        'mixed_floats':['3', '4', '7.1', 'asdf', np.nan], 'b': [pd.NA] * 5})
    
    output_df = same(to_float, [[s('to_float'), s('df'), "mixed_floats"]], base_df)
    pd.testing.assert_series_equal(
        output_df['mixed_floats'],
        pd.Series([3, 4, 7.1, np.nan, np.nan], dtype='float64', name='mixed_floats'))

    

# def test_dropcol():
#     base_df = pd.DataFrame({
#         'a':np.random.randint(1, 10, 5), 'b':np.random.randint(1, 10, 5),
#         'c':np.random.randint(1, 10, 5)})

#     same(DropCol, [[s('dropcol'), s('df'), "a"]], base_df)

# def test_onehot():
#     base_df = pd.DataFrame({
#         'a':['cc', 'cc', 'dd', 'ee', 'ff'], 'b': [pd.NA, 2, 2, 2, pd.NA]})
    
#     output_df = same(OneHot, [[s('onehot'), s('df'), "a"]], base_df)
#     assert output_df.columns.to_list() == ['b', 'cc', 'dd', 'ee', 'ff']
    
# def test_groupby():
#     base_df = pd.DataFrame({
#         'a':['cc', 'cc', 'cc', 'ee', 'ff'], 'b': [pd.NA, 2, 2, 2, pd.NA]})
    
#     output_df = same(GroupBy, [[s('groupby'), s('df'), "a", {'b':'count'}]], base_df)
#     expected_output = pd.DataFrame({'b': {'cc': 2, 'ee': 1, 'ff': 0}},
#                                    index=pd.Index(['cc', 'ee', 'ff'], dtype='object', name='a'))
#     pd.testing.assert_frame_equal(output_df, expected_output)
    
# def test_reindex():
#     base_df = pd.DataFrame({
#         'a':['ca', 'cb', 'cd', 'ee', 'ff'], 'b': [pd.NA, 2, 2, 2, pd.NA]})
    
#     output_df = same(reindex, [[s('reindex'), s('df'), "a"]], base_df)
#     assert output_df.index.to_list() == ['ca', 'cb', 'cd', 'ee', 'ff']
