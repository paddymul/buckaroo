import pandas as pd

"""
THe dastardly dataframe dataset.

The weirdest dataframes that cause trouble frquently

"""

def get_basic_df():
    return pd.DataFrame({'a':[10,20,30]})

def get_multi_index_cols_df(rows=15) -> pd.DataFrame:
    cols = pd.MultiIndex.from_tuples(
    [('foo', 'a'), ('foo', 'b'),  ('bar', 'a'), ('bar', 'b'), ('bar', 'c')])
    return pd.DataFrame(
        [["asdf","foo_b", "bar_a", "bar_b", "bar_c"]] * rows,
        columns=cols)
def get_tuple_cols_df(rows=15) -> pd.DataFrame:
    multi_col_df = get_multi_index_cols_df(rows)
    multi_col_df.columns = multi_col_df.columns.to_flat_index()
    return multi_col_df
