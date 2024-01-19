import pandas as pd
#from buckaroo.dataflow import DataFlow
from buckaroo.dataflow_traditional import DataFlow
from buckaroo import dataflow_traditional as dft


simple_df = pd.DataFrame({'int_col':[1, 2, 3], 'str_col':['a', 'b', 'c']})



def test_dataflow_operating_df():
    d_flow = DataFlow(simple_df)

    # assert d_flow.sampled_df is not simple_df
    d_flow.raw_df = simple_df
    print("operating_df", d_flow.sampled_df)
    assert d_flow.sampled_df is simple_df

    d_flow.sample_method = "first"
    assert len(d_flow.sampled_df) == 1
    
    d_flow.sample_method = "default"
    assert d_flow.sampled_df is simple_df

    
def test_dataflow_cleaned():

    d_flow = DataFlow(simple_df)
    #these two should be None to start
    # assert d_flow.cleaned_df is None
    # assert d_flow.cleaned_sd == {}
    # d_flow.raw_df = simple_df
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

    assert d_flow.summary_sd == {}
    d_flow.analysis_klasses = "foo"
    d_flow.cleaning_method = "one op"
    assert d_flow.summary_sd == {'foo':8}

def test_merged_sd():
    d_flow = DataFlow(simple_df)
    assert d_flow.merged_sd == {}
    d_flow.analysis_klasses = "foo"
    d_flow.cleaning_method = "one op"
    assert d_flow.summary_sd == {'foo':8}
    assert d_flow.merged_sd == {'foo':8}

def test_widget():
    d_flow = DataFlow(simple_df)
    assert d_flow.merged_sd == {}
    d_flow.analysis_klasses = "foo"
    d_flow.cleaning_method = "one op"
    assert d_flow.summary_sd == {'foo':8}
    assert d_flow.merged_sd == {'foo':8}

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
	    'column_config_override': { 'displayer': 'string'}},
        'only_in_base': {'f':77},
        'completely_new_column': {'k':90}}

    result = dft.merge_sds(sd_base, sd_second)
    assert result == expected
