from typing import List
import pandas as pd
from buckaroo.dataflow.styling_core import ColumnConfig, DFViewerConfig, NormalColumnConfig, StylingAnalysis, rewrite_override_col_references
from buckaroo.ddd_library import get_basic_df2, get_multi_index_cols_df, get_tuple_cols_df
from buckaroo.pluggable_analysis_framework.col_analysis import SDType
from tests.unit.test_utils import assert_dict_eq
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

def test_get_dfviewer_column_config_override():
    """
      This test the case where some analysis puts a 'column_config_override' key into the sddict.

      I'm pretty sure that BuckarooWidget(... column_config_overrides=...)
      goes through a different codepath
      """
    sd: SDType = {
    'a': {'orig_col_name': 'sent_int_col', 'rewritten_col_name': 'a'},
    'b': {'orig_col_name': 'sent_str_col', 'rewritten_col_name': 'b',
          'column_config_override' : {
              'color_map_config': {'color_rule': 'color_from_column', 'val_column': 'Volume_colors'}}}
    }

    b_config : NormalColumnConfig = {
    'col_name': 'b', 'header_name':'sent_str_col', 'displayer_args': {'displayer': 'obj'},
             'color_map_config': {'color_rule': 'color_from_column', 'val_column': 'Volume_colors'}}
    expected_output: DFViewerConfig = {
        'pinned_rows': [],
        'column_config':  [
            {'col_name': 'a', 'header_name':'sent_int_col', 'displayer_args': {'displayer': 'obj'}},
            b_config
        ],
        'first_col_config': {'col_name': 'index', 'header_name':'index',
                             'displayer_args': {'displayer': 'obj'}},
        'component_config': {},
        'extra_grid_config': {},
    }

    actual = StylingAnalysis.get_dfviewer_config(sd, BASIC_DF)
    assert expected_output == actual


def rewrite_override():
    """
      certain column_config overrides, notably  tooltip and color map will reference original column configs

      They need to point at rewritten col_names

      """

    rewrites: Dist[str,str] =  {
        'Volume_colors': "ccc",
        'foo' : 'ddd'
    }
    color_from_column = {
              'color_map_config': {'color_rule': 'color_from_column', 'val_column': 'Volume_colors'}}
    rewritten_color_from_column = {
              'color_map_config': {'color_rule': 'color_from_column', 'val_column': 'ccc'}}
    #color_map_config.val_column
    assert rewrite_override_col_references(rewrites, color_from_column) == rewritten_color_from_column

    color_not_null =  {
        'color_map_config': {'color_rule': 'color_not_null', 'exist_column': 'foo'}}

    rewritten_color_not_null =  {
        'color_map_config': {'color_rule': 'color_not_null', 'exist_column': 'ddd'}}
    assert rewrite_override_col_references(rewrites, color_not_null) == rewritten_color_not_null
    #color_map_config.exist_column

    tooltip_config = {
        'tooltip_config': {'tooltip_type':'simple', 'val_column':'Volume_colors'}}

    rewritten_tooltip_config = {
        'tooltip_config': {'tooltip_type':'simple', 'val_column':'ccc'}}

    assert rewrite_override_col_references(rewrites, tooltip_config) == rewritten_tooltip_config
    no_rewrite_config = {
        'displayer_args': {'displayer':'boolean'}}
    assert rewrite_override_col_references(rewrites, no_rewrite_config.copy()) == no_rewrite_config

def test_override_columnconfig2() -> None:
    sd: SDType = {
        'a': {'orig_col_name': 'int_col', 'rewritten_col_name': 'a'},
        'int_col': {
            'column_config_override': {'color_map_config': {'color_rule': 'color_from_column', 'col_name': 'a'}}}}
    typed_df = pd.DataFrame(
    {'int_col': [1] * 5,
     # 'float_col': [.5] * ROWS,
     # "str_col": ["foobar"]* ROWS},
    })
    result = StylingAnalysis.style_columns(sd, typed_df)

    assert result[0]['col_name'] == 'a'
    print("0"*80)
    print(result[0])
    print("1"*80)
    print(result[1])
    print("&"*80)
    assert_dict_eq({'col_name':'a', 'header_name':'int_col',
                    'displayer_args': {'displayer': 'obj'},
                    'color_map_config': {'color_rule': 'color_from_column', 'col_name': 'a'}}, result[0])
