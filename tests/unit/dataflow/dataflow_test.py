import pandas as pd
from buckaroo.dataflow_traditional import DataFlow
from buckaroo import dataflow_traditional as dft
from .fixtures import (DistinctCount)
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
    dfc = CustomizableDataflow(BASIC_DF)
    assert dfc.widget_args_tuple[0] is BASIC_DF


    assert dfc.df_data_dict['main'] == BASIC_DF_JSON_DATA
    assert dfc.df_display_args['main']['df_viewer_config'] == DFVIEWER_CONFIG_DEFAULT

def test_custom_dataflow():

    class IntStyling(StylingAnalysis):
        @staticmethod
        def style_column(col, sd):
            return {'col_name':col, 'displayer_args': {'displayer': 'int'}}

        df_display_name = "int_styles"
        data_key = "main"
        summary_stats_key= '555555555'


    class TwoStyleDFC(CustomizableDataflow):
        analysis_klasses = [StylingAnalysis, IntStyling]
        #analysis_klasses = [IntStyling]
        
    cdfc = TwoStyleDFC(BASIC_DF)
    assert cdfc.widget_args_tuple[0] is BASIC_DF
    assert cdfc.df_display_args['main']['df_viewer_config'] == DFVIEWER_CONFIG_DEFAULT
    DFVIEWER_CONFIG_INT = {
                   'pinned_rows': [],
                   'column_config':  [
                       {'col_name':'index', 'displayer_args': {'displayer': 'int'}},
                       {'col_name':'a', 'displayer_args': {'displayer': 'int'}},
                       {'col_name':'b', 'displayer_args': {'displayer': 'int'}}]}
    
    assert cdfc.df_display_args['int_styles']['df_viewer_config'] == DFVIEWER_CONFIG_INT



def test_custom_summary_stats():
    class DCDFC(CustomizableDataflow):
        analysis_klasses = [DistinctCount, StylingAnalysis]

    dc_dfc = DCDFC(BASIC_DF)

    summary_sd = dc_dfc.widget_args_tuple[1]

    assert summary_sd == {'index': {'distinct_count': 3}, 
                          'a': {'distinct_count':2}, 'b': {'distinct_count':3}}
    assert list(summary_sd.keys()) == ['index', 'a', 'b']

SENTINEL_DF = pd.DataFrame({'sent_int_col':[11, 22, 33], 'sent_str_col':['ka', 'b', 'c']})


class PostProcessingAnalysis(ColAnalysis):

    post_processing_method = "post1"

    @classmethod
    def post_process_df(kls, cleaned_df):
        return [SENTINEL_DF, {'sent_int_col': {'sentinel_prop':5}}]


def test_custom_post_processing():
    class PostDCFC(CustomizableDataflow):
        analysis_klasses = [PostProcessingAnalysis, StylingAnalysis]

    p_dfc = PostDCFC(BASIC_DF)

    assert p_dfc.buckaroo_options['post_processing'] == ['', 'post1']
    assert p_dfc.buckaroo_state['post_processing'] == ''

    temp_buckaroo_state = p_dfc.buckaroo_state.copy()
    temp_buckaroo_state['post_processing'] = 'post1'
    p_dfc.buckaroo_state = temp_buckaroo_state

    assert p_dfc.processed_df is SENTINEL_DF

class AlwaysFailPostProcessingAnalysis(ColAnalysis):

    post_processing_method = "always_fail"

    @classmethod
    def post_process_df(kls, cleaned_df):
        1/0


def test_error_post_processing():
    class ErrorCFC(CustomizableDataflow):
        analysis_klasses = [AlwaysFailPostProcessingAnalysis, StylingAnalysis]

    e_dfc = ErrorCFC(BASIC_DF)

    # assert e_dfc.buckaroo_options['post_processing'] == ['', 'post1']
    # assert e_dfc.buckaroo_state['post_processing'] == ''

    assert e_dfc.buckaroo_options['post_processing'] == ['', 'always_fail']
    assert e_dfc.buckaroo_state['post_processing'] == ''

    temp_buckaroo_state = e_dfc.buckaroo_state.copy()
    temp_buckaroo_state['post_processing'] = 'always_fail'
    e_dfc.buckaroo_state = temp_buckaroo_state
    assert e_dfc.processed_df.values == [["division by zero"]]

def test_column_config_override_widget():
    ROWS = 200
    typed_df = pd.DataFrame(
        {'int_col': [1] * ROWS,
         'float_col': [.5] * ROWS,
         "str_col": ["foobar"]* ROWS})
    bw2 = BuckarooWidget(
        typed_df, 
        column_config_overrides={
            'float_col':
            {'displayer_args': { 'displayer': 'integer', 'min_digits': 3, 'max_digits': 5 }}})
    float_col_config = bw2.df_display_args['main']['df_viewer_config']['column_config'][2]
    assert float_col_config == {'col_name': 'float_col', 'displayer_args': { 'displayer': 'integer', 'min_digits': 3, 'max_digits': 5 }}
    


def test_pinned_rows_override_widget():
    ROWS = 200
    typed_df = pd.DataFrame(
        {'int_col': [1] * ROWS,
         'float_col': [.5] * ROWS,
         "str_col": ["foobar"]* ROWS})
    HIST_ROW = {'primary_key_val': 'histogram', 'displayer_args': { 'displayer': 'histogram' }}
    bw2 = BuckarooWidget(typed_df, pinned_rows=[HIST_ROW])
    pinned_rows = bw2.df_display_args['main']['df_viewer_config']['pinned_rows']
    assert pinned_rows[0] == HIST_ROW

    

class TransposeProcessing(ColAnalysis):
    @classmethod
    def post_process_df(kls, df):
        return [df.T, {}]
    post_processing_method = "transpose"


def test_transpose_error():
    ROWS = 5
    typed_df = pd.DataFrame(
        {'int_col': [1] * ROWS,
         'float_col': [.5] * ROWS,
         "str_col": ["foobar"]* ROWS})

    base_a_klasses = BuckarooWidget.analysis_klasses.copy()
    base_a_klasses.extend([TransposeProcessing])

    class VCBuckarooWidget(BuckarooWidget):
        analysis_klasses = base_a_klasses

    vcb = VCBuckarooWidget(typed_df, debug=False)
    temp_buckaroo_state = vcb.buckaroo_state.copy()
    temp_buckaroo_state['post_processing'] = 'transpose'
    vcb.buckaroo_state = temp_buckaroo_state
    assert vcb.processed_df.values.tolist() == [
        [1, 1, 1, 1, 1],
        [0.5, 0.5, 0.5, 0.5, 0.5],
        ['foobar', 'foobar', 'foobar', 'foobar', 'foobar']]
