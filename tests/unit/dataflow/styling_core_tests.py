from typing import List
import pandas as pd
from buckaroo.dataflow.styling_core import ColumnConfig, DFViewerConfig, StylingAnalysis
from buckaroo.ddd_library import get_basic_df2, get_multi_index_cols_df, get_tuple_cols_df
from buckaroo.pluggable_analysis_framework.col_analysis import SDType
BASIC_DF = get_basic_df2()

def test_simple_styling() -> None:
    simple_df: pd.DataFrame = pd.DataFrame({
        'foo':[10, 20, 30],
        'bar':['foo', 'bar', 'baz']})

    dfvc: DFViewerConfig = StylingAnalysis.get_dfviewer_config(
    {'a':{'orig_col_name':'foo'}, 'b':{'orig_col_name':'bar'}}, simple_df)

    col_config: List[ColumnConfig] = dfvc['column_config']
    assert len(col_config) == 2
    assert col_config[0]['col_name'] == 'a'
    assert col_config[0]['header_name'] == 'foo'
    assert col_config[1]['col_name'] == 'b'
    assert col_config[1]['header_name'] == 'bar'

def test_multi_index_styling() -> None:

    mic_df: pd.DataFrame = get_multi_index_cols_df()
    fake_sd:SDType = {
        "a": {'orig_col_name':('foo','a')},
        "b": {'orig_col_name':('foo','b')},
        "c": {'orig_col_name':('bar','a')},
    }

    dfvc: DFViewerConfig = StylingAnalysis.get_dfviewer_config(fake_sd, mic_df)

    col_config: List[ColumnConfig] = dfvc['column_config']
    assert len(col_config) == 3
    #assert col_config[0]['col_path'] == ('index', '')
    assert col_config[0]['col_path'] == ('foo', 'a')
    assert col_config[1]['col_path'] == ('foo', 'b')

    assert col_config[2]['col_path'] == ('bar', 'a')

def test_tuple_col_styling() -> None:

    mic_df: pd.DataFrame = get_tuple_cols_df()
    fake_sd:SDType = {
        "a": {'orig_col_name':('foo','a')},
        "b": {'orig_col_name':('foo','b')},
        "c": {'orig_col_name':('bar','a')},
    }

    dfvc: DFViewerConfig = StylingAnalysis.get_dfviewer_config(fake_sd, mic_df)

    col_config: List[ColumnConfig] = dfvc['column_config']
    assert len(col_config) == 3
    #assert col_config[0]['col_name'] == "('index', '')"
    print(col_config[0])
    #assert col_config[0]['col_path'] == ('index', '')
    assert col_config[0]['col_path'] == ('foo', 'a')
    assert col_config[1]['col_path'] == ('foo', 'b')
    assert col_config[2]['col_path'] == ('bar', 'a')

def test_get_dfviewer_config_merge_hidden():
    sd: SDType = {'a':
        {'orig_col_name': 'sent_int_col', 'rewritten_col_name': 'a'},
        'b':
        {'orig_col_name': 'sent_str_col', 'rewritten_col_name': 'b'},
        'sent_int_col':
        {'merge_rule': 'hidden'}}

    expected_output: DFViewerConfig = {
        'pinned_rows': [],
        'column_config':  [
            {'col_name': 'b', 'header_name':'sent_str_col', 'displayer_args': {'displayer': 'obj'}},
        ],
        'first_col_config': {'col_name': 'index', 'header_name':'index',
                             'displayer_args': {'displayer': 'obj'}},
        'component_config': {},
        'extra_grid_config': {},
    }

    actual = StylingAnalysis.get_dfviewer_config(sd, BASIC_DF)
    assert expected_output == actual
