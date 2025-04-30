import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _(ACBuckaroo, pd):
    dirty_df = pd.DataFrame(
        {'a':[10,  20,  30,   40,  10, 20.3, None,],
         'b':["3", "4", "a", "5", "5",  "b", None ]})

    #bw2 = ACBuckaroo(citibike_df)
    bw2 = ACBuckaroo(dirty_df)
    bw2
    return bw2, dirty_df


@app.cell
def _(AggresiveCleaningGenOps, BuckarooInfiniteWidget, HeuristicFracs):
    from buckaroo.customizations.pandas_commands import (
        Command,
        SafeInt, DropCol, FillNA, GroupBy, NoOp, Search)
    from buckaroo.customizations.pandas_cleaning_commands import (
        IntParse, StripIntParse, StrBool, USDate)
    from buckaroo.customizations.pd_autoclean_conf import (NoCleaningConf)
    from buckaroo.dataflow.autocleaning import AutocleaningConfig

    class ACHeuristic(AutocleaningConfig):
        """
        add a check between rules_op_names to all of the included command classes
        """
        autocleaning_analysis_klasses = [HeuristicFracs, AggresiveCleaningGenOps]
        command_klasses = [
            IntParse, StripIntParse, StrBool, USDate,
            DropCol, FillNA, GroupBy, NoOp,
            Search]

        quick_command_klasses = [Search]
        name="default"

    class BlankCleaning(AutocleaningConfig):
        """

        """
        quick_command_klasses = [Search]
        name=""

    class ACBuckaroo(BuckarooInfiniteWidget):
        autoclean_conf = tuple([ACHeuristic, NoCleaningConf])
        #autoclean_conf = tuple([ACHeuristic])
    return (
        ACBuckaroo,
        ACHeuristic,
        AutocleaningConfig,
        BlankCleaning,
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
    citibike_df = pd.read_parquet('./citibike-trips-2016-04.parq')
    citibike_df

    bw = BuckarooInfiniteWidget(citibike_df)
    bw.buckaroo_state = {
      "cleaning_method": "NoCleaning",
      "post_processing": "",
      "sampled": False,
      "show_commands": "on",
      "df_display": "main",
      "search_string": "",
      "quick_command_args": {}
    }
    #bw
    return (
        BuckarooInfiniteWidget,
        DataFrame,
        buckaroo,
        bw,
        citibike_df,
        marimo_monkeypatch,
        mo,
        np,
        pd,
    )


@app.cell
def _(pd):
    import re
    from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)
    def int_parse_frac(ser):
        null_count =  (~ ser.apply(pd.to_numeric, errors='coerce').isnull()).sum()
        return  null_count / len(ser)

    digits_and_period = re.compile(r'[^\d\.]')
    def strip_int_parse_frac(ser):
        stripped = ser.str.replace(digits_and_period, "", regex=True)

        #don't like the string conversion here, should still be vectorized
        int_parsable = ser.astype(str).str.isdigit() 
        parsable = (int_parsable | (stripped != ""))
        return parsable.sum() / len(ser)


    TRUE_SYNONYMS = ["true", "yes", "on", "1"]
    FALSE_SYNONYMS = ["false", "no", "off", "0"]
    BOOL_SYNONYMS = TRUE_SYNONYMS + FALSE_SYNONYMS

    def str_bool_frac(ser):
        matches = ser.str.lower().isin(BOOL_SYNONYMS)
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
def _(ColAnalysis):
    from buckaroo.jlisp.lisp_utils import s
    from buckaroo.auto_clean.heuristic_lang import get_top_score

    class HeuristicCleaningGenOps(ColAnalysis):
        """
        This class is meant to be extended with idfferent rules passed in

        create other ColAnalysis classes that satisfy requires_summary

        Then put this group of classes into their own AutocleaningConfig
        """
        requires_summary = ['str_bool_frac', 'regular_int_parse_frac', 'strip_int_parse_frac', 'us_dates_frac']
        provides_defaults = {'cleaning_ops': []}

        rules = {
            'str_bool_frac':         [s('m>'), .7],
            'regular_int_parse_frac':  [s('m>'), .9],
            'strip_int_parse_frac':    [s('m>'), .7],
            'none':               [s('none-rule')],
            'us_dates_frac':         [s('primary'), [s('m>'), .7]]}

        rules_op_names = {
            'str_bool_frac': 'str_bool',
            'regular_int_parse_frac': 'regular_int_parse',
            'strip_int_parse_frac':    'strip_int_parse',
            'us_dates_frac':         'us_date'}


        @classmethod
        def computed_summary(kls, column_metadata):

            cleaning_op_name = get_top_score(kls.rules, column_metadata)
            print("cleaning_op_name", cleaning_op_name, column_metadata)
            if cleaning_op_name == 'none':
                return {'cleaning_ops': []}
            else:
                ops = [
                    {'symbol': kls.rules_op_names.get(cleaning_op_name, cleaning_op_name),
                     'meta':{ 'auto_clean': True, 'clean_strategy': kls.__name__}},
                    {'symbol': 'df'}]
                print("ops", ops)

                return {'cleaning_ops':ops, 'add_orig': True}
    return HeuristicCleaningGenOps, get_top_score, s


@app.cell
def _(HeuristicCleaningGenOps, s):
    class AggresiveCleaningGenOps(HeuristicCleaningGenOps):
        requires_summary = ['str_bool_frac', 'regular_int_parse_frac', 'strip_int_parse_frac', 'us_dates_frac']
        provides_defaults = {'cleaning_ops': []}

        rules = {
            'str_bool_frac':         [s('m>'), .7],
            'regular_int_parse_frac':  [s('m>'), .9],
            'strip_int_parse_frac':    [s('m>'), .7],
            'none':               [s('none-rule')],
            'us_dates_frac':         [s('primary'), [s('m>'), .7]]}

        rules_op_names = {
            'str_bool_frac': 'str_bool',
            'regular_int_parse_frac': 'regular_int_parse',
            'strip_int_parse_frac':    'strip_int_parse',
            'us_dates_frac':         'us_date'}
    return (AggresiveCleaningGenOps,)


@app.cell
def _(bw2):
    bw2.buckaroo_options
    return


@app.cell
def _(bw2):
    bw2.buckaroo_state
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
