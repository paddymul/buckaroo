import polars as pl
from buckaroo.customizations.polars_analysis import (
    VCAnalysis, PLCleaningStats, BasicAnalysis)
from buckaroo.pluggable_analysis_framework.polars_analysis_management import PlDfStats, PolarsAnalysis
from buckaroo.jlisp.lisp_utils import split_operations, lists_match
from buckaroo.dataflow.autocleaning import Autocleaning, merge_ops, format_ops
from buckaroo.customizations.polars_commands import (
    DropCol, FillNA, GroupBy #, OneHot, GroupBy, reindex
)



dirty_df = pl.DataFrame({
    'a':[10,  20,  30,   40,  10, 20.3,   5, None, None, None],
    'b':["3", "4", "a", "5", "5",  "b", "b", None, None, None]})


def make_default_analysis(**kwargs):
    class DefaultAnalysis(PolarsAnalysis):
        requires_summary = []
        provides_defaults = kwargs
    return DefaultAnalysis

class CleaningGenOps(PolarsAnalysis):
    requires_summary = ['int_parse_fail', 'int_parse']
    provides_defaults = {'cleaning_ops': []}

    int_parse_threshhold = .3
    @classmethod
    def computed_summary(kls, column_metadata):
        if column_metadata['int_parse'] > kls.int_parse_threshhold:
            return {'cleaning_ops': [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}]}
        else:
            return {'cleaning_ops': []}


def test_cleaning_stats():
    dfs = PlDfStats(dirty_df, [VCAnalysis, PLCleaningStats, BasicAnalysis])

    # "3", "4", "5", "5"   4 out of 10
    assert dfs.sdf['b']['int_parse'] == 0.4
    assert dfs.sdf['b']['int_parse_fail'] == 0.6


SAFE_INT_TOKEN = [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}]
def test_ops_gen():

    dfs = PlDfStats(dirty_df, [make_default_analysis(int_parse=.4, int_parse_fail=.6),
                               CleaningGenOps], debug=True)
    assert dfs.sdf['b']['cleaning_ops'] == SAFE_INT_TOKEN
    dfs = PlDfStats(dirty_df, [make_default_analysis(int_parse=.2, int_parse_fail=.8),
                               CleaningGenOps])
    assert dfs.sdf['b']['cleaning_ops'] == []



def test_format_ops():
    column_meta = {
        'a': {'cleaning_ops':SAFE_INT_TOKEN },
        'b': {'cleaning_ops': [{'symbol': 'replace_dirty', 'meta':{'auto_clean': True}}, '\n', None]}}

    expected_ops = [
        [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}, 'a'],
        [{'symbol': 'replace_dirty', 'meta':{'auto_clean': True}}, 'b', '\n', None]]
    assert format_ops(column_meta) == expected_ops


class AlwaysSafeIntGenOps(PolarsAnalysis):
    requires_summary = []
    provides_defaults = {'cleaning_ops': []}

    @classmethod
    def computed_summary(kls, column_metadata):
        return {'cleaning_ops': [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}]}

def test_merge_ops():
    existing_ops = [
        [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}, 'a'],
        [{'symbol': 'usergen'}, 'foo_column']
    ]

    cleaning_ops = [
        [{'symbol': 'new_cleaning', 'meta':{'auto_clean': True}}, 'a']]

    expected_merged = [
        [{'symbol': 'new_cleaning', 'meta':{'auto_clean': True}}, 'a'],
        [{'symbol': 'usergen'}, 'foo_column']
    ]
    print( merge_ops(existing_ops, cleaning_ops))
    print("@"*80)
    assert merge_ops(existing_ops, cleaning_ops) == expected_merged
        

def test_handle_user_ops():

    
    class ACModded(Autocleaning):
        autocleaning_analysis_klasses = [VCAnalysis, PLCleaningStats, BasicAnalysis, CleaningGenOps]
        command_klasses = [DropCol, FillNA, GroupBy]
    
    ac = ACModded()    
    df = pl.DataFrame({'a': [10, 20, 30]})

    cleaning_result = ac.handle_ops_and_clean(df, cleaning_method='normal', existing_operations=[])

    cleaned_df, cleaning_sd, generated_code, merged_operations = cleaning_result
    
    
    assert merged_operations == [
        [{'symbol': 'safe_int', 'meta':{'auto_clean': True}}, 'a']]
