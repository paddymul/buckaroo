import pandas as pd
import numpy as np
from polars import functions as F
from polars import datatypes as pdt
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import ColAnalysis
import warnings

from buckaroo.pluggable_analysis_framework.polars_analysis_management import PolarsAnalysis, normalize_polars_histogram
from buckaroo.pluggable_analysis_framework.polars_utils import NUMERIC_POLARS_DTYPES
from buckaroo.pluggable_analysis_framework.utils import json_postfix

def get_mode(ser):
    mode_raw = ser.mode()
    if len(mode_raw) == 0:
        return np.nan
    else:
        return mode_raw.values[0]

"""
to best take advantage of the DAG and pluggable_analysis_framework, structure your code as follows
a single ColAnalysis can return multiple facts, but those facts shouldn't be interdepedent
That way individual facts can be overridden via the DAG machinery, and other facts that depend on them will
get the proper value

Overtime codebases will probably trend towards many classes with single facts, but it doesn't have to be that way.  Code what comes naturally to you


"""


class DefaultSummaryStats(ColAnalysis):
    provides_summary = [
        'length', 'min', 'max', 'mean', 'nan_count',
        'value_counts', 'mode']

    @staticmethod
    def series_summary(sampled_ser, ser):
        len_ = len(ser)
        value_counts = ser.value_counts()
        nan_count = len_ - len(ser.dropna())
        is_numeric = pd.api.types.is_numeric_dtype(ser)
        is_bool = pd.api.types.is_bool_dtype(ser)

        base_d = dict(
            length=len_,
            nan_count=nan_count,
            value_counts=value_counts,
            mode=get_mode(ser),
            min=np.nan,
            max=np.nan)
        if is_numeric and not is_bool:
            base_d.update({
                'mean': ser.mean(),
                'min': ser.dropna().min(),
                'max': ser.dropna().max()})
        return base_d

class ComputedDefaultSummaryStats(ColAnalysis):

    summary_stats_display = [
        'dtype',
        'length', 'nan_count', 'distinct_count', 'empty_count',
        'empty_per', 'unique_per', 'is_numeric', 'is_integer',
        'is_datetime', 'mode', 'min', 'max','mean']

    requires_summary = ['length', 'nan_count',
                        'value_counts']
    provides_summary = ['distinct_per', 'empty_per', 'unique_per', 'nan_per',
                        'unique_count', 'empty_count', 'distinct_count']

    @staticmethod
    def computed_summary(summary_dict):
        len_ = summary_dict['length']
        value_counts = summary_dict['value_counts']
        try:
            empty_count = value_counts.get('', 0)
        except Exception:
            empty_count = 0
        distinct_count=len(value_counts)
        unique_count = len(value_counts[value_counts==1])

        return dict(
            unique_count=unique_count,
            empty_count=empty_count,
            distinct_count=distinct_count,
            distinct_per=distinct_count/len_,
            empty_per=empty_count/len_,
            unique_per=unique_count/len_,
            nan_per=summary_dict['nan_count']/len_)


def int_digits(n):
    if pd.isna(n):
        return 1
    if np.isnan(n):
        return 1
    if n == 0:
        return 1
    if np.sign(n) == -1:
        return int(np.floor(np.log10(np.abs(n)))) + 2
    return int(np.floor(np.log10(n)+1))



class TypingStats(ColAnalysis):
    provides_summary = [
        'dtype', 'is_numeric', 'is_integer', 'is_datetime', 'is_bool', 'is_float', '_type']
    #requires_summary = ['min', 'max', '_type']

    @staticmethod
    def series_summary(sampled_ser, ser):
        return dict(
            dtype=ser.dtype,
            is_numeric=pd.api.types.is_numeric_dtype(ser),
            is_integer=pd.api.types.is_integer_dtype(ser),
            is_datetime=probable_datetime(ser),
            is_bool=pd.api.types.is_bool_dtype(ser),
            is_float=pd.api.types.is_float_dtype(ser),
            is_string=pd.api.types.is_string_dtype(ser),
            memory_usage=ser.memory_usage())

    @staticmethod
    def computed_summary(summary_dict):
        _type = "obj"
        if summary_dict['is_bool']:
            _type = "boolean"
        elif summary_dict['is_numeric']:
            if summary_dict['is_float']:
                _type = "float"
            else:
                _type = "integer"
        #elif pd.api.types.is_datetime64_any_dtype(ser):
        elif summary_dict['is_datetime']:
            _type = 'datetime'
        elif summary_dict['is_string']:
            _type = "string"
        return dict(_type=_type)


class BasicAnalysis(PolarsAnalysis):
    provides_summary = ['null_count', 'mean', 'max', 'min', 'value_counts']
    select_clauses = [
        F.all().null_count().name.map(json_postfix('null_count')),
        F.all().mean().name.map(json_postfix('mean')),
        F.all().max().name.map(json_postfix('max')),
        F.all().min().name.map(json_postfix('min')),
        F.all().quantile(.99).name.map(json_postfix('quin99')),
        F.all().value_counts(sort=True).slice(0,10).implode().name.map(json_postfix('value_counts'))
    ]


class PlTyping(PolarsAnalysis):
    column_ops = {'dtype':  ("all", lambda col_series: col_series.dtype)}
    provides_summary = ['_type', 'is_numeric']


    @staticmethod
    def computed_summary(summary_dict):
        dt = summary_dict['dtype']

        res = {'is_numeric':  False}

        if dt in pdt.INTEGER_DTYPES:
            t = 'integer'
        elif dt in pdt.DATETIME_DTYPES:
            t = 'datetime'
        elif dt in pdt.FLOAT_DTYPES:
            t = 'float'
        elif dt == pdt.Utf8:
            t = 'string'
        elif dt == pdt.Boolean:
            t = 'boolean'
        else:
            t = 'unknown'
        if t in ('integer', 'float'):
            res['is_numeric'] = True
        res['_type'] = t
        return res

class HistogramAnalysis(PolarsAnalysis):
    column_ops = {
        'hist': (NUMERIC_POLARS_DTYPES,
                 lambda col_series: normalize_polars_histogram(col_series.hist(bin_count=10), col_series))}




class ColDisplayHints(ColAnalysis):
    requires_summary = ['min', 'max', '_type']
    provides_summary = [
        'is_numeric', 'min_digits', 'max_digits', 'type', 'formatter']

    @staticmethod
    def computed_summary(summary_dict):
        base_dict = {'type':summary_dict['_type']}
        if summary_dict['is_datetime']:
            base_dict['formatter'] = 'default'
        if summary_dict['is_numeric'] and not summary_dict['is_bool']:
            base_dict.update({
                'min_digits':int_digits(summary_dict['min']),
                'max_digits':int_digits(summary_dict['max']),
                })
        return base_dict

class PlColDisplayHints(PolarsAnalysis):
    requires_summary = ['min', 'max', '_type', 'is_numeric']
    provides_summary = [
        'min_digits', 'max_digits', 'type', 'formatter']

    @staticmethod
    def computed_summary(summary_dict):
        base_dict = {'type':summary_dict['_type']}
        if summary_dict['_type'] == 'datetime':
            base_dict['formatter'] = 'default'
        if summary_dict['is_numeric']:
            base_dict.update({
                'min_digits':int_digits(summary_dict['min']),
                'max_digits':int_digits(summary_dict['max']),
                })
        return base_dict



PL_Analysis_Klasses = [BasicAnalysis, PlTyping, PlColDisplayHints]
