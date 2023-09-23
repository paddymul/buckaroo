import unittest
import pytest

import pandas as pd
from buckaroo import auto_clean as ac
from pandas import NA as NA
from numpy import nan
from pandas.testing import assert_series_equal, assert_frame_equal


DATETIME_META = {'datetime': 0.75, 'datetime_error': 0.25, 'int': 0.25, 'int_error': 0.75, 'float': 0.25, 'float_error': 0.75, 'bool': 0, 'bool_error':1}

INT_META = {'datetime': 0.0, 'datetime_error': 1.0, 'int': 0.75, 'int_error': 0.25, 'float': 0.75, 'float_error': 0.25, 'bool': 0.0, 'bool_error': 1.0}

FLOAT_META = {'datetime': 0.0, 'datetime_error': 1.0, 'int': 0.25, 'int_error': 0.75, 'float': 0.75, 'float_error': 0.25, 'bool': 0.0, 'bool_error': 1.0}

STRING_META =  {'datetime': 0.0, 'datetime_error': 1.0, 'int': 0.0, 'int_error': 1.0, 'float': 0.25, 'float_error': 0.75, 'bool': 0.0, 'bool_error': 1.0}

DATETIME_EDGECASE_META = {'datetime': 1.0, 'datetime_error': 1.0, 'int': 0.0, 'int_error': 1.0, 'float': 0.0, 'float_error': 1, 'bool': 0.0, 'bool_error': 1.0}

BOOL_META = {'bool': .6, 'bool_error': 0.4,
             'datetime': 0.0, 'datetime_error': 1.0,
             'float': 0.6, 'float_error': 0.4,
             'int': 0.6, 'int_error': 0.4}


MIXED_NUMERIC_META = {'bool': 0.0, 'bool_error': 1.0,
                      'datetime': 0.0, 'datetime_error': 1.0,
                      'float': (2/3), 'float_error': (1/3),
                      'int': (2/3), 'int_error': (1/3)}


def assign_values(d, new_values):
    d2 = d.copy()
    d2.update(new_values)
    return d2

DATETIME_DTYPE_META = assign_values(ac.default_type_dict, {'general_type':'datetime', 'exact_type': 'datetime64[ns]'})

MIXED_EXACT = assign_values(ac.default_type_dict, {'exact_type': 'Int64', 'general_type': 'int', 'int':1})

# WEIRD_INT = {'bool': 0.0, 'bool_error': 1.0,
#                       'datetime': 0.0, 'datetime_error': 1.0,
#                       'float': (2/3), 'float_error': (1/3),
#                       'int': (2/3), 'int_error': (1/3)}




def test_get_typing_metadata():
    #assert WEIRD_INT == ac.get_typing_metadata(pd.Series([5, 2, 3.1, None, NA]))
    assert INT_META == ac.get_typing_metadata(pd.Series(['181', '182', '183', 'a']))
    assert FLOAT_META == ac.get_typing_metadata(pd.Series(['181.1', '182.2', '183', 'a']))
    assert STRING_META == ac.get_typing_metadata(pd.Series(['181.1', 'b', 'c', 'a']))
    assert DATETIME_META == ac.get_typing_metadata(pd.Series(['1981-05-11', '1982-05-11', '1983', 'a']))
    assert DATETIME_EDGECASE_META == ac.get_typing_metadata(pd.Series(['00:01.6', '00:01.6', '00:01.6', None]))
    assert DATETIME_DTYPE_META == ac.get_typing_metadata(pd.date_range('2010-01-01', '2010-01-31'))

    assert MIXED_EXACT == ac.get_typing_metadata(pd.Series([NA, 2, 3, NA, NA], dtype='Int64'))
    assert MIXED_NUMERIC_META == ac.get_typing_metadata(pd.Series(['a', 2.0, 3.0, None, NA]))
    

    #there are still problems here, the code isn't properly distinguishing bools from ints and bools
    assert BOOL_META == ac.get_typing_metadata(pd.Series(['a', 'b', False, True, False]))

    #only nans
    print(ac.get_typing_metadata(pd.Series([nan, NA])))
    print(ac.get_typing_metadata(pd.Series([])))


def test_recommend_type():
    assert ac.recommend_type(DATETIME_META) == 'datetime'
    assert ac.recommend_type(INT_META) == 'int'
    assert ac.recommend_type(FLOAT_META) == 'float'
    assert ac.recommend_type(STRING_META) == 'string'
    assert ac.recommend_type(DATETIME_DTYPE_META) == 'datetime'

    WEIRD_INT_SER = pd.Series(['a', 2, 3, 4, None])
    assert ac.recommend_type( ac.get_typing_metadata(WEIRD_INT_SER)) == 'int'

def test_smart_to_int():
    assert_series_equal(
        ac.smart_to_int(pd.Series(['a', 2, 3, 4, None])),
        pd.Series([NA, 2,3,4, NA], dtype='Int8'))


def test_coerce_series():
    assert_series_equal(
        ac.coerce_series(pd.Series(['a', 2, 3, 4, None]), 'int'),
        pd.Series([NA, 2,3,4, NA], dtype='Int64'))

    assert_series_equal(
        ac.coerce_series(pd.Series(['a', False, True, None]), 'bool'),
        pd.Series([NA, False, True, NA], dtype='boolean'))

    assert_series_equal(
        ac.coerce_series(pd.Series(['a', 2.0, 3.0, None, NA]), 'int'),
        pd.Series([NA, 2, 3, NA, NA], dtype='Int64'))

    assert_series_equal(
        ac.coerce_series(pd.Series(['a', 2.0, 3.1, None, NA]), 'float'),
        pd.Series([nan, 2, 3.1, nan, nan], dtype='float'))
    
def test_autotype_df():
    assert_frame_equal(
        ac.auto_type_df(
            pd.DataFrame({
                'int':pd.Series(['a', 2, 3, 4, None]),
                'bool':pd.Series(['a', False, True, None]),
                'int2':pd.Series(['a', 2.0, 3.0, None, NA]),
                'float':pd.Series(['a', 2.0, 3.1, None, NA])})),
            pd.DataFrame({
                'int' :  pd.Series([NA, 2,3,4, NA], dtype='Int64'),
                'bool':  pd.Series([NA, False, True, NA], dtype='boolean'),
                'int2':  pd.Series([NA, 2, 3, NA, NA], dtype='Int64'),
                'float': pd.Series([nan, 2, 3.1, nan, nan], dtype='float')}))