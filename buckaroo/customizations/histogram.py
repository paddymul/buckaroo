import pandas as pd
import numpy as np
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import ColAnalysis


def numeric_histogram_labels(endpoints):
    left = endpoints[0]
    labels = []
    for edge in endpoints[1:]:
        labels.append("{:.0f}-{:.0f}".format(left, edge))
        left = edge
    return labels
#histogram_labels(endpoints)

def categorical_dict(len_, val_counts, top_n_positions=7):
    top = min(len(val_counts), top_n_positions)
    top_vals = val_counts.iloc[:top]
        
    rest_vals = val_counts.iloc[top:]
    try:
        histogram = top_vals.to_dict()
    except TypeError:
        top_vals.index = top_vals.index.map(str)
        histogram = top_vals.to_dict()

    full_long_tail = rest_vals.sum()
    unique_count = sum(val_counts == 1)
    long_tail = full_long_tail - unique_count
    if unique_count > 0:
        histogram['unique'] = np.round( (unique_count/len_)* 100, 0)
    if long_tail > 0:
        histogram['longtail'] = np.round((long_tail/len_) * 100,0)
    return histogram    

def categorical_histogram(length, val_counts, nan_per, top_n_positions=7):
    nan_observation = {'name':'NA', 'NA':np.round(nan_per*100, 0)}
    cd = categorical_dict(length, val_counts, top_n_positions)
    
    histogram = []
    longtail_obs = {'name': 'longtail'}
    for k,v in cd.items():
        if k in ["longtail", "unique"]:
            longtail_obs[k] = v
            continue
        histogram.append({'name':k, 'cat_pop': np.round((v/length)*100,0) })
    if len(longtail_obs) > 1:
        histogram.append(longtail_obs)
    if nan_per > 0.0:
        histogram.append(nan_observation)
    return histogram

def numeric_histogram(histogram_args, min_, max_, nan_per):

    low_tail, high_tail = histogram_args['low_tail'], histogram_args['high_tail']
    ret_histo = []
    nan_observation = {'name':'NA', 'NA':np.round(nan_per*100, 0)}
    if nan_per == 1.0:
        return [nan_observation]
    
    populations, endpoints = histogram_args['meat_histogram']
    
    labels = numeric_histogram_labels(endpoints)
    normalized_pop = populations / populations.sum()
    low_label = "%r - %r" % (min_, low_tail)

    ret_histo.append({'name': low_label, 'tail':1})
    for label, pop in zip(labels, normalized_pop):
        ret_histo.append({'name': label, 'population':np.round(pop * 100, 0)})
    high_label = "%r - %r" % (high_tail, max_)
    ret_histo.append({'name': high_label, 'tail':1})
    if nan_per > 0.0:
        ret_histo.append(nan_observation)
    return ret_histo



def histogram(histogram_args, length, value_counts, min_, max_, is_numeric, nan_per):
    if is_numeric and len(value_counts)>5:
        temp_histo =  numeric_histogram(
            histogram_args,
            min_, max_, nan_per)
        if len(temp_histo) > 5:
            #if we had basically a categorical variable encoded into an integer.. don't return it
            return temp_histo
    return categorical_histogram(length, value_counts, nan_per)


class Histogram(ColAnalysis):

    @staticmethod
    def series_summary(sampled_ser, ser):
        if not pd.api.types.is_numeric_dtype(ser):
            return dict(histogram_args={})
        if pd.api.types.is_bool_dtype(ser):
            return dict(histogram_args={})
        vals = ser.dropna()
        low_tail = np.quantile(ser, 0.01)
        high_tail =  np.quantile(ser, 0.99)
        low_pass  = ser > low_tail 
        high_pass = ser < high_tail
        meat = vals[low_pass & high_pass]

        return dict(
            histogram_args=dict(
                meat_histogram=np.histogram(meat, 10),
                low_tail=low_tail,
                hight_tail=high_tail))


    requires_summary = ['value_counts', 'nan_per', 'is_numeric', 'length',
                        'min', 'max',
                        ]
    provides_summary = ['histogram', 'histogram_args']

    @staticmethod
    def computed_summary(summary_dict):
        return dict(
            histogram=histogram(
                summary_dict['histogram_args'],
                summary_dict['length'],
                summary_dict['value_counts'],
                summary_dict['min'], summary_dict['max'],
                summary_dict['is_numeric'], summary_dict['nan_per']))
    provides_summary = [
        'dtype', 'is_numeric', 'is_integer', 'is_datetime',]