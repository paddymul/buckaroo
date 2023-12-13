from unittest import TestCase

import polars as pl
import numpy as np
from polars import functions as F
from buckaroo.customizations.polars_analysis import VCAnalysis, BasicAnalysis, HistogramAnalysis

from buckaroo.pluggable_analysis_framework.utils import (json_postfix, replace_in_dict)

from buckaroo.pluggable_analysis_framework.polars_analysis_management import (
    full_produce_summary_df,
    produce_series_df, PolarsAnalysis, extract_table_hint)

test_df = pl.DataFrame({
        'normal_int_series' : pl.Series([1,2,3,4]),
        #'empty_na_ser' : pl.Series([pl.Null] * 4, dtype="Int64"),
        'float_nan_ser' : pl.Series([3.5, np.nan, 4.8, 2.2])
    })

word_only_df = pl.DataFrame({'letters': 'h o r s e'.split(' ')})

df = pl.read_csv('./examples/data/2014-01-citibike-tripdata.csv')

empty_df = pl.DataFrame({})
#empty_df_with_columns = pl.DataFrame({}, columns=[0])



class SelectOnlyAnalysis(PolarsAnalysis):

    select_clauses = [
        F.all().null_count().name.map(json_postfix('null_count')),
        F.all().mean().name.map(json_postfix('mean')),
        F.all().quantile(.99).name.map(json_postfix('quin99'))]


def test_produce_series_df():
    """just make sure this doesn't fail"""
    
    sdf, errs = produce_series_df(
        test_df, [SelectOnlyAnalysis], 'test_df', debug=True)
    expected = {
        'float_nan_ser':      {'mean': None, 'null_count':  0, 'quin99': None},
        'normal_int_series':  {'mean': 2.5,  'null_count':  0, 'quin99':  4.0}}
    dsdf = replace_in_dict(sdf, [(np.nan, None)])
    assert dsdf == expected

class MaxAnalysis(PolarsAnalysis):
    select_clauses = [F.all().max().name.map(json_postfix('max'))]

def test_produce_series_combine_df():
    """just make sure this doesn't fail"""
    
    sdf, errs = produce_series_df(
        test_df, [SelectOnlyAnalysis, MaxAnalysis], 'test_df', debug=True)
    expected = {
        'float_nan_ser':      {'mean': None, 'null_count':  0, 'quin99': None, 'max': 4.8},
        'normal_int_series':  {'mean': 2.5,  'null_count':  0, 'quin99':  4.0, 'max': 4.0},
        }
    dsdf = replace_in_dict(sdf, [(np.nan, None)])
    assert dsdf == expected

def test_produce_series_column_ops():
    mixed_df = pl.DataFrame(
        {'string_col': ["foo", "bar", "baz"] + [""]*2,
         'int_col':[1,2,3,30, 100],
         'float_col':[1.1, 1.1, 3, 3, 5]})

    summary_df, _unused = produce_series_df(mixed_df, [HistogramAnalysis])
    assert summary_df["string_col"] == {}

    assert summary_df["int_col"]["histogram_args"]["meat_histogram"] == (
        [2,  0,  0,  0,  0,  0,  0,  0,  0,  1],
        [1.0,  4.0,  7.0,  10.0,  13.0,  16.0,  19.0,  22.0,  25.0,  28.0,  100.0],)
    


def test_histogram_analysis():
    cats = [chr(x) for x in range(97, 102)] * 2 
    cats += [chr(x) for x in range(103,113)]
    cats += ['foo']*30 + ['bar'] * 50

    df = pl.DataFrame({'categories': cats, 'numerical_categories': [3]*30 + [7] * 70})
    HA_CLASSES = [VCAnalysis, BasicAnalysis, HistogramAnalysis]
    summary_df, _unused, errs = full_produce_summary_df(df, HA_CLASSES, debug=True)
    assert summary_df["categories"]["categorical_histogram"] == {'bar': 0.5, 'foo': 0.3, 'longtail': 0.1, 'unique': 0.1}
    assert summary_df["numerical_categories"]["categorical_histogram"] == {3:.3, 7:.7, 'longtail': 0.0, 'unique': 0.0}
    
    


def test_extract_table_hint():

    summary_dict = {'a': {'null_count': 0,
                          'mean': 35.0,
                          'max': 100,
                          'min': 2,
                          'is_numeric': True,
                          '_type': 'integer',
                          'type': 'integer'}
                    }


    expected =  {
        'a': {
            'type':'integer',
            'is_numeric': True,
            'is_integer': None,
            'min_digits':None,
            'max_digits':None,
            'formatter':None,
            'histogram': []}}
    TestCase().assertDictEqual(expected, extract_table_hint(summary_dict, ['a']))
