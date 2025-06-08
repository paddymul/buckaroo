from typing import List
import pytest
import pandas as pd
from buckaroo.dataflow.styling_core import ColumnConfig, DFViewerConfig, StylingAnalysis


def test_simple_styling() -> None:
    simple_df: pd.DataFrame = pd.DataFrame({
        'a':[10, 20, 30],
        'b':['foo', 'bar', 'baz']})

    dfvc: DFViewerConfig = StylingAnalysis.style_columns({'a':{}, 'b':{}}, simple_df)

    col_config: List[ColumnConfig] = dfvc['column_config']
    assert len(col_config) == 3
    assert col_config[1]['col_name'] == 'a'
    assert col_config[2]['col_name'] == 'b'
