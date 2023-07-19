import unittest
import pytest
import pandas as pd
from buckaroo.pluggable_analysis_framework import (
    ColAnalysis, order_analysis, check_solvable, NotProvidedException,
    produce_summary_df)


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

    def test_produce_summary_df(self):
        produce_summary_df(test_df, [DistinctCount, Len, DistinctPer], 'test_df')


"""
to run the tests as regular python functions use the following code.
This will be useful for live testing adding analysis funcs

loader = unittest.TestLoader()
suite  = unittest.TestSuite()
tests = loader.loadTestsFromTestCase(TestOrderAnalysis)
suite.addTests(tests)
ab = unittest.TextTestRunner(verbosity=3).run(suite)
"""
