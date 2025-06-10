"""
THe dastardly dataframe dataset.

The weirdest dataframes that cause trouble frquently

"""

import pandas as pd
import numpy as np

def get_basic_df():
    return pd.DataFrame({'a':[10,20,30]})

#from testing
def get_basic_df2() -> pd.DataFrame:
    return pd.DataFrame({'foo_col': [10, 20, 20], 'bar_col':['foo', 'bar', 'baz']})


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

def df_with_infinity() -> pd.DataFrame:
    return pd.DataFrame({'a': [np.nan, np.inf, np.inf * -1]})

def df_with_col_named_index() -> pd.DataFrame:
    return pd.DataFrame({'a':      ["asdf", "foo_b", "bar_a", "bar_b", "bar_c"],
                         'index':  ["7777", "ooooo", "--- -", "33333", "assdf"]})

def df_with_named_index() -> pd.DataFrame:
    """
      someone put the effort into naming the index, you'd probably want to display that
    """
    return pd.DataFrame({'a':      ["asdf", "foo_b", "bar_a", "bar_b", "bar_c"]},
                        index=pd.Index([10,20,30,40,50], name='foo'))


"""
Mkae a duplicate column dataframe

  the numeric column dataframe

  a dataframe with a column named index

  a dataframe with a named index

  a dataframe with series composed of names different than the column names
  

  """
