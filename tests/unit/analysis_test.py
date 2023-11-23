from datetime import datetime as dtdt
import numpy as np
import pandas as pd
from buckaroo.customizations.analysis import DefaultSummaryStats, ColDisplayHints
from buckaroo.customizations.histogram import Histogram


text_ser = pd.Series(["foo", "bar", "baz"])
datelike_ser = pd.Series([
    "2014-01-01 00:00:06",
    "2014-01-01 00:00:38",
    "2014-01-01 00:03:59"

])
datetime_ser = pd.Series([dtdt(2000, 1, 1), dtdt(2001, 1, 1), pd.NaT])
all_nan_ser = pd.Series([np.nan, np.nan])
int_ser = pd.Series([10, 30, -10, 33])
fp_ser = pd.Series([33.2, 83.2, -1.0, 0])

nan_text_ser = pd.Series([np.nan, np.nan, 'y', 'y'])
nan_mixed_type_ser = pd.Series([np.nan, np.nan, 'y', 'y', 8.0])
unhashable_ser = pd.Series([['a'], ['b']])



all_sers = [
    text_ser, datelike_ser, all_nan_ser,
    int_ser, fp_ser, nan_text_ser, nan_mixed_type_ser, unhashable_ser]

def test_text_ser():
    DefaultSummaryStats.series_summary(nan_text_ser,  nan_text_ser)
    DefaultSummaryStats.series_summary(nan_mixed_type_ser, nan_mixed_type_ser)

def test_unhashable():
    result = DefaultSummaryStats.series_summary(unhashable_ser, unhashable_ser)
    #print(result)
    cleaned_result = {i:result[i] for i in result if i!='value_counts'}
    assert     {'length': 2, 'nan_count': 0, 
                'mode': ['a'], 'min': np.nan, 'max': np.nan} == cleaned_result

def test_unhashable3():
    ser = pd.Series([{'a':1, 'b':2}, {'b':10, 'c': 5}])
    DefaultSummaryStats.series_summary(ser, ser) # 'nan_per'
    
def test_default_summary_stats():
    for ser in all_sers:
        print(DefaultSummaryStats.series_summary(ser, ser))

def test_datetime_hints():
    result = ColDisplayHints.summary(
        datetime_ser, {'nan_per':0}, datetime_ser)
    assert     {'type': 'datetime',
                'formatter': 'default',
                'is_integer': False,
                'is_numeric': False,
                } == result    

def test_datetime_histogram():
    series_result = Histogram.series_summary(
        datetime_ser, datetime_ser)
    assert series_result == {'histogram_args':{}}

    summary_result = Histogram.computed_summary(
        dict(histogram_args={},
             length=3, 
             value_counts=pd.Series(
                 [1,1],
                 index=pd.DatetimeIndex([                   
                     dtdt(2000, 1, 1),
                     dtdt(2001, 1, 1)])),

             min=dtdt(2000, 1, 1),
             max=dtdt(2001, 1, 1),
             is_numeric=False,
             nan_per=.33
             ))

    assert     {
                'histogram': [{'cat_pop': 33.0,
                               'name': pd.Timestamp('2000-01-01 00:00:00')},
                              {'cat_pop': 33.0,
                               'name': pd.Timestamp('2001-01-01 00:00:00')},
                              {'name': 'longtail', 'unique': 67.0},
                              {'NA': 33.0, 'name': 'NA'}
                              ],
                } == summary_result
