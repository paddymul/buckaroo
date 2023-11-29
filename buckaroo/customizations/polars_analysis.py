import polars as pl
import pandas as pd
import numpy as np
from polars import functions as F
from polars import datatypes as pdt
from buckaroo.customizations.analysis_utils import int_digits
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




class ComputedDefaultSummaryStats(PolarsAnalysis):
    summary_stats_display = [
        'dtype',
        'length', 'nan_count', 'distinct_count', 'empty_count',
        'empty_per', 'unique_per', 'is_numeric', 
        'mode', 'min', 'max','mean']

    requires_summary = ['length', 'nan_count',
                        'unique_count', 'empty_count', 'distinct_count']
    provides_summary = ['distinct_per', 'empty_per', 'unique_per', 'nan_per']
                        

    @staticmethod
    def computed_summary(summary_dict):
        len_ = summary_dict['length']
        
        return dict(
            distinct_per=summary_dict['distinct_count']/len_,
            empty_per=summary_dict.get('empty_count',0)/len_,
            unique_per=summary_dict['unique_count']/len_,
            nan_per=summary_dict['nan_count']/len_)



class BasicAnalysis(PolarsAnalysis):
    provides_summary = ['length', 'nan_count', 'min', 'max', 'min',
                        'mode', 'mean',
                        'value_counts',
                        'unique_count', 'empty_count', 'distinct_count']
    select_clauses = [
        F.all().len().name.map(json_postfix('length')),
        F.all().null_count().name.map(json_postfix('nan_count')),
        F.all().min().name.map(json_postfix('min')),
        F.all().max().name.map(json_postfix('max')),
        #F.all().mode().implode().name.map(json_postfix('mode')),
        F.all().mean().name.map(json_postfix('mean')),
        F.all().value_counts(sort=True).slice(10).implode().name.map(json_postfix('value_counts')),
        F.col(pl.Utf8).str.count_matches("^$").sum().name.map(json_postfix('empty_count')),
        F.all().approx_n_unique().name.map(json_postfix('distinct_count')),
        (F.all().len() - F.all().is_duplicated().sum()).name.map(json_postfix('unique_count')),
    ]

class PlTyping(PolarsAnalysis):
    column_ops = {'dtype':  ("all", lambda col_series: col_series.dtype)}
    provides_summary = ['dtype', '_type', 'is_numeric']


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

PL_Analysis_Klasses = [BasicAnalysis, PlTyping, PlColDisplayHints,
                       #HistogramAnalysis,
                       ComputedDefaultSummaryStats]

