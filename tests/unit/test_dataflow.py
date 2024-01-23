import pytest
import pandas as pd
#from buckaroo.dataflow import DataFlow
from buckaroo.dataflow_traditional import DataFlow
from buckaroo import dataflow_traditional as dft


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
    df, merged_sd, dfviewer_config = d_flow.widget_args_tuple

    assert merged_sd == {'index' : {}, 'a': {}, 'b': {}}
    assert dfviewer_config['pinned_rows'] == []
    assert dfviewer_config['column_config'] == [
            {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'a', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'b', 'displayer_args': {'displayer': 'obj'}}]
    
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
        
         
from buckaroo.buckaroo_widget import BuckarooWidget
EMPTY_DF_JSON = {
            'dfviewer_config': {
                'pinned_rows': [],
                'column_config': []},
            'data': []}

BASIC_DF = pd.DataFrame({'a': [10, 20, 20], 'b':['foo', 'bar', 'baz']})
BASIC_DF_JSON_DATA = [{'index':0, 'a':10, 'b':'foo'},
                        {'index':1, 'a':20, 'b':'bar'},
                        {'index':2, 'a':20, 'b':'baz'}]
DFVIEWER_CONFIG_DEFAULT = {
                   'pinned_rows': [],
                   'column_config':  [
                       {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
                       {'col_name':'a', 'displayer_args': {'displayer': 'obj'}},
                       {'col_name':'b', 'displayer_args': {'displayer': 'obj'}}]}

def test_widget_instatiation():
    dfc = DataFlow(BASIC_DF)
    assert dfc.widget_args_tuple[0] is BASIC_DF

    main_df = {'data': BASIC_DF_JSON_DATA,
               'dfviewer_config': DFVIEWER_CONFIG_DEFAULT}

    expected_df_dict =  {
        'main': main_df,
        'all': EMPTY_DF_JSON}

    assert dfc.df_dict == expected_df_dict
    bw = BuckarooWidget(BASIC_DF)
    assert bw.df_dict == expected_df_dict

from buckaroo.dataflow_traditional import CustomizableDataflow, SimpleStylingAnalysis

def test_custom_dataflow():

    class IntStyling(SimpleStylingAnalysis):
        @staticmethod
        def sd_to_column_config(col, sd):
            return {'col_name':col, 'displayer_args': {'displayer': 'int'}}

        style_method = "int_styles"


    class TwoStyleDFC(CustomizableDataflow):
        analysis_klasses = [SimpleStylingAnalysis, IntStyling]
        
    cdfc = TwoStyleDFC(BASIC_DF)
    assert cdfc.widget_args_tuple[0] is BASIC_DF
    #assert cdfc.df_dict['main']['dfviewer_config'] == DFVIEWER_CONFIG_DEFAULT

    DFVIEWER_CONFIG_INT = {
                   'pinned_rows': [],
                   'column_config':  [
                       {'col_name':'index', 'displayer_args': {'displayer': 'int'}},
                       {'col_name':'a', 'displayer_args': {'displayer': 'int'}},
                       {'col_name':'b', 'displayer_args': {'displayer': 'int'}}]}

    cdfc.style_method = "int_styles"
    assert cdfc.df_dict['main']['dfviewer_config'] == DFVIEWER_CONFIG_INT


    with pytest.raises(dft.UnknownStyleMethod):
        cdfc.style_method = "non_existent_styling"

from .fixtures import (DistinctCount, Len, DistinctPer, DCLen, DependsNoProvides)

def test_custom_summary_stats():
    class DCDFC(CustomizableDataflow):
        analysis_klasses = [DistinctCount, SimpleStylingAnalysis]

    dc_dfc = DCDFC(BASIC_DF)

    summary_sd = dc_dfc.widget_args_tuple[1]

    assert summary_sd == {'index': {'distinct_count': 3}, 
                          'a': {'distinct_count':2}, 'b': {'distinct_count':3}}
    assert list(summary_sd.keys()) == ['index', 'a', 'b']

