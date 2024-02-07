from buckaroo.dataflow_traditional import StylingAnalysis
from buckaroo.pluggable_analysis_framework.polars_analysis_management import (PolarsAnalysis)
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)
from buckaroo.polars_buckaroo import PolarsBuckarooWidget
import polars as pl 

simple_df = pl.DataFrame({'int_col':[1, 2, 3], 'str_col':['a', 'b', 'c']})
BASIC_DF_JSON_DATA = [{'index':0, 'a':10, 'b':'foo'},
                        {'index':1, 'a':20, 'b':'bar'},
                        {'index':2, 'a':20, 'b':'baz'}]

BASIC_DF = pl.DataFrame({'a': [10, 20, 20], 'b':['foo', 'bar', 'baz']})


DFVIEWER_CONFIG_DEFAULT = {
                   'pinned_rows': [],
                   'column_config':  [
                       {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
                       {'col_name':'a', 'displayer_args': {'displayer': 'obj'}},
                       {'col_name':'b', 'displayer_args': {'displayer': 'obj'}}]}


class BasicStyling(StylingAnalysis):
    df_display_name = "basic"
    

def test_widget_instatiation():
    dfc = PolarsBuckarooWidget(BASIC_DF)
    #the BasicStyling is simple and predictable, it writes to 'basic' which nothing else should
    dfc.add_analysis(BasicStyling)

    assert dfc.widget_args_tuple[1] is BASIC_DF
    assert dfc.df_data_dict['main'] == BASIC_DF_JSON_DATA

    actual_column_config = dfc.df_display_args['basic']['df_viewer_config']['column_config']
    expected_column_config = DFVIEWER_CONFIG_DEFAULT['column_config']

    #this test is brittle because styling is rapidly changing in development
    assert actual_column_config == expected_column_config 

def test_custom_dataflow():
    """Tests that a styling method can be added BuckarooWidget and
    that it properly modifies column_config. This Styling analysis
    should be identical between polars and pandas

    """
    class IntStyling(StylingAnalysis):
        @staticmethod
        def style_column(col, sd):
            return {'col_name':col, 'displayer_args': {'displayer': 'int'}}

        df_display_name = "int_styles"
        data_key = "main"
        summary_stats_key= '555555555'


    class TwoStyleDFC(PolarsBuckarooWidget):
        analysis_klasses = [StylingAnalysis, IntStyling]
        #analysis_klasses = [IntStyling]
        
    cdfc = TwoStyleDFC(BASIC_DF)
    assert cdfc.widget_args_tuple[1] is BASIC_DF
    assert cdfc.df_display_args['main']['df_viewer_config'] == DFVIEWER_CONFIG_DEFAULT
    DFVIEWER_CONFIG_INT = {
                   'pinned_rows': [],
                   'column_config':  [
                       {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
                       {'col_name':'a', 'displayer_args': {'displayer': 'int'}},
                       {'col_name':'b', 'displayer_args': {'displayer': 'int'}}]}
    
    assert cdfc.df_display_args['int_styles']['df_viewer_config'] == DFVIEWER_CONFIG_INT


SENTINEL_DF = pl.DataFrame({'sent_int_col':[11, 22, 33], 'sent_str_col':['ka', 'b', 'c']})


class PostProcessingAnalysis(ColAnalysis):

    post_processing_method = "post1"

    @classmethod
    def post_process_df(kls, cleaned_df):
        return [SENTINEL_DF, {'sent_int_col': {'sentinel_prop':5}}]


def test_custom_post_processing():
    """This test demonstrates that a post processing method can be
    added to BuckarooWidget through an analysis class. It further
    checks that BuckarooWidget responds to changes in buckaroo_state
    that activate the actual post_processing function

    """
    class PostDCFC(PolarsBuckarooWidget):
        analysis_klasses = [PostProcessingAnalysis, StylingAnalysis]

    p_dfc = PostDCFC(BASIC_DF)

    assert p_dfc.buckaroo_options['post_processing'] == ['', 'post1']
    assert p_dfc.buckaroo_state['post_processing'] == ''

    temp_buckaroo_state = p_dfc.buckaroo_state.copy()
    temp_buckaroo_state['post_processing'] = 'post1'
    p_dfc.buckaroo_state = temp_buckaroo_state

    assert p_dfc.processed_df is SENTINEL_DF


class TransposeProcessing(ColAnalysis):
    @classmethod
    def post_process_df(kls, df):
        return [df.transpose(), {}]
    post_processing_method = "transpose"


def test_transpose_error():
    ROWS = 5
    typed_df = pl.DataFrame(
        {'int_col': [1] * ROWS,
         'float_col': [.5] * ROWS,
         "str_col": ["foobar"]* ROWS})

    base_a_klasses = PolarsBuckarooWidget.analysis_klasses.copy()
    base_a_klasses.extend([TransposeProcessing])

    class VCBuckarooWidget(PolarsBuckarooWidget):
        analysis_klasses = base_a_klasses

    vcb = VCBuckarooWidget(typed_df, debug=False)
    assert type(vcb.processed_df) == pl.DataFrame
    assert vcb.processed_df.to_numpy().tolist() ==[
        [1, 0.5, 'foobar'],
        [1, 0.5, 'foobar'],
        [1, 0.5, 'foobar'],
        [1, 0.5, 'foobar'],
        [1, 0.5, 'foobar']]

    temp_buckaroo_state = vcb.buckaroo_state.copy()
    temp_buckaroo_state['post_processing'] = 'transpose'
    vcb.buckaroo_state = temp_buckaroo_state
    assert type(vcb.processed_df) == pl.DataFrame
    #note that Polars doesn'transpose to objects, but to strings instead
    assert vcb.processed_df.to_numpy().tolist() == [
        ['1', '1', '1', '1', '1'],
        ['0.5', '0.5', '0.5', '0.5', '0.5'],
        ['foobar', 'foobar', 'foobar', 'foobar', 'foobar']]


class ShowErrorsPostProcessing(ColAnalysis):
    @classmethod
    def post_process_df(kls, df):
        print("^"*80)
        print(type(df))
        result_df = df.select(
            F.all(),
            #pl.col('float_col').lt(5).replace(True, "foo").replace(False, None).alias('errored_float')
        )
        #return [result_df, {}]
        return [df, {}]

    post_processing_method = "show_errors"

def test_other_post_processing():
    ROWS = 5
    typed_df = pl.DataFrame(
        {'int_col': [1] * ROWS,
         'float_col': [.5] * ROWS,
         "str_col": ["foobar"]* ROWS})
    bw = PolarsBuckarooWidget(typed_df, debug=False)

    bw.add_analysis(ShowErrorsPostProcessing)

    temp_buckaroo_state = bw.buckaroo_state.copy()
    temp_buckaroo_state['post_processing'] = 'show_errors'
    bw.buckaroo_state = temp_buckaroo_state
    print(bw.processed_df)
    1/0

    
class TransposeProcessing2(ColAnalysis):
    @classmethod
    def post_process_df(kls, df):
        return [df.transpose(), {}]
    post_processing_method = "transpose2"


def test_transpose_error2():
    ROWS = 5
    typed_df = pl.DataFrame(
        {'int_col': [1] * ROWS,
         'float_col': [.5] * ROWS,
         "str_col": ["foobar"]* ROWS})

    base_a_klasses = PolarsBuckarooWidget.analysis_klasses.copy()
    base_a_klasses.extend([TransposeProcessing2])

    class VCBuckarooWidget2(PolarsBuckarooWidget):
        analysis_klasses = base_a_klasses

    vcb = VCBuckarooWidget2(typed_df, debug=False)
    assert type(vcb.processed_df) == pl.DataFrame
    assert vcb.processed_df.to_numpy().tolist() ==[
        [1, 0.5, 'foobar'],
        [1, 0.5, 'foobar'],
        [1, 0.5, 'foobar'],
        [1, 0.5, 'foobar'],
        [1, 0.5, 'foobar']]

    temp_buckaroo_state = vcb.buckaroo_state.copy()
    temp_buckaroo_state['post_processing'] = 'transpose2'
    vcb.buckaroo_state = temp_buckaroo_state
    assert type(vcb.processed_df) == pl.DataFrame
    #note that Polars doesn'transpose to objects, but to strings instead
    assert vcb.processed_df.to_numpy().tolist() == [
        ['1', '1', '1', '1', '1'],
        ['0.5', '0.5', '0.5', '0.5', '0.5'],
        ['foobar', 'foobar', 'foobar', 'foobar', 'foobar']]
