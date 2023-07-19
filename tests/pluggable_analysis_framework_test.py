import unittest
import pytest
import pandas as pd
import numpy as np
import graphlib
from buckaroo.pluggable_analysis_framework import (
    ColAnalysis, order_analysis, check_solvable, NotProvidedException,
    AnalsysisPipeline, produce_summary_df)

from buckaroo.analysis import (TypingStats, DefaultSummaryStats)

class NoRoute(ColAnalysis):    
    provided_summary = ['not_used']
    requires_summary = ["does_not_exist"]
    
class CycleA(ColAnalysis):
    provided_summary = ['cycle_a']
    requires_summary = ["cycle_b"]

class CycleB(ColAnalysis):
    provided_summary = ['cycle_b']
    requires_summary = ["cycle_a"]


class CA_AB(ColAnalysis):
    provided_summary = ["a", "b"]

class CA_CD(ColAnalysis):
    provided_summary = ["c", "d"]

class CA_EF(ColAnalysis):
    provided_summary = ["e", "f"]
    requires_summary = ["a", "b", "c", "d"]

class CA_G(ColAnalysis):
    provided_summary = ["g"]
    requires_summary = ["e"]

test_df = pd.DataFrame({
        'normal_int_series' : pd.Series([1,2,3,4]),
        'empty_na_ser' : pd.Series([], dtype="Int64"),
        'float_nan_ser' : pd.Series([3.5, np.nan, 4.8])
    })

class DistinctCount(ColAnalysis):
    requires_raw = True
    provided_summary = ["distinct_count"]
    @staticmethod
    def summary(sampled_ser, summary_ser, raw_ser):
        val_counts = raw_ser.value_counts()
        distinct_count= len(val_counts)
        return {'distinct_count': distinct_count}

class Len(ColAnalysis):
    provided_summary = ["len"]
    requires_raw = True
    @staticmethod
    def summary(sampled_ser, summary_ser, raw_ser):
        return {'len': len(raw_ser)}

class DCLen(ColAnalysis):
    provided_summary = ["len", "distinct_count"]
    requires_raw = True
    @staticmethod
    def summary(sampled_ser, summary_ser, raw_ser):
        val_counts = raw_ser.value_counts()
        distinct_count= len(val_counts)
        return {'len':len(raw_ser), 'distinct_count':distinct_count}

class DistinctPer(ColAnalysis):
    provided_summary = ["distinct_per"]
    requires_summary = ["len", "distinct_count"]
    
    @staticmethod
    def summary(sampled_ser, summary_ser, raw_ser):
        return {'distinct_per': summary_ser.loc['distinct_count'] / summary_ser.loc['len']}



class TestOrderAnalysis(unittest.TestCase):

    def test_default_order(self):
        self.assertEqual(
            order_analysis([DistinctCount, Len, DistinctPer]),
            [DistinctCount, Len, DistinctPer])
        self.assertEqual(
            order_analysis([DistinctPer, DistinctCount, Len]),
            [DistinctCount, Len, DistinctPer])
    
    def test_multiple_provides(self):
        self.assertEqual(
            order_analysis([DCLen, DistinctPer]),
            [DCLen, DistinctPer])
        self.assertEqual(
            order_analysis([DistinctPer, DCLen]),
            [DCLen, DistinctPer])
        self.assertEqual(
            order_analysis([CA_G, CA_CD, CA_AB, CA_EF]),
            [CA_CD, CA_AB, CA_EF, CA_G])
            #note the order between CA_CD and CA_AB doesn't matter - 
            # as long as they occur before other classes
        
    def test_cycle(self):
        with self.assertRaises(graphlib.CycleError):
            order_analysis([CycleA, CycleB])
            
    def test_no_route(self):
        check_solvable([Len])
        with self.assertRaises(NotProvidedException):
            check_solvable([NoRoute])

df = pd.read_csv('./examples/data/2014-01-citibike-tripdata.csv')
class TestAnalysisPipeline(unittest.TestCase):
    def test_produce_summary_df(self):
        produce_summary_df(test_df, [DistinctCount, Len, DistinctPer], 'test_df')


    def test_pipeline_base(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        #just verify that there are no errors
        ap.produce_summary_dataframe(df)

    def test_add_aobj(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        class Foo(ColAnalysis):
            provided_summary = [
                'foo',]
            requires_summary = ['length']

            @staticmethod
            def summary(sampled_ser, summary_ser, ser):
                return dict(foo=8)
        ap.add_analysis(Foo)
        sdf = ap.produce_summary_dataframe(df)
        self.assertEqual(sdf.loc['foo']['tripduration'], 8)

    def test_replace_aobj(self):
        ap = AnalsysisPipeline([TypingStats, DefaultSummaryStats])
        class Foo(ColAnalysis):
            provided_summary = [
                'foo',]
            requires_summary = ['length']

            @staticmethod
            def summary(sampled_ser, summary_ser, ser):
                return dict(foo=8)
        ap.add_analysis(Foo)
        sdf = ap.produce_summary_dataframe(df)
        self.assertEqual(sdf.loc['foo']['tripduration'], 8)
        #15 facts returned about tripduration
        self.assertEqual(len(sdf['tripduration']), 15)
        #Create an updated Foo that returns 9
        class Foo(ColAnalysis):
            provided_summary = [
                'foo',]
            requires_summary = ['length']

            @staticmethod
            def summary(sampled_ser, summary_ser, ser):
                return dict(foo=9)
        ap.add_analysis(Foo)
        sdf2 = ap.produce_summary_dataframe(df)
        self.assertEqual(sdf2.loc['foo']['tripduration'], 9)
        #still 15 facts returned about tripduration
        self.assertEqual(len(sdf2['tripduration']), 15)
        #Create an updated Foo that returns 9
        
        
import pandas as pd
from buckaroo.buckaroo_widget import BuckarooWidget


def test_basic_instantiation():
    df = pd.read_csv('./examples/data/2014-01-citibike-tripdata.csv')
    w = BuckarooWidget(df)
    assert w.dfConfig['totalRows'] == 499


"""
to run the tests as regular python functions use the following code.
This will be useful for live testing adding analysis funcs

loader = unittest.TestLoader()
suite  = unittest.TestSuite()
tests = loader.loadTestsFromTestCase(TestOrderAnalysis)
suite.addTests(tests)
ab = unittest.TextTestRunner(verbosity=3).run(suite)
"""
