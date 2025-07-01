# state:READONLY
"""
🎯 ULTRA-MINIMAL REPRODUCTION of the citibike_df polars mode() failure.

ERROR: .rename_alias(selector.mode()): Series length 4 doesn't match the DataFrame height of 10

🔍 ROOT CAUSE IDENTIFIED:
The issue occurs when columns are renamed to a,b,c,d,e AND there is an interaction between:
1. select_clauses that include mode()
2. computed_summary classes present in the analysis pipeline

🎯 MINIMAL FAILING COMBINATION (just 4 analysis classes):
✅ PASS: Mode + ValueCounts + BasicStats (3 classes)
❌ FAIL: Mode + ValueCounts + BasicStats + Computed (4 classes)

The computed_summary class doesn't even need to depend on the mode() result - 
its mere presence causes the polars select_clauses execution to fail.

This is NOT about the mode() operation itself, but about how polars handles
multiple select_clauses when computed_summary classes are in the pipeline.

ORIGINAL FINDINGS: The error occurred with ALL 5 core analysis classes:
- VCAnalysis, BasicAnalysis, PlTyping, ComputedDefaultSummaryStats, HistogramAnalysis

IMPROVED FINDINGS: Reduced to just 4 minimal analysis classes that reproduce the exact same error.
"""

import polars as pl
import polars.selectors as cs
from polars import functions as F
from buckaroo.polars_buckaroo import PolarsBuckarooInfiniteWidget
from buckaroo.pluggable_analysis_framework.polars_analysis_management import PolarsAnalysis
from buckaroo.pluggable_analysis_framework.utils import json_postfix
from buckaroo.customizations.styling import DefaultSummaryStatsStyling, DefaultMainStyling


# Create test data that reproduces the issue
def get_test_data():
    return pl.DataFrame({
        'tripduration': [558, 501, 116, 1151, 819, 330, 720, 480, 900, 650],
        'start_station_name': [
            'W 22 St & 8 Ave', 'E 25 St & 1 Ave', 'Canal St & Rutgers St',
            'LaGuardia Pl & W 3 St', 'E 9 St & Avenue C', 'Allen St & Hester St',
            'W 22 St & 8 Ave', 'E 25 St & 1 Ave', 'Canal St & Rutgers St',
            'LaGuardia Pl & W 3 St'
        ],
        'usertype': [
            'Subscriber', 'Subscriber', 'Subscriber', 'Subscriber', 'Subscriber',
            'Customer', 'Customer', 'Subscriber', 'Customer', 'Subscriber'
        ],
        'birth_year': [1983.0, 1983.0, 1988.0, 1987.0, 1986.0, 1990.0, 1992.0, 1985.0, 1989.0, 1984.0],
        'gender': [1, 1, 1, 1, 2, 1, 2, 1, 2, 1]
    })


# 🎯 ULTRA-MINIMAL ANALYSIS CLASSES THAT REPRODUCE THE BUG

PROBABLY_STRUCTS = (~cs.numeric() & ~cs.string() & ~cs.temporal() & ~cs.boolean())
NOT_STRUCTS = (~PROBABLY_STRUCTS)

class MinimalModeAnalysis(PolarsAnalysis):
    """MINIMAL: Just the problematic mode() select clause"""
    provides_defaults = {'most_freq': 0}
    select_clauses = [
        NOT_STRUCTS.mode().name.map(json_postfix('most_freq')),
    ]

class MinimalValueCountsAnalysis(PolarsAnalysis):
    """MINIMAL: Just value_counts select clause (might interact with mode)"""
    provides_defaults = dict(
        value_counts=pl.Series("", [{'a': 'error', 'count': 1}], 
                              dtype=pl.Struct({'a': pl.String, 'count': pl.UInt32})))
    select_clauses = [
        NOT_STRUCTS.exclude("count").value_counts(sort=True)
        .implode().name.map(json_postfix('value_counts')),
    ]

class MinimalBasicStatsAnalysis(PolarsAnalysis):
    """MINIMAL: Basic stats that might interact with mode"""
    provides_defaults = {'length': 0, 'null_count': 0, 'mean': 0}
    select_clauses = [
        F.all().len().name.map(json_postfix('length')),
        F.all().null_count().name.map(json_postfix('null_count')),
        NOT_STRUCTS.mean().name.map(json_postfix('mean')),
    ]

class MinimalComputedAnalysis(PolarsAnalysis):
    """MINIMAL: Simple computed_summary that depends on select_clauses results"""
    requires_summary = ['length', 'null_count']
    provides_defaults = dict(null_per=0)

    @staticmethod
    def computed_summary(summary_dict):
        len_ = summary_dict['length']
        null_count = summary_dict.get('null_count', 0)
        return dict(null_per=null_count/len_ if len_ > 0 else 0)


# 🎯 ULTRA-MINIMAL TEST WIDGETS

class WorkingWidget(PolarsBuckarooInfiniteWidget):
    """✅ WORKING: 3 analysis classes with select_clauses only"""
    analysis_klasses = [
        MinimalModeAnalysis,
        MinimalValueCountsAnalysis,
        MinimalBasicStatsAnalysis
    ]

class FailingWidget(PolarsBuckarooInfiniteWidget):
    """❌ FAILING: 4 analysis classes - adding computed_summary breaks mode()"""
    analysis_klasses = [
        MinimalModeAnalysis,
        MinimalValueCountsAnalysis,
        MinimalBasicStatsAnalysis,
        MinimalComputedAnalysis
    ]


# ULTRA-MINIMAL TEST WIDGETS (NO STYLING TO AVOID DEPENDENCIES)

class UltraMinimalWidget(PolarsBuckarooInfiniteWidget):
    """Ultra minimal: Just mode() clause alone"""
    analysis_klasses = [MinimalModeAnalysis]

class TwoClassMinimalWidget(PolarsBuckarooInfiniteWidget):
    """Minimal: Mode + ValueCounts only"""
    analysis_klasses = [MinimalModeAnalysis, MinimalValueCountsAnalysis]

class ThreeClassMinimalWidget(PolarsBuckarooInfiniteWidget):
    """Minimal: Mode + ValueCounts + BasicStats"""
    analysis_klasses = [
        MinimalModeAnalysis,
        MinimalValueCountsAnalysis,
        MinimalBasicStatsAnalysis
    ]

class FourClassMinimalWidget(PolarsBuckarooInfiniteWidget):
    """Minimal: Mode + ValueCounts + BasicStats + Computed"""
    analysis_klasses = [
        MinimalModeAnalysis,
        MinimalValueCountsAnalysis,
        MinimalBasicStatsAnalysis,
        MinimalComputedAnalysis
    ]


# PROGRESSIVE TEST WIDGETS TO ISOLATE THE PROBLEM

class TwoClassWidget(PolarsBuckarooInfiniteWidget):
    """Test: Mode + ValueCounts only"""
    analysis_klasses = [
        MinimalModeAnalysis,
        MinimalValueCountsAnalysis,
        DefaultSummaryStatsStyling, 
        DefaultMainStyling
    ]

class ThreeClassWidget(PolarsBuckarooInfiniteWidget):
    """Test: Mode + ValueCounts + BasicStats"""
    analysis_klasses = [
        MinimalModeAnalysis,
        MinimalValueCountsAnalysis,
        MinimalBasicStatsAnalysis,
        DefaultSummaryStatsStyling, 
        DefaultMainStyling
    ]

class FourClassWidget(PolarsBuckarooInfiniteWidget):
    """Test: Mode + ValueCounts + BasicStats + Computed"""
    analysis_klasses = [
        MinimalModeAnalysis,
        MinimalValueCountsAnalysis,
        MinimalBasicStatsAnalysis,
        MinimalComputedAnalysis,
        DefaultSummaryStatsStyling, 
        DefaultMainStyling
    ]

class ModeOnlyWidget(PolarsBuckarooInfiniteWidget):
    """Test: Just the mode clause by itself"""
    analysis_klasses = [
        MinimalModeAnalysis,
        DefaultSummaryStatsStyling, 
        DefaultMainStyling
    ]


# 🎯 KEY TESTS - DEMONSTRATES THE EXACT TIPPING POINT

def test_working_combination():
    """✅ WORKING: 3 analysis classes - should PASS"""
    minimal_df = get_test_data()
    widget = WorkingWidget(minimal_df, debug=True)

def test_failing_combination():
    """❌ FAILING: 4 analysis classes - should FAIL with mode() error"""
    minimal_df = get_test_data()
    widget = FailingWidget(minimal_df, debug=True)


# ORIGINAL TESTS
def test_citibike_minimal_failure():
    """Original test that reproduces the citibike polars mode() error."""
    minimal_df = get_test_data()
    widget = PolarsBuckarooInfiniteWidget(minimal_df, debug=True)


# ULTRA-MINIMAL TESTS (NO STYLING DEPENDENCIES)
def test_ultra_minimal():
    """Ultra minimal: Just mode() clause, no styling"""
    minimal_df = get_test_data()
    widget = UltraMinimalWidget(minimal_df, debug=True)

def test_two_classes_minimal():
    """Minimal: Mode + ValueCounts, no styling"""
    minimal_df = get_test_data()
    widget = TwoClassMinimalWidget(minimal_df, debug=True)

def test_three_classes_minimal():
    """Minimal: Mode + ValueCounts + BasicStats, no styling"""
    minimal_df = get_test_data()
    widget = ThreeClassMinimalWidget(minimal_df, debug=True)

def test_four_classes_minimal():
    """Minimal: Mode + ValueCounts + BasicStats + Computed, no styling"""
    minimal_df = get_test_data()
    widget = FourClassMinimalWidget(minimal_df, debug=True)


# NEW MINIMAL TESTS TO ISOLATE THE PROBLEM
def test_mode_only():
    """Test: Just the mode() clause alone"""
    minimal_df = get_test_data()
    widget = ModeOnlyWidget(minimal_df, debug=True)

def test_two_classes():
    """Test: Mode + ValueCounts"""
    minimal_df = get_test_data()
    widget = TwoClassWidget(minimal_df, debug=True)

def test_three_classes():
    """Test: Mode + ValueCounts + BasicStats"""
    minimal_df = get_test_data()
    widget = ThreeClassWidget(minimal_df, debug=True)

def test_four_classes():
    """Test: Mode + ValueCounts + BasicStats + Computed"""
    minimal_df = get_test_data()
    widget = FourClassWidget(minimal_df, debug=True) 