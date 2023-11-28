import polars as pl


import json
from collections import defaultdict
from typing import Any, Mapping, MutableMapping


def split_to_dicts(stat_df:pl.DataFrame) -> Mapping[str, MutableMapping[str, Any]]:
    summary: MutableMapping[str, MutableMapping[str, Any]] = defaultdict(lambda : {})
    for col in stat_df.columns:
        orig_col, measure = json.loads(col)
        summary[orig_col][measure] = stat_df[col][0]
    return summary