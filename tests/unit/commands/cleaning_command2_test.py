import pandas as pd
import numpy as np

from buckaroo.jlisp.lisp_utils import s
from .command_test import assert_to_py_same_transform_df

from buckaroo.customizations.pandas_cleaning_commands import (
    IntParse,
    StrBool,
    USDate,
    StripIntParse)


same = assert_to_py_same_transform_df

expected_df = pd.DataFrame({
        'mixed_bool': pd.Series([
            True,
            True, 
            True, 
            True,
            False,
            False,
            True,
            False,
            False,
            False,
            False,
            True,
            None
        ], dtype='boolean')})

# expected_df = pd.DataFrame({
#         'mixed_bool': pd.Series([
#             5, #True,
#             6, #True, 
#             7, #True, 
#             8, #True,

#             False,
#             False,
#             True,
#             False,
#             False,
#             False,
#             False,
#             True,
#             None
#         ])})

def test_str_bool():
    base_df = pd.DataFrame({
        'mixed_bool': [
            True,
            "True",
            "Yes",
            "On",
            "false",
            False,
            "1",
            "Off",
            "0",
            " 0",
            "No",
            1,
            None,
        ]})
    
    output_df = same(StrBool, [[s('str_bool'), s('df'), "mixed_bool"]], base_df)
    assert isinstance(output_df['mixed_bool'].dtype , pd.core.arrays.boolean.BooleanDtype)
    assert output_df['mixed_bool'].to_list() == expected_df['mixed_bool'].to_list()

# def test_to_float():
#     base_df = pd.DataFrame({
#         'mixed_floats':['3', '4', '7.1', 'asdf', np.nan], 'b': [pd.NA] * 5})
    
#     output_df = same(to_float, [[s('to_float'), s('df'), "mixed_floats"]], base_df)
#     pd.testing.assert_series_equal(
#         output_df['mixed_floats'],
#         pd.Series([3, 4, 7.1, np.nan, np.nan], dtype='float64', name='mixed_floats'))

# def _test_to_string():
#     """
#     skipping for now.  works on my machine against pandas 2.1.1 fails in CI against pandas 1.3.5
#     """
#     base_df = pd.DataFrame({
#         'mixed_strings':['a', 'b', pd.NA], 'b': [pd.NA] * 3})
    
#     output_df = same(to_string, [[s('to_string'), s('df'), "mixed_strings"]], base_df)
#     pd.testing.assert_series_equal(
#         output_df['mixed_strings'],
#         pd.Series(['a', 'b', pd.NA], dtype='string', name='mixed_strings'))

