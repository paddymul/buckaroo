import pandas as pd
import numpy as np
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import ColAnalysis
import warnings

def probable_datetime(ser):
    #turning off warnings in this single function is a bit of a hack.
    #Understandable since this is explicitly abusing pd.to_datetime
    #which throws warnings.

    warnings.filterwarnings('ignore')
    s_ser = ser.sample(np.min([len(ser), 500]))
    try:
        dt_ser = pd.to_datetime(s_ser)
        #pd.to_datetime(1_00_000_000_000_000_000) == pd.to_datetime('1973-01-01') 
        warnings.filterwarnings('default')
        if dt_ser.max() < pd.to_datetime('1973-01-01'):
            return False
        return True
        
    except Exception:
        warnings.filterwarnings('default')
        return False

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

class TypingStats(ColAnalysis):
    provides_summary = [
        'dtype', 'is_numeric', 'is_integer', 'is_datetime',]

    @staticmethod
    def series_summary(sampled_ser, ser):
        return dict(
            dtype=ser.dtype,
            is_numeric=pd.api.types.is_numeric_dtype(ser),
            is_integer=pd.api.types.is_integer_dtype(ser),
            is_datetime=probable_datetime(ser),
            memory_usage=ser.memory_usage()
            )

class DefaultSummaryStats(ColAnalysis):
    provides_summary = [
        'length', 'min', 'max', 'mean', 'nan_count',
        'value_counts', 'mode']

    
    @staticmethod
    def series_summary(sampled_ser, ser):
        l = len(ser)
        value_counts = ser.value_counts()
        nan_count = l - len(ser.dropna())
        is_numeric = pd.api.types.is_numeric_dtype(ser)
        is_bool = pd.api.types.is_bool_dtype(ser)

        base_d = dict(
            length=l,
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
    #'nan_per'

    requires_summary = ['length', 'nan_count',
                        'value_counts']
    provides_summary = ['distinct_per', 'empty_per', 'unique_per', 'nan_per',
                        'unique_count', 'empty_count', 'distinct_count']

    @staticmethod
    def computed_summary(summary_dict):
        l = summary_dict['length']
        value_counts = summary_dict['value_counts']
        try:
            empty_count = value_counts.get('', 0)
        except:
            empty_count = 0
        distinct_count=len(value_counts)
        unique_count = len(value_counts[value_counts==1])

        return dict(
            unique_count=unique_count,
            empty_count=empty_count,
            distinct_count=distinct_count,
            distinct_per=distinct_count/l,
            empty_per=empty_count/l,
            unique_per=unique_count/l,
            nan_per=summary_dict['nan_count']/l)


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


class ColDisplayHints(ColAnalysis):
    requires_summary = ['min', 'max']
    provides_summary = [
        'is_numeric', 'is_integer', 'min_digits', 'max_digits', 'type', 'formatter']

    @staticmethod
    def summary(sampled_ser, summary_ser, ser):
        is_numeric = pd.api.types.is_numeric_dtype(sampled_ser)
        is_bool = pd.api.types.is_bool_dtype(sampled_ser)
        _type = "obj"
        extras = {}
        if is_bool:
            _type = "boolean"
        elif is_numeric:
            if pd.api.types.is_float_dtype(sampled_ser):
                _type = "float"
            else:
                _type = "integer"
        elif pd.api.types.is_datetime64_any_dtype(ser):
            extras = {'type':'datetime', 'formatter': 'default'}
        elif pd.api.types.is_string_dtype(sampled_ser):
            _type = "string"
        base_dict = dict(
            type=_type,
            is_numeric=is_numeric,
            is_integer=pd.api.types.is_integer_dtype(sampled_ser))
        base_dict.update(extras)
        if is_numeric and not is_bool:
            base_dict.update({
                'min_digits':int_digits(summary_ser.loc['min']),
                'max_digits':int_digits(summary_ser.loc['max']),
                })
        return base_dict

