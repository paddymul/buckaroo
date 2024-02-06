import pandas as pd
from buckaroo.dataflow_traditional import DataFlow
from buckaroo import dataflow_traditional as dft
from ..fixtures import (DistinctCount)
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)
from buckaroo.dataflow_traditional import CustomizableDataflow, StylingAnalysis
from buckaroo.buckaroo_widget import BuckarooWidget

simple_df = pd.DataFrame({'int_col':[1, 2, 3], 'str_col':['a', 'b', 'c']})


def test_dataflow_operating_df():
    d_flow = DataFlow(simple_df)
    d_flow.raw_df = simple_df
    assert d_flow.sampled_df is simple_df
    d_flow.sample_method = "first"
    assert len(d_flow.sampled_df) == 1
    d_flow.sample_method = "default"
    assert d_flow.sampled_df is simple_df

    
def test_dataflow_cleaned():
    d_flow = DataFlow(simple_df)
    assert d_flow.cleaned_df is simple_df
    d_flow.existing_operations = ["one"]
    assert d_flow.cleaned_df is dft.SENTINEL_DF_1
    d_flow.cleaning_method = "one op"
    assert d_flow.cleaned_df is dft.SENTINEL_DF_2

def test_dataflow_processed():

    d_flow = DataFlow(simple_df)
    assert d_flow.processed_df is simple_df
    #processed is currently a no-op, so I'm skipping actual tests for now

def test_summary_sd():
    d_flow = DataFlow(simple_df)
    assert d_flow.summary_sd == {'index': {}, 'int_col': {}, 'str_col': {}}
    d_flow.analysis_klasses = "foo"
    d_flow.cleaning_method = "one op"
    assert d_flow.summary_sd == {'some-col': {'foo':8}}

def test_merged_sd():
    d_flow = DataFlow(simple_df)
    assert d_flow.merged_sd == {'index': {}, 'int_col': {}, 'str_col': {}}
    d_flow.analysis_klasses = "foo"
    d_flow.cleaning_method = "one op"
    assert d_flow.summary_sd == {'some-col': {'foo':8}}
    assert d_flow.merged_sd == {'some-col': {'foo':8}}


def test_column_config():
    basic_df = pd.DataFrame({'a': [10, 20, 30], 'b':['foo', 'bar', 'baz']})
    d_flow = DataFlow(basic_df)
    df, merged_sd = d_flow.widget_args_tuple

    #dfviewer_config = d_flow.df_display_args['main']
    assert merged_sd == {'index' : {}, 'a': {}, 'b': {}}
    
def test_merge_sds():

    sd_base = {
        'Volume' : {
            'a':10,
	    'column_config_override': {
                'color_map_config' : {'color_rule': 'color_from_column',
	                              'col_name': 'Volume_colors'}}},
        'Volume_colors' : {
            'a': 30,
	    'column_config_override': { 'displayer': 'hidden'}},
        'only_in_base': {'f':77}}

    sd_second = {
        'Volume' : {
            'a': 999,
            'b': "foo",
	    'column_config_override': {
                'tooltip_config': {'tooltip_type' : 'summary_series'}}},
        'Volume_colors' : {
            'd':111,
	    'column_config_override': { 'displayer': 'string'}},
        'completely_new_column': {'k':90}}

    expected = {
        'Volume' : {
            'a': 999,
            'b': "foo",
	    'column_config_override': {
                'color_map_config' : {'color_rule': 'color_from_column',
	                              'col_name': 'Volume_colors'},
                #note that column_config_override is merged, not just overwritten
                'tooltip_config': {'tooltip_type' : 'summary_series'}}},
        'Volume_colors' : {
            'a': 30,
            'd': 111,
            #sd_second has a different value for 'displayer then sd_base
	    'column_config_override': { 'displayer': 'string'}},
        #only in base, needs to be present
        'only_in_base': {'f':77},
        #only found in second should show up here
        'completely_new_column': {'k':90}}

    result = dft.merge_sds(sd_base, sd_second)
    
    assert result == expected
    

def test_merge_column_config():
    overrides = {
        'bar' : {'displayer_args':  {'displayer': 'int'}},
        'foo' : {'color_map_config' : {'color_rule': 'color_from_column',
	                               'col_name': 'Volume_colors'}}}

    computed_column_config =     [
            {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'foo', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'bar', 'displayer_args': {'displayer': 'obj'}}]

    merged = dft.merge_column_config(
        computed_column_config, overrides)

    expected = [
            {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'foo', 'displayer_args': {'displayer': 'obj'},
             'color_map_config' : {'color_rule': 'color_from_column',
	                               'col_name': 'Volume_colors'}},
            {'col_name':'bar', 'displayer_args': {'displayer': 'int'}}]
    assert expected == merged
        

def test_merge_column_config_hide():
    overrides = {
        'bar' : {'merge_rule':'hidden'}}
    computed_column_config =     [

            {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'foo', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'bar', 'displayer_args': {'displayer': 'obj'}}]

    merged = dft.merge_column_config(
        computed_column_config, overrides)

    expected = [
            {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'foo',   'displayer_args': {'displayer': 'obj'}}]
        
    assert expected == merged
        
