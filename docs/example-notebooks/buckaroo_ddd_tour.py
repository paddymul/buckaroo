import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import buckaroo
    from buckaroo import ddd_library as ddd
    from buckaroo.marimo_utils import marimo_unmonkeypatch; marimo_unmonkeypatch()
    return buckaroo, ddd, mo


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
def _(ddd, disp):
    disp(ddd.get_basic_df())
    return


@app.cell
def _(ddd, disp):
    disp(ddd.get_multiindex_index_df())
    return


@app.cell
def _():
    #mo.ui.code_editor(buckaroo.BuckarooInfiniteWidget(ddd.get_multiindex_index_df()).get_story_config())
    return


@app.cell
def _(ddd, disp):
    disp(ddd.get_multiindex_index_df())
    return


@app.cell
def _(ddd, disp):
    disp(ddd.get_multiindex_with_names_index_df())
    return


@app.cell
def _(ddd, disp):
    disp(ddd.get_multiindex_index_multiindex_with_names_cols_df())
    return


@app.cell
def _(ddd, disp):
    disp(ddd.get_multiindex_index_with_names_multiindex_cols_df())
    # for single level indexes, use header_name, not one level col_path
    # index columns should be pinned also
    return


@app.cell
def _(ddd, disp):
    disp(ddd.get_multiindex_with_names_both())
    return


@app.cell
def _(ddd, mo):
    mo.plain(ddd.get_multiindex_with_names_both())
    return


@app.cell
def _(ddd, disp):
    disp(ddd.get_multiindex3_index_df())
    return


@app.cell
def _(ddd, disp):
    disp(ddd.df_with_infinity())
    return


@app.cell
def _():
    #mo.ui.data_explorer(ddd.df_with_infinity())
    return


@app.cell
def _():
    #get_code(ddd.get_multiindex3_index_df())
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
