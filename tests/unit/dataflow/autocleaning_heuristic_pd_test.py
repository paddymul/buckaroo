import pandas as pd
from buckaroo.customizations.analysis import (
    DefaultSummaryStats, PdCleaningStats)
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)
from buckaroo.dataflow.autocleaning import AutocleaningConfig
from buckaroo.dataflow.autocleaning import PandasAutocleaning
from buckaroo.customizations.pandas_commands import (
    SafeInt, DropCol, FillNA, GroupBy, NoOp, Search
)
from buckaroo.customizations.pd_autoclean_conf import (NoCleaningConf)
from buckaroo.auto_clean.heuristic_lang import eval_heuristic_rule, eval_heuristics, get_top_score
from buckaroo.jlisp.lisp_utils import s


dirty_df = pd.DataFrame(
    {'a':[10,  20,  30,   40,  10, 20.3,   5, None, None, None],
     'b':["3", "4", "a", "5", "5",  "b", "b", None, None, None]})


def make_default_analysis(**kwargs):
    class DefaultAnalysis(ColAnalysis):
        requires_summary = []
        provides_defaults = kwargs
    return DefaultAnalysis

class CleaningGenOps(ColAnalysis):
    requires_summary = ['int_parse_fail', 'int_parse']
    provides_defaults = {'cleaning_ops': []}

    int_parse_threshhold = .3
    @classmethod
    def computed_summary(kls, column_metadata):
        if column_metadata['int_parse'] > kls.int_parse_threshhold:
            return {'cleaning_ops': [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}, {'symbol': 'df'}],
                    'add_orig': True}
        else:
            return {'cleaning_ops': []}


class ACConf(AutocleaningConfig):
    autocleaning_analysis_klasses = [DefaultSummaryStats, CleaningGenOps, PdCleaningStats]
    command_klasses = [DropCol, FillNA, GroupBy, NoOp, SafeInt, Search]
    quick_command_klasses = [Search]
    name="default"


EXPECTED_GEN_CODE = """def clean(df):
    df['a'] = smart_to_int(df['a'])
    return df"""

def test_autoclean_codegen():
    ac = PandasAutocleaning([ACConf, NoCleaningConf])
    df = pd.DataFrame({'a': ["30", "40"]})
    cleaning_result = ac.handle_ops_and_clean(
        df, cleaning_method='default', quick_command_args={}, existing_operations=[])
    cleaned_df, cleaning_sd, generated_code, merged_operations = cleaning_result

    assert generated_code == EXPECTED_GEN_CODE



class HeuristicCleaningGenOps(ColAnalysis):
    """
    This class is meant to be extended with idfferent rules passed in

    create other ColAnalysis classes that satisfy requires_summary

    Then put this group of classes into their own AutocleaningConfig
    """
    requires_summary = ['t_str_bool', 'regular_int_parse', 'strip_int_parse', 't_us_dates']
    provides_defaults = {'cleaning_ops': []}

    rules = {
        't_str_bool':         [s('m>'), .7],
        'regular_int_parse':  [s('m>'), .9],
        'strip_int_parse':    [s('m>'), .7],
        'none':               [s('none-rule')],
        't_us_dates':         [s('primary'), [s('m>'), .7]]}


    @classmethod
    def computed_summary(kls, column_metadata):

        cleaning_op_name = get_top_score(kls.rules, column_metadata)
        if cleaning_op_name == 'none':
            return {'cleaning_ops': []}
        else:
            return {'cleaning_ops': [
                {'symbol': cleaning_op_name,
                 'meta':{ 'auto_clean': True, 'clean_strategy': kls.__name__}},
                {'symbol': 'df'}],
                    'add_orig': True}



class ACHeuristic(AutocleaningConfig):
    autocleaning_analysis_klasses = [DefaultSummaryStats, HeuristicCleaningGenOps, PdCleaningStats]
    command_klasses = [DropCol, FillNA, GroupBy, NoOp, SafeInt, Search]
    quick_command_klasses = [Search]
    name="default"


EXPECTED_GEN_CODE = """def clean(df):
    df['a'] = smart_to_int(df['a'])
    return df"""

def test_heuristic_autoclean_codegen():
    ac = PandasAutocleaning([ACHeuristic, NoCleaningConf])
    df = pd.DataFrame({'a': ["30", "40"]})
    cleaning_result = ac.handle_ops_and_clean(
        df, cleaning_method='default', quick_command_args={}, existing_operations=[])
    cleaned_df, cleaning_sd, generated_code, merged_operations = cleaning_result

    assert generated_code == EXPECTED_GEN_CODE
