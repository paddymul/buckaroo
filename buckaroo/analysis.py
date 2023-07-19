from functools import reduce
import pandas as pd
from pandas.io.json import dumps as pdumps
import numpy as np
from buckaroo.pluggable_analysis_framework import ColAnalysis
'''
class DfStats(object):
    def __init__(self,
            df,
            annotate_funcs=[add_col_rankings],
            # summary_func=summary_stats.summarize_df,
            # order_col_func=summary_stats.order_columns):
            summary_func=summarize_df,
            order_col_func=order_columns):

        rows = len(df)
        cols = len(df.columns)
        item_count = rows * cols


        if item_count > FAST_SUMMARY_WHEN_GREATER:
            df = df.sample(np.min([50_000, len(df)]))
        self.df = df
        self.sdf = summary_func(df)
        for func in annotate_funcs:
            func(df, self.sdf)
        try:
            self.cpd = get_cor_pair_dict(self.df, self.sdf)
            self.col_order = order_col_func(self.sdf, self.cpd)
        except Exception as e:
            print(e)
            self.col_order = self.df.columns
'''

def probable_datetime(ser):
    s_ser = ser.sample(np.min([len(ser), 500]))
    try:
        dt_ser = pd.to_datetime(s_ser)
        #pd.to_datetime(1_00_000_000_000_000_000) == pd.to_datetime('1973-01-01') 
        if dt_ser.max() < pd.to_datetime('1973-01-01'):
            return False
        return True
        
    except Exception as e:
        return False

def get_mode(ser):
    mode_raw = ser.mode()
    if len(mode_raw) == 0:
        return np.nan
    else:
        return mode_raw.values[0]



class TypingStats(ColAnalysis):
    provided_summary = [
        'dtype', 'is_numeric', 'is_integer', 'is_datetime',]

    @staticmethod
    def summary(sampled_ser, summary_ser, ser):
        return dict(
            dtype=ser.dtype,
            is_numeric=pd.api.types.is_numeric_dtype(ser),
            is_integer=pd.api.types.is_integer_dtype(ser),
            is_datetime=probable_datetime(ser),
            memory_usage=ser.memory_usage()
            )

class DefaultSummaryStats(ColAnalysis):
    provided_summary = [
        'length', 'min', 'max', 'mean', 'nan_count', 'distinct_count',
        'distinct_per', 'empty_count', 'empty_per', 'unique_per', 'nan_per',
        'mode']
    
    @staticmethod
    def summary(sampled_ser, summary_ser, ser):
        l = len(ser)
        val_counts = ser.value_counts()
        distinct_count= len(val_counts)
        nan_count = l - len(ser.dropna())
        unique_count = len(val_counts[val_counts==1])
        empty_count = val_counts.get('', 0)

        return dict(
            length=l,
            nan_count=nan_count,
            distinct_count=distinct_count,
            distinct_per=distinct_count/l,
            empty_count=empty_count,
            empty_per=empty_count/l,
            unique_per=unique_count/l,
            nan_per=nan_count/l,
            mode=get_mode(ser))


class DefaultSummaryStats(ColAnalysis):
    provided_summary = [
        'length', 'min', 'max', 'mean', 'nan_count', 'distinct_count',
        'distinct_per', 'empty_count', 'empty_per', 'unique_per', 'nan_per',
        'mode']
    
    @staticmethod
    def summary(sampled_ser, summary_ser, ser):


def int_digits(n):
    if n == 0:
        return 1
    if np.sign(n) == -1:
        return int(np.floor(np.log10(np.abs(n)))) + 2
    return int(np.floor(np.log10(n)+1))


def histogram(ser):
    raw_counts, bins = np.histogram(ser, 10)
    scaled_counts = np.round(raw_counts/raw_counts.sum(),2)
    return [scaled_counts, bins]

def table_sumarize_num_ser(ser):
    if len(ser) == 0:
        return dict(is_numeric=False)
    return dict(
        is_numeric=True,
        is_integer=pd.api.types.is_integer_dtype(ser),
        min_digits=int_digits(ser.min()),
        max_digits=int_digits(ser.max()),
        histogram=histogram(ser))


def summarize_numeric(ser):

    num_stats = summarize_string(ser)
    num_stats.update(dict(
        min=ser.min(),
        max=ser.max(),
        mean=ser.mean()))

    return num_stats

def summarize_column(ser):
    if pd.api.types.is_numeric_dtype(ser.dtype):
        return summarize_numeric(ser)
    else:
        return summarize_string(ser)



class DfStats(object):
    def __init__(self,
            df,
            annotate_funcs=[add_col_rankings],
            # summary_func=summary_stats.summarize_df,
            # order_col_func=summary_stats.order_columns):
            summary_func=summarize_df,
            order_col_func=order_columns):

        rows = len(df)
        cols = len(df.columns)
        item_count = rows * cols


        if item_count > FAST_SUMMARY_WHEN_GREATER:
            df = df.sample(np.min([50_000, len(df)]))
        self.df = df
        self.sdf = summary_func(df)
        for func in annotate_funcs:
            func(df, self.sdf)
        try:
            self.cpd = get_cor_pair_dict(self.df, self.sdf)
            self.col_order = order_col_func(self.sdf, self.cpd)
        except Exception as e:
            print(e)
            self.col_order = self.df.columns

        

