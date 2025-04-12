import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        # Tour of Buckaroo
        Buckaroo expedites the core task of data work by showing histograms and summary stats with every DataFrame.
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import buckaroo
    from buckaroo import BuckarooInfiniteWidget
    return BuckarooInfiniteWidget, buckaroo, mo, pd


@app.cell
def _(BuckarooInfiniteWidget, dropdown_dict, mo):
    mo.vstack(
        [
            dropdown_dict,
            #mo.ui.text(value=dropdown_dict.value),
            BuckarooInfiniteWidget(dropdown_dict.value[0], column_config_overrides = dropdown_dict.value[1])
        ]
    )
    return


@app.cell(hide_code=True)
def _(DataFrame):
    _ts_col = ["2020-01-01 01:00Z", "2020-01-01 02:00Z", "2020-02-28 02:00Z", "2020-03-15 02:00Z", None]
    datetime_df = DataFrame(
        {'timestamp': _ts_col,
         'timestamp_obj_displayer': _ts_col,
         'timestamp_datetime_default_displayer':_ts_col,
         'timestamp_datetime_locale_en-US':_ts_col,
         'timestamp_datetime_locale_en-US-Long':_ts_col,
         'timestamp_datetime_locale_en-GB':_ts_col})

    def _locale_col_conf(locale, args={}):
        return {'displayer_args': {'displayer': 'datetimeLocaleString',
                                'locale':locale,
                                'args':args}}
    datetime_config = {
        'timestamp_obj_displayer':  {'displayer_args': {'displayer': 'obj'}},    
        'timestamp_datetime_default_displayer' : {'displayer_args':  {'displayer': 'datetimeDefault'}},
        'timestamp_datetime_locale_en-US' : _locale_col_conf('en-US'),
        'timestamp_datetime_locale_en-US-Long': _locale_col_conf('en-US', { 'weekday': 'long'}),
        'timestamp_datetime_locale_en-GB' : _locale_col_conf('en-GB')}
    return datetime_config, datetime_df


@app.cell(hide_code=True)
def _(DataFrame):
    _base_str_col = ["asdf", "qwerty", "really long string, much  much longer",
                    None,  "A"]

    _str_df = DataFrame({
        'strings_string_displayer_max_len': _base_str_col,
        'strings_obj_displayer':  _base_str_col,
        'strings_string_displayer': _base_str_col})
    _str_config =  {
        'strings_string_displayer_max_len': {'displayer_args': {'displayer': 'string', 'max_length':35}},
        'strings_obj_displayer':  {'displayer_args': {'displayer': 'obj'}},      
        'strings_string_displayer': {'displayer_args': {'displayer': 'string'}},
    }
    str_config = (_str_df, _str_config)
    return (str_config,)


@app.cell(hide_code=True)
def _(DataFrame):
    _float_col = [5, -8, 13.23, -8.01, -999.345245234, None]
    _float_df = DataFrame({
        'float_obj_displayer': _float_col,
        'float_float_displayer_1__3': _float_col,
        'float_float_displayer_0__3': _float_col,
        'float_float_displayer_3__3': _float_col,
        'float_float_displayer_3_13': _float_col})
    def _float_col_conf(min_digits, max_digits):
        return {'displayer_args':
                { 'displayer': 'float', 'min_fraction_digits':min_digits, 'max_fraction_digits': max_digits}}
    _float_config = {
        'float_obj_displayer':  {'displayer_args': {'displayer': 'obj'}},      
        'float_float_displayer_1__3' : _float_col_conf(1,3),
        'float_float_displayer_0__3' : _float_col_conf(0,3),
        'float_float_displayer_3__3' : _float_col_conf(3,3),
        'float_float_displayer_3_13' : _float_col_conf(3,13)}
    float_config = (_float_df, _float_config)
    return (float_config,)


@app.cell(hide_code=True)
def _():
    # Extra utility functions and marimo overrides
    import numpy as np
    from buckaroo.marimo_utils import marimo_monkeypatch, BuckarooDataFrame as DataFrame

    # this overrides pd.read_csv and pd.read_parquet to return BuckarooDataFrames which overrides displays as BuckarooWidget, not the default marimo table
    marimo_monkeypatch()
    return DataFrame, marimo_monkeypatch, np


@app.cell
def _(float_config, mo, str_config):
    dfs = {"float_config": float_config, "str_config": str_config}
    dropdown_dict = mo.ui.dropdown(
        options=dfs,
        value="float_config",
        label="Choose the config",
    )
    return dfs, dropdown_dict


if __name__ == "__main__":
    app.run()
