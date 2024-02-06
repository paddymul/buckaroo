import numpy as np
import polars as pl
from polars import functions as F
from buckaroo.pluggable_analysis_framework.polars_analysis_management import (
    PolarsAnalysis, polars_produce_series_df)
from buckaroo.pluggable_analysis_framework.utils import (json_postfix, replace_in_dict)
from buckaroo.polars_buckaroo import PolarsBuckarooWidget
from buckaroo.dataflow_traditional import StylingAnalysis

def test_basic_instantiation():
    PolarsBuckarooWidget(
        pl.DataFrame({'a':[1,2,3]}), )

def test_sdf_hints():
    pbw = PolarsBuckarooWidget(
        pl.DataFrame({'a':[1,2,3]}), debug=True)
    assert pbw.merged_sd['a']['type'] == 'integer'



EXPECTED_DF_VIEWER_CONFIG = {
    'pinned_rows': [],
    'column_config': [
        {'col_name': 'index', 'displayer_args': {'displayer': 'obj'}},
        {'col_name': 'normal_int_series', 'displayer_args': {'displayer': 'obj'}}]}
                             
class SelectOnlyAnalysis(PolarsAnalysis):

    select_clauses = [
        F.all().null_count().name.map(json_postfix('null_count')),
        F.all().mean().name.map(json_postfix('mean')),
        F.all().quantile(.99).name.map(json_postfix('quin99'))]

test_df = pl.DataFrame({
        'normal_int_series' : pl.Series([1,2,3,4]),
})



def test_polars_all_stats():
    """the all_stats verify that PolarsBuckarooWidget produces the
    same summary_stats shape tatha pandas does.

    Since polars doesn't have an index concept, some things are a little different, but the summary_stats display essentiall depends on the index being present and displayed

    """
    
    sdf, errs = polars_produce_series_df(
        test_df, [SelectOnlyAnalysis], 'test_df', debug=True)
    expected = {
        #'float_nan_ser':      {'mean': None, 'null_count':  0, 'quin99': None},
        'normal_int_series':  {'mean': 2.5,  'null_count':  0, 'quin99':  4.0}}
    dsdf = replace_in_dict(sdf, [(np.nan, None)])
    class SimplePolarsBuckaroo(PolarsBuckarooWidget):
        analysis_klasses= [SelectOnlyAnalysis, StylingAnalysis]

    spbw = SimplePolarsBuckaroo(test_df)
    assert spbw.merged_sd == {
        'normal_int_series':  {'mean': 2.5,  'null_count':  0, 'quin99':  4.0}}
    assert spbw.df_data_dict['all_stats'] == [
        {'index': 'mean', 'normal_int_series': 2.5},
        {'index': 'null_count', 'normal_int_series': 0.0},
        {'index': 'quin99', 'normal_int_series': 4.0}]
    assert spbw.df_display_args['main']['df_viewer_config'] == EXPECTED_DF_VIEWER_CONFIG

def test_pandas_all_stats():
    """just make sure this doesn't fail"""
    from buckaroo.buckaroo_widget import BuckarooWidget
    from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)
    import pandas as pd

    pd_test_df = pd.DataFrame({
        'normal_int_series' : pl.Series([1,2,3,4]),
        #'empty_na_ser' : pl.Series([pl.Null] * 4, dtype="Int64"),
        #'float_nan_ser' : pl.Series([3.5, np.nan, 4.8, 2.2])
    })

    
    class SimpleAnalysis(ColAnalysis):
        requires_raw = True
        provides_series_stats = ["distinct_count"]

        @staticmethod
        def series_summary(sampled_ser, raw_ser):
            return dict(
                null_count=0,
                mean=2.5,
                quin99=4.0)

    class SimpleBuckaroo(BuckarooWidget):
        analysis_klasses= [SimpleAnalysis, StylingAnalysis]

    sbw = SimpleBuckaroo(pd_test_df)
    assert sbw.merged_sd == {
        'index': {'mean': 2.5, 'null_count': 0, 'quin99': 4.0},
        'normal_int_series':  {'mean': 2.5,  'null_count':  0, 'quin99':  4.0}}
    assert sbw.df_display_args['main']['df_viewer_config'] == EXPECTED_DF_VIEWER_CONFIG

def Xtest_object_dtype1():

    ser = pl.Series([{'a':5}])
    df = pl.DataFrame({'nested_dicts2': ser})
    PolarsBuckarooWidget(df)

def Xtest_object_dtype2():

    ser = pl.Series([{'a':5}], dtype=pl.Object)
    df = pl.DataFrame({'nested_dicts2': ser})
    PolarsBuckarooWidget(df)


    # I eventually wanted to test non regular object like this
    # ser = pl.Series([
    #         {'level_1': {'a':10}}, None], dtype=pl.Object)
    # df = pl.DataFrame({'nested_dicts2': ser})

'''
FIXME:test a large dataframe that forces sampling
'''
