import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    #import marimo as mo
    #import pandas as pd
    #import buckaroo
    from buckaroo import ddd_library as ddd
    from buckaroo.marimo_utils import marimo_unmonkeypatch; marimo_unmonkeypatch()
    return (ddd,)


@app.cell
def _(BuckarooInfiniteWidget, dropdown_dict, mo):
    # Welcome to the the Buckaroo styling gallery

    # Give Marimo and this gallery a little bit of time to load. The rest of the app and explanatory text will load in about 30 seconds. A lot is going on, python is being downloaded to run via Web Assembly in your browser.
    disp_func = BuckarooInfiniteWidget
    mo.vstack(
        [
         dropdown_dict,
         disp_func(dropdown_dict.value[0]),
        mo.md(dropdown_dict.value[1])])
    return


@app.cell
def _(buckaroo, mo):
    def disp(df):
        return mo.plain(df)
    def disp(df):
        return df
    def disp(df):
        return buckaroo.BuckarooInfiniteWidget(df ) #, pinned_rows=[])
    def get_code(df):
        return mo.ui.code_editor(buckaroo.BuckarooInfiniteWidget(df).get_story_config())

    return (disp,)


@app.cell
def _():
    #mo.ui.code_editor(buckaroo.BuckarooInfiniteWidget(ddd.get_multiindex_index_df()).get_story_config())
    return


@app.cell
def _():
    #mo.ui.data_explorer(ddd.df_with_infinity())
    return


@app.cell
def _():
    #get_code(ddd.get_multiindex3_index_df())
    return


@app.cell(hide_code=True)
def _(ddd):

    _df = ddd.get_multiindex_cols_df()

    _explain_md = """
    ##  multi_index_cols_df
     This dataframe has a column multi_index

    """
    multiindex_cols_df_config = (_df, _explain_md)
    return (multiindex_cols_df_config,)


@app.cell(hide_code=True)
def _(ddd):

    _df = ddd.get_multiindex_with_names_index_df()

    _explain_md = """
    ##  multi_index_with_names_index_df
     This dataframe has a multi_index with names

    """
    multi_index_with_names_index_df_config = (_df, _explain_md)
    return (multi_index_with_names_index_df_config,)


@app.cell
def _(mo, multi_index_with_names_index_df_config, multiindex_cols_df_config):
    # The DFs and configs are defined in the above hidden cells.  Unhide them for details
    dfs = {
    'multiindex_cols_df_config': multiindex_cols_df_config,
    'multi_index_with_names_index_df_config': multi_index_with_names_index_df_config,
    }


    dropdown_dict = mo.ui.dropdown(
        options=dfs,
        value="multiindex_cols_df_config",
        label="Choose the config",
    )
    return (dropdown_dict,)


@app.cell(hide_code=True)
async def _():
    import marimo as mo
    import pandas as pd
    import sys

    if "pyodide" in sys.modules:  # a hacky way to figure out if we're running in pyodide
        import micropip

        await micropip.install("buckaroo")

    import buckaroo
    from buckaroo import BuckarooInfiniteWidget


    # Extra utility functions and marimo overrides
    import numpy as np
    from buckaroo.marimo_utils import marimo_monkeypatch, BuckarooDataFrame as DataFrame

    # this overrides pd.read_csv and pd.read_parquet to return BuckarooDataFrames which overrides displays as BuckarooWidget, not the default marimo table
    marimo_monkeypatch()
    import json
    import re


    def format_json(obj):
        """
        Formats obj to json  string to remove unnecessary whitespace.
        Returns:
            The formatted JSON string.
        """
        json_string = json.dumps(obj, indent=4)
        # Remove whitespace before closing curly braces
        formatted_string = re.sub(r"\s+}", "}", json_string)
        # formatted_string = json_string
        return formatted_string
    return BuckarooInfiniteWidget, buckaroo, mo


if __name__ == "__main__":
    app.run()
