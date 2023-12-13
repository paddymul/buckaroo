from unittest import TestCase

import polars as pl
import numpy as np
from polars import functions as F
from buckaroo.customizations.polars_analysis import VCAnalysis, HistogramAnalysis

from buckaroo.pluggable_analysis_framework.utils import (json_postfix, replace_in_dict)

from buckaroo.pluggable_analysis_framework.polars_analysis_management import (
    produce_series_df, PolarsAnalysis, extract_table_hint)

test_df = pl.DataFrame({
        'normal_int_series' : pl.Series([1,2,3,4]),
        #'empty_na_ser' : pl.Series([pl.Null] * 4, dtype="Int64"),
        'float_nan_ser' : pl.Series([3.5, np.nan, 4.8, 2.2])
    })

word_only_df = pl.DataFrame({'letters': 'h o r s e'.split(' ')})

df = pl.read_csv('./examples/data/2014-01-citibike-tripdata.csv')

empty_df = pl.DataFrame({})
#empty_df_with_columns = pl.DataFrame({}, columns=[0])



class SelectOnlyAnalysis(PolarsAnalysis):

    select_clauses = [
        F.all().null_count().name.map(json_postfix('null_count')),
        F.all().mean().name.map(json_postfix('mean')),
        F.all().quantile(.99).name.map(json_postfix('quin99'))]


def test_produce_series_df():
    """just make sure this doesn't fail"""
    
    sdf, errs = produce_series_df(
        test_df, [SelectOnlyAnalysis], 'test_df', debug=True)
    expected = {
        'float_nan_ser':      {'mean': None, 'null_count':  0, 'quin99': None},
        'normal_int_series':  {'mean': 2.5,  'null_count':  0, 'quin99':  4.0}}
    dsdf = replace_in_dict(sdf, [(np.nan, None)])
    assert dsdf == expected

class MaxAnalysis(PolarsAnalysis):
    select_clauses = [F.all().max().name.map(json_postfix('max'))]

def test_produce_series_combine_df():
    """just make sure this doesn't fail"""
    
    sdf, errs = produce_series_df(
        test_df, [SelectOnlyAnalysis, MaxAnalysis], 'test_df', debug=True)
    expected = {
        'float_nan_ser':      {'mean': None, 'null_count':  0, 'quin99': None, 'max': 4.8},
        'normal_int_series':  {'mean': 2.5,  'null_count':  0, 'quin99':  4.0, 'max': 4.0},
        }
    dsdf = replace_in_dict(sdf, [(np.nan, None)])
    assert dsdf == expected

def test_produce_series_column_ops():
    mixed_df = pl.DataFrame(
        {'string_col': ["foo", "bar", "baz"] + [""]*2,
         'int_col':[1,2,3,30, 100],
         'float_col':[1.1, 1.1, 3, 3, 5]})

    summary_df, _unused = produce_series_df(mixed_df, [HistogramAnalysis])
    assert summary_df["string_col"] == {}

    assert summary_df["int_col"]["histogram_args"]["meat_histogram"] == (
        [2,  0,  0,  0,  0,  0,  0,  0,  0,  1],
        [1.0,  4.0,  7.0,  10.0,  13.0,  16.0,  19.0,  22.0,  25.0,  28.0,  100.0],)
    


def test_histogram_analysis():
    cats = [chr(x) for x in range(97, 102)] * 2 
    cats += [chr(x) for x in range(103,113)]
    cats += ['foo']*30 + ['bar'] * 50

    df = pl.DataFrame({'categorical': cats})
    summary_df, _unused = produce_series_df(df, [VCAnalysis, HistogramAnalysis])
    assert summary_df["categorical_histogram"] == {'foo':30}
    
    #.5 bar, .3 foo , 10% longtail, 10% unique

def test_extract_table_hint():

    summary_dict = {'a': {'null_count': 0,
                          'mean': 35.0,
                          'max': 100,
                          'min': 2,
                          'is_numeric': True,
                          '_type': 'integer',
                          'type': 'integer'}
                    }


    expected =  {
        'a': {
            'type':'integer',
            'is_numeric': True,
            'is_integer': None,
            'min_digits':None,
            'max_digits':None,
            'formatter':None,
            'histogram': []}}
    TestCase().assertDictEqual(expected, extract_table_hint(summary_dict, ['a']))




'''
class TestAnalysisPipeline(unittest.TestCase):

    def test_produce_series_df(self):
        """just make sure this doesn't fail"""

        sdf, errs = produce_series_df(
            test_df, [Len], 'test_df', debug=True)
        ld = {'len':4}
        assert sdf == {'normal_int_series': ld, 'empty_na_ser': ld, 'float_nan_ser': ld}

        sdf2, errs = produce_series_df(
            test_df, [DistinctCount], 'test_df', debug=True)
        assert sdf2 == {'normal_int_series': {'distinct_count': 4},
                        'empty_na_ser': {'distinct_count':0}, 'float_nan_ser': {'distinct_count':2}}

        sdf3, errs = produce_series_df(
            test_df, [DistinctCount, DistinctPer], 'test_df', debug=True)
        assert sdf3 == {'normal_int_series': {'distinct_count': 4},
                        'empty_na_ser': {'distinct_count':0}, 'float_nan_ser': {'distinct_count':2}}

    def test_full_produce_summary_df(self):
        """just make sure this doesn't fail"""
        sdf, th, errs = full_produce_summary_df(
            test_df, [DistinctCount, Len, DistinctPer], 'test_df', debug=True)
        assert errs == {}

    def test_full_produce_summary_df_empy(self):
        """just make sure this doesn't fail"""
        
        sdf, th, errs = full_produce_summary_df(
            empty_df, [DistinctCount, Len, DistinctPer], 'test_df', debug=True)
        assert errs == {}

    def test_full_produce_summary_df_empy2(self):
        """just make sure this doesn't fail"""
        
        sdf, th, errs = full_produce_summary_df(
            empty_df_with_columns, [DistinctCount, Len, DistinctPer], 'test_df', debug=True)
        assert errs == {}

    def test_produce_summary_df_hints(self):
        #this test should be ported over to the full basic_widget test with actaul verificaiton of values
        
        summary_df, hints, errs = full_produce_summary_df(
            test_df, [DumbTableHints], 'test_df')

        for col, hint_obj in hints.items():
            #hacky replication of typescript types, just basically testing that hints are constructed properly
            if hint_obj['is_numeric'] is False:
                assert 'histogram' in hint_obj.keys()
            else:
                expected_set = set(
                    ['is_numeric', 'is_integer', 'min_digits', 'max_digits', 'type', 'formatter', 'histogram'])
                assert expected_set == set(hint_obj.keys())

    def test_pipeline_base(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        #just verify that there are no errors
        ap.process_df(df)

    def test_add_aobj(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        class Foo(ColAnalysis):
            provides_summary = ['foo']
            requires_summary = ['length']

            @staticmethod
            def computed_summary(summary):
                return dict(foo=8)
        assert ap.add_analysis(Foo) == (True, []) #verify no errors thrown
        sdf, _unused, _unused_errs = ap.process_df(df)
        self.assertEqual(sdf['tripduration']['foo'], 8)

    def test_add_buggy_aobj(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        class Foo(ColAnalysis):
            provides_summary = ['foo']
            requires_summary = ['length']

            @staticmethod
            def computed_summary(summary_dict):
                1/0 #throw an error
                return dict(foo=8)
        unit_test_results, errs = ap.add_analysis(Foo)
        
        assert unit_test_results is False

    def test_replace_aobj(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        class Foo(ColAnalysis):
            provides_summary = ['foo']
            requires_summary = ['length']

            @staticmethod
            def computed_summary(bar):
                return dict(foo=8)
        ap.add_analysis(Foo)
        sdf, _unused, _unused_errs = ap.process_df(df)
        self.assertEqual(sdf['tripduration']['foo'], 8)
        #18 facts returned about tripduration
        #FIXME
        #self.assertEqual(len(sdf['tripduration']), 18)
        #Create an updated Foo that returns 9
        class Foo(ColAnalysis):
            provides_summary = ['foo']
            requires_summary = ['length']

            @staticmethod
            def computed_summary(bar):
                return dict(foo=9)
        ap.add_analysis(Foo)
        sdf2, _unused, _unused_errs = ap.process_df(df)
        self.assertEqual(sdf2['tripduration']['foo'], 9)
        #still 18 facts returned about tripduration
        #self.assertEqual(len(sdf2['tripduration']), 18)
        #Create an updated Foo that returns 9

    def xtest_summary_stats_display(self):
        """I don't remember what this test does, and I can't get it
        to work after the series_summary refactor
        """
        ap = AnalsysisPipeline([TypingStats])
        self.assertEqual(ap.summary_stats_display, "all")
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        print(ap.summary_stats_display)
        self.assertTrue("dtype" in ap.summary_stats_display)

    def test_add_summary_stats_display(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        class Foo(ColAnalysis):
            provides_summary = ['foo']
            requires_summary = ['length']
            summary_stats_display = ['foo']

        ap.add_analysis(Foo)
        self.assertEquals(ap.summary_stats_display, ['foo'])

    def test_invalid_summary_stats_display_throws(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        class Foo(ColAnalysis):
            provides_summary = ['foo']
            requires_summary = ['length']
            summary_stats_display = ['not_provided']

        def bad_add():
            ap.add_analysis(Foo)            

        self.assertRaises(NonExistentSummaryRowException, bad_add)

    def test_invalid_summary_stats_display_throws2(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        class Foo(ColAnalysis):
            provides_summary = ['foo']
            requires_summary = ['length']
            summary_stats_display = ['not_provided']

        def bad_add():
            ap.add_analysis(Foo)            

        self.assertRaises(NonExistentSummaryRowException, bad_add)



class SometimesProvides(ColAnalysis):
    provides_summary = ['conditional_on_dtype']

    summary_stats_display = ['conditional_on_dtype']
    
    @staticmethod
    def series_summary(ser, ser2):
        import pandas as pd
        is_numeric = pd.api.types.is_numeric_dtype(ser)
        if is_numeric:
            return dict(conditional_on_dtype=True)
        return {}

class TestDfStats(unittest.TestCase):
    def test_dfstats_sometimes_present(self):
        """many ColAnalysis objects are written such that they only
        provide stats for certain dtypes. This used to cause
        instantiation failures. This test verifies that there are no
        stack traces. The alternative would be to have ColAnalyis
        objects always return every key, even if NA. That's a less
        natural style to write analyis code.

        Possible future improvement is to run through PERVERSE_DF and
        verify that each ColAnalyis provides its specified value as
        non NA at least once

        """
        #dfs = DfStats(word_only_df, [SometimesProvides])
        #ab = dfs.presentation_sdf

        #triggers a getter?
        DfStats(word_only_df, [SometimesProvides]).presentation_sdf


'''
