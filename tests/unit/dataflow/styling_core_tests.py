from typing import List
import pandas as pd
from buckaroo.dataflow.styling_core import ColumnConfig, DFViewerConfig, StylingAnalysis
from buckaroo.ddd_library import get_multi_index_cols_df
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import SDType


def test_simple_styling() -> None:
    simple_df: pd.DataFrame = pd.DataFrame({
        'a':[10, 20, 30],
        'b':['foo', 'bar', 'baz']})

    dfvc: DFViewerConfig = StylingAnalysis.style_columns({'a':{}, 'b':{}}, simple_df)

    col_config: List[ColumnConfig] = dfvc['column_config']
    assert len(col_config) == 3
    assert col_config[1]['col_name'] == 'a'
    assert col_config[2]['col_name'] == 'b'

def test_multi_index_styling() -> None:

    mic_df: pd.DataFrame = get_multi_index_cols_df()
    fake_sd:SDType = {
        "('foo', 'a')": {},
        "('foo', 'b')": {},
        "('bar', 'a')": {}
    }

    dfvc: DFViewerConfig = StylingAnalysis.style_columns(fake_sd, mic_df)

    col_config: List[ColumnConfig] = dfvc['column_config']
    assert len(col_config) == 4
    assert col_config[0]['col_path'] == ('index', '')
    assert col_config[1]['col_path'] == ('foo', 'a')
    assert col_config[2]['col_path'] == ('foo', 'b')
    assert col_config[3]['col_path'] == ('bar', 'a')

def test_tuple_col_styling() -> None:

    mic_df: pd.DataFrame = get_tuple_cols_df()
    fake_sd:SDType = {
        "('foo', 'a')": {},
        "('foo', 'b')": {},
        "('bar', 'a')": {}
    }

    dfvc: DFViewerConfig = StylingAnalysis.style_columns(fake_sd, mic_df)

    col_config: List[ColumnConfig] = dfvc['column_config']
    assert len(col_config) == 4
    #assert col_config[0]['col_name'] == "('index', '')"
    print(col_config[1])
    assert col_config[0]['col_path'] == ('index', '')
    assert col_config[1]['col_path'] == ('foo', 'a')
    assert col_config[2]['col_path'] == ('foo', 'b')
    assert col_config[3]['col_path'] == ('bar', 'a')
