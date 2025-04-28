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
