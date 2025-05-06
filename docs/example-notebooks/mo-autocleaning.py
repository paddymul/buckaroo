import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _(ACBuckaroo, float_, obj_, pd):
    dirty_df = pd.DataFrame(
        {'a':[10,  20,  30,   40,  10, 20.3,  None,    8,  9, 10, 11, 20, None],
         'b':["3", "4", "a", "5", "5",  "b9", None, " 9",  "9-", 11, "867-5309", "-9", None],
        'us_dates': ["", "07/10/1982", "07/15/1982", "7/10/1982", "17/10/1982", "03/04/1982", "03/02/2002", "12/09/1968",
                      "03/04/1982", "", "06/22/2024", "07/4/1776", "07/20/1969"],
         "mostly_bool": [True, "True", "Yes", "On", "false", False, "1", "Off", "0", " 0", "No", 1, None]
        })
    bw = ACBuckaroo(
        dirty_df, 
        pinned_rows=[
            obj_('dtype'),
            float_('str_bool_frac'), float_('regular_int_parse_frac'), float_('strip_int_parse_frac'), float_('us_dates_frac'),
            obj_('cleaning_name')])

    bw
    return bw, dirty_df


@app.cell
def _(bw):
    bw.df_data_dict['all_stats']
    return


@app.cell
def _():
    from buckaroo.styling_helpers import obj_, float_
    return float_, obj_


@app.cell
def _(pd, re, s):
    from buckaroo.customizations.pandas_commands import (
        Command,
        SafeInt, DropCol, FillNA, GroupBy, NoOp, Search)
    from buckaroo.customizations.pandas_cleaning_commands import (
        IntParse, StrBool, USDate)
    from buckaroo.customizations.pd_autoclean_conf import (NoCleaningConf)
    from buckaroo.dataflow.autocleaning import AutocleaningConfig

    class StripIntParse(Command):
        command_default = [s('strip_int_parse'), s('df'), "col"]
        command_pattern = []

        @staticmethod 
        def transform(df, col):
            _digits_and_period = re.compile(r'[^\d\.]')
            _ser = df[col]
            _reg_parse = _ser.apply(pd.to_numeric, errors='coerce')
            _strip_parse = _ser.str.replace(_digits_and_period, "", regex=True).apply(pd.to_numeric, errors='coerce', dtype_backend='pyarrow')
            _combined = _reg_parse.fillna(_strip_parse)
            df[col] = _combined
            return df

        @staticmethod 
        def transform_to_py(df, col):
            return f"""    _digits_and_period = re.compile(r'[^\\d\\.]')
        _ser = df['{col}']
        _reg_parse = _ser.apply(pd.to_numeric, errors='coerce')
        _strip_parse = _ser.str.replace(_digits_and_period, "", regex=True).apply(pd.to_numeric, errors='coerce', dtype_backend='pyarrow')
        _combined = _reg_parse.fillna(_strip_parse)
        df['{col}'] = _combined"""
    return (
        AutocleaningConfig,
        Command,
        DropCol,
        FillNA,
        GroupBy,
        IntParse,
        NoCleaningConf,
        NoOp,
        SafeInt,
        Search,
        StrBool,
        StripIntParse,
        USDate,
    )


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import buckaroo
    from buckaroo import BuckarooInfiniteWidget
    import numpy as np
    from buckaroo.marimo_utils import marimo_monkeypatch, BuckarooDataFrame as DataFrame

    # this overrides pd.read_csv and pd.read_parquet to return BuckarooDataFrames which overrides displays as BuckarooWidget, not the default marimo table
    marimo_monkeypatch()
    return (
        BuckarooInfiniteWidget,
        DataFrame,
        buckaroo,
        marimo_monkeypatch,
        mo,
        np,
        pd,
    )


@app.cell
def _(np, pd):
    import re
    from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)
    def int_parse_frac(ser):
        null_count =  (~ ser.apply(pd.to_numeric, errors='coerce').isnull()).sum()
        return  null_count / len(ser)

    digits_and_period = re.compile(r'[^\d\.]')
    def strip_int_parse_frac(ser):
        if pd.api.types.is_object_dtype(ser):
            ser = ser.astype('string')
        if not pd.api.types.is_string_dtype(ser):
            return 0
        ser = ser.sample(np.min([300, len(ser)]))
        stripped = ser.str.replace(digits_and_period, "", regex=True)

        #don't like the string conversion here, should still be vectorized
        int_parsable = ser.astype(str).str.isdigit() 
        parsable = (int_parsable | (stripped != ""))
        return parsable.sum() / len(ser)


    TRUE_SYNONYMS = ["true", "yes", "on", "1"]
    FALSE_SYNONYMS = ["false", "no", "off", "0"]
    BOOL_SYNONYMS = TRUE_SYNONYMS + FALSE_SYNONYMS

    def str_bool_frac(ser):
        ser = ser.sample(np.min([300, len(ser)]))
        if pd.api.types.is_object_dtype(ser):
            ser = ser.astype('string')
        if not pd.api.types.is_string_dtype(ser):
            return 0
        matches = ser.str.lower().str.strip().isin(BOOL_SYNONYMS)
        return matches.sum() / len(ser)

    def us_dates_frac(ser):
        parsed_dates = pd.to_datetime(ser, errors='coerce', format="%m/%d/%Y")
        return (~ parsed_dates.isna()).sum() / len(ser)

    def euro_dates_frac(ser):
        parsed_dates = pd.to_datetime(ser, errors='coerce', format="%d/%m/%Y")
        return (~ parsed_dates.isna()).sum() / len(ser)

    class HeuristicFracs(ColAnalysis):
        provides_defaults = dict(
            str_bool_frac=0, regular_int_parse_frac=0, strip_int_parse_frac=0, us_dates_frac=0)

        @staticmethod
        def series_summary(sampled_ser, ser):
            if not (pd.api.types.is_string_dtype(ser) or pd.api.types.is_object_dtype(ser)):
                return {}

            return dict(
                str_bool_frac=str_bool_frac(ser),
                regular_int_parse_frac=int_parse_frac(ser),
                strip_int_parse_frac=strip_int_parse_frac(ser),
                us_dates_frac=us_dates_frac(ser))
    return (
        BOOL_SYNONYMS,
        ColAnalysis,
        FALSE_SYNONYMS,
        HeuristicFracs,
        TRUE_SYNONYMS,
        digits_and_period,
        euro_dates_frac,
        int_parse_frac,
        re,
        str_bool_frac,
        strip_int_parse_frac,
        us_dates_frac,
    )


@app.cell
def _(ColAnalysis, get_top_score, sA):
    class BaseHeuristicCleaningGenOps(ColAnalysis):
        """
        This class is meant to be extended with different rules passed in

        create other ColAnalysis classes that satisfy requires_summary

        Then put this group of classes into their own AutocleaningConfig
        """
        requires_summary = []
        provides_defaults = {'cleaning_ops': []}

        rules = {}
        rules_op_names = {}

        @classmethod
        def computed_summary(kls, column_metadata):
            cleaning_op_name = get_top_score(kls.rules, column_metadata)
            if cleaning_op_name == 'none':
                return {'cleaning_ops': [], 'cleaning_name':'None'}
            else:
                cleaning_name = kls.rules_op_names.get(cleaning_op_name, cleaning_op_name)
                ops = [sA(cleaning_name, clean_strategy= kls.__name__, clean_col=column_metadata['col_name'] ),
                    {'symbol': 'df'}]
                return {'cleaning_ops':ops, 'cleaning_name':cleaning_name, 'add_orig': True}        

    return (BaseHeuristicCleaningGenOps,)


@app.cell
def _(ColAnalysis):
    from buckaroo.jlisp.lisp_utils import s, sA
    from buckaroo.auto_clean.heuristic_lang import get_top_score

    class HeuristicCleaningGenOps(ColAnalysis):
        """
        This class is meant to be extended with different rules passed in

        create other ColAnalysis classes that satisfy requires_summary

        Then put this group of classes into their own AutocleaningConfig
        """
        requires_summary = ['str_bool_frac', 'regular_int_parse_frac', 'strip_int_parse_frac', 'us_dates_frac']
        provides_defaults = {'cleaning_ops': [], 'cleaning_name':""}

        rules = {
            'str_bool_frac':         [s('m>'), .7],
            'regular_int_parse_frac':  [s('m>'), .9],
            'strip_int_parse_frac':    [s('m>'), .7],
            'none':               [s('none-rule')],
            'us_dates_frac':         [s('primary'), [s('m>'), .7]]}

        rules_op_names = {
            'str_bool_frac':           'str_bool',
            'regular_int_parse_frac':  'regular_int_parse',
            'strip_int_parse_frac':    'strip_int_parse',
            'us_dates_frac':           'us_date'}

        @classmethod
        def computed_summary(kls, column_metadata):
            cleaning_op_name = get_top_score(kls.rules, column_metadata)
            if cleaning_op_name == 'none':
                return {'cleaning_ops': [], 'cleaning_name':'None'}
            else:
                cleaning_name = kls.rules_op_names.get(cleaning_op_name, cleaning_op_name)
                ops = [sA(cleaning_name, clean_strategy= kls.__name__, clean_col=column_metadata['col_name'] ),
                    {'symbol': 'df'}]
                return {'cleaning_ops':ops, 'cleaning_name':cleaning_name, 'add_orig': True}
    return HeuristicCleaningGenOps, get_top_score, s, sA


@app.cell
def _(BaseHeuristicCleaningGenOps, s):
    frac_name_to_command =  {
            'str_bool_frac':            'str_bool',
            'regular_int_parse_frac':   'regular_int_parse',
            'strip_int_parse_frac':     'strip_int_parse',
            'us_dates_frac':            'us_date'}

    class ConvservativeCleaningGenops(BaseHeuristicCleaningGenOps):
        requires_summary = ['str_bool_frac', 'regular_int_parse_frac', 'strip_int_parse_frac', 'us_dates_frac']

        rules = {
            'str_bool_frac':          [s('m>'), .9],
            'regular_int_parse_frac': [s('m>'), .9],
            'strip_int_parse_frac':   [s('m>'), .9],
            'none':                   [s('none-rule')],
            'us_dates_frac':          [s('primary'), [s('m>'), .8]]}
        rules_op_names = frac_name_to_command

    class AggresiveCleaningGenOps(BaseHeuristicCleaningGenOps):
        requires_summary = ['str_bool_frac', 'regular_int_parse_frac', 'strip_int_parse_frac', 'us_dates_frac']
        rules = {
            'str_bool_frac':          [s('m>'), .6],
            'regular_int_parse_frac': [s('m>'), .9],
            'strip_int_parse_frac':   [s('m>'), .75],
            'none':                   [s('none-rule')],
            'us_dates_frac':          [s('primary'), [s('m>'), .7]]}

        rules_op_names = frac_name_to_command
    return (
        AggresiveCleaningGenOps,
        ConvservativeCleaningGenops,
        frac_name_to_command,
    )


@app.cell
def _(
    AggresiveCleaningGenOps,
    AutocleaningConfig,
    BuckarooInfiniteWidget,
    ConvservativeCleaningGenops,
    DropCol,
    FillNA,
    GroupBy,
    HeuristicFracs,
    IntParse,
    NoCleaningConf,
    NoOp,
    Search,
    StrBool,
    StripIntParse,
    USDate,
):
    class AggressiveAC(AutocleaningConfig):
        autocleaning_analysis_klasses = [HeuristicFracs, AggresiveCleaningGenOps]
        command_klasses = [
            IntParse, StripIntParse, StrBool, USDate,
            DropCol, FillNA, GroupBy, NoOp,
            Search]

        quick_command_klasses = [Search]
        name="aggressive"

    class ConservativeAC(AggressiveAC):
        autocleaning_analysis_klasses = [HeuristicFracs, ConvservativeCleaningGenops]
        name="conservative"

    class ACBuckaroo(BuckarooInfiniteWidget):
        autoclean_conf = tuple([NoCleaningConf, AggressiveAC, ConservativeAC])
    return ACBuckaroo, AggressiveAC, ConservativeAC


if __name__ == "__main__":
    app.run()
