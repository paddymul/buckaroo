import polars as pl
from buckaroo.customizations.polars_analysis import (
    VCAnalysis, PLCleaningStats, BasicAnalysis)
from buckaroo.pluggable_analysis_framework.polars_analysis_management import PlDfStats, PolarsAnalysis

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
            return {'cleaning_ops': ['clean_int']}
        else:
            return {'cleaning_ops': []}


def test_cleaning_stats():
    dfs = PlDfStats(dirty_df, [VCAnalysis, PLCleaningStats, BasicAnalysis])

    # "3", "4", "5", "5"   4 out of 10
    assert dfs.sdf['b']['int_parse'] == 0.4
    assert dfs.sdf['b']['int_parse_fail'] == 0.6

def test_ops_gen():

    dfs = PlDfStats(dirty_df, [make_default_analysis(int_parse=.4, int_parse_fail=.6),
                               CleaningGenOps], debug=True)
    assert dfs.sdf['b']['cleaning_ops'] == ['clean_int']
    dfs = PlDfStats(dirty_df, [make_default_analysis(int_parse=.2, int_parse_fail=.8),
                               CleaningGenOps])
    assert dfs.sdf['b']['cleaning_ops'] == []


def format_ops(column_meta):
    ret_ops = []
    for k,v in column_meta.items():
        ops = v['cleaning_ops']
        if len(ops) > 0:
            temp_ops = ops.copy()
            temp_ops.insert(1, k)
            ret_ops.append(temp_ops)
    return ret_ops

def test_format_ops():

    column_meta = {'a': {'cleaning_ops':['clean_int']},
                   'b': {'cleaning_ops':['replace_dirty', '\n', None]}}

    expected_ops = [
        ['clean_int', 'a'],
        ['replace_dirty', 'b', '\n', None]]
    assert format_ops(column_meta) == expected_ops

