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
from buckaroo.pluggable_analysis_framework.polars_analysis_management import (
    PolarsAnalysis, polars_produce_series_df, PlDfStats, PolarsAnalysisPipeline
)
from buckaroo.pluggable_analysis_framework.analysis_management import produce_summary_df
from buckaroo.pluggable_analysis_framework.utils import json_postfix
from buckaroo.customizations.styling import DefaultSummaryStatsStyling, DefaultMainStyling
import pandas as pd
import numpy as np


# Create test data that reproduces the issue
def get_test_data():
    """Create minimal test data that reproduces the polars mode() error"""
    return pl.DataFrame({
        'tripduration': [400, 500, 600, 400],  # Repeated values for mode
        'start_station_name': ['W 3 St', 'E 5 St', 'W 3 St', 'E 5 St'],
        'usertype': ['Subscriber', 'Customer', 'Subscriber', 'Subscriber'], 
        'birth_year': [1990.0, 1985.0, 1990.0, 1995.0],
        'gender': [1, 2, 1, 1]
    }).with_row_count().head(10)  # Extend to 10 rows to match error


# 🎯 ULTRA-MINIMAL ANALYSIS CLASSES THAT REPRODUCE THE BUG

PROBABLY_STRUCTS = (~cs.numeric() & ~cs.string() & ~cs.temporal() & ~cs.boolean())
NOT_STRUCTS = (~PROBABLY_STRUCTS)

class MinimalModeAnalysis(PolarsAnalysis):
    """MINIMAL: Just the problematic mode() select clause"""
    provides_defaults = {'most_freq': 'NotComputed'}
    select_clauses = [
        NOT_STRUCTS.mode().name.map(json_postfix('most_freq')),
    ]
    @staticmethod
    def computed_summary(summary_dict):
        return {}

class MinimalValueCountsAnalysis(PolarsAnalysis):
    """MINIMAL: Just value_counts select clause (might interact with mode)"""
    provides_defaults = {'value_counts': 'NotComputed'}
    select_clauses = [
        cs.exclude(["count"]).value_counts(sort=True, parallel=False).head(7)
        .implode().name.map(json_postfix('value_counts')),
    ]
    @staticmethod
    def computed_summary(summary_dict):
        return {}

class MinimalBasicStatsAnalysis(PolarsAnalysis):
    """MINIMAL: Basic stats that might interact with mode"""
    provides_defaults = {'length': 'NotComputed', 'null_count': 'NotComputed', 'mean': 'NotComputed'}
    select_clauses = [
        F.all().len().name.map(json_postfix('length')),
        F.all().null_count().name.map(json_postfix('null_count')),
        NOT_STRUCTS.mean().name.map(json_postfix('mean')),
    ]
    @staticmethod
    def computed_summary(summary_dict):
        return {}

class MinimalComputedAnalysis(PolarsAnalysis):
    """MINIMAL: Simple computed_summary that depends on select_clauses results"""
    provides_defaults = {'derived_stat': 'NotComputed'}
    requires_summary = ['length', 'null_count']
    select_clauses = []  # No select clauses - pure computed
    
    @staticmethod
    def computed_summary(summary_dict):
        try:
            len_ = summary_dict['length']
            null_count = summary_dict['null_count']
            return {'derived_stat': len_ - null_count}
        except KeyError as e:
            print(f"DEBUG: Error in MinimalComputedAnalysis.computed_summary: {e}")
            print(f"DEBUG: Missing keys that MinimalComputedAnalysis expects:")
            for req_key in MinimalComputedAnalysis.requires_summary:
                if req_key not in summary_dict:
                    print(f"  - {req_key}")
            raise e


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
    widget = FailingWidget(minimal_df, debug=True)


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


# Test functions for direct analysis pipeline calls
def test_direct_polars_produce_series_df():
    """Test polars_produce_series_df directly without widgets"""
    df = get_test_data()
    
    # Test with just mode analysis - should work
    mode_classes = [MinimalModeAnalysis]
    result_dict, errs = polars_produce_series_df(df, mode_classes, debug=True)
    print(f"Mode only - Result keys: {list(result_dict.keys())}")
    print(f"Mode only - Errors: {errs}")
    assert len(errs) == 0, f"Expected no errors, got: {errs}"
    
    # Test with all 4 classes - the combination that fails
    all_classes = [MinimalModeAnalysis, MinimalValueCountsAnalysis, MinimalBasicStatsAnalysis, MinimalComputedAnalysis]
    result_dict, errs = polars_produce_series_df(df, all_classes, debug=True)
    print(f"All 4 classes - Result keys: {list(result_dict.keys())}")
    print(f"All 4 classes - Errors: {errs}")


def test_direct_produce_summary_df():
    """Test produce_summary_df directly with polars data"""
    df = get_test_data()
    
    # First get series results
    all_classes = [MinimalModeAnalysis, MinimalValueCountsAnalysis, MinimalBasicStatsAnalysis, MinimalComputedAnalysis]
    series_dict, series_errs = polars_produce_series_df(df, all_classes, debug=True)
    
    print(f"Series dict keys: {list(series_dict.keys())}")
    for key, value in series_dict.items():
        print(f"  {key}: {type(value)} - {value}")
    
    # Now test produce_summary_df
    summary_dict, summary_errs = produce_summary_df(df.to_pandas(), series_dict, all_classes, debug=True)
    print(f"Summary dict keys: {list(summary_dict.keys())}")
    print(f"Summary errors: {summary_errs}")


def test_polars_pipeline_direct():
    """Test PolarsAnalysisPipeline.full_produce_summary_df directly"""
    df = get_test_data()
    
    # Test working combination 
    working_classes = [MinimalModeAnalysis, MinimalValueCountsAnalysis, MinimalBasicStatsAnalysis]
    result_dict, errs = PolarsAnalysisPipeline.full_produce_summary_df(df, working_classes, debug=True)
    print(f"Working combination - Result keys: {list(result_dict.keys())}")
    print(f"Working combination - Errors: {errs}")
    
    # Test failing combination
    failing_classes = [MinimalModeAnalysis, MinimalValueCountsAnalysis, MinimalBasicStatsAnalysis, MinimalComputedAnalysis]
    result_dict, errs = PolarsAnalysisPipeline.full_produce_summary_df(df, failing_classes, debug=True)
    print(f"Failing combination - Result keys: {list(result_dict.keys())}")
    print(f"Failing combination - Errors: {errs}")


# Individual class testing for ultra-granular isolation
def test_individual_mode_clause():
    """Test just the mode clause in isolation"""
    df = get_test_data()
    mode_clause = NOT_STRUCTS.mode().name.map(json_postfix('most_freq'))
    
    # Test individual execution
    result = df.lazy().select(mode_clause).collect()
    print(f"Mode clause result shape: {result.shape}")
    print(f"Mode clause result columns: {result.columns}")
    print(f"Mode clause result: {result}")


def test_individual_clauses_combined():
    """Test combining individual clauses step by step"""
    df = get_test_data()
    
    clauses = [
        NOT_STRUCTS.mode().name.map(json_postfix('most_freq')),
        cs.exclude(["count"]).value_counts(sort=True, parallel=False).head(7).implode().name.map(json_postfix('value_counts')),
        F.all().len().name.map(json_postfix('length')),
        F.all().null_count().name.map(json_postfix('null_count')),
        NOT_STRUCTS.mean().name.map(json_postfix('mean')),
    ]
    
    # Test each clause individually 
    for i, clause in enumerate(clauses):
        try:
            result = df.lazy().select(clause).collect()
            print(f"Clause {i} works: {result.shape} columns")
        except Exception as e:
            print(f"Clause {i} fails: {e}")
    
    # Test combining them all
    try:
        result = df.lazy().select(clauses).collect()
        print(f"All clauses combined work: {result.shape}")
    except Exception as e:
        print(f"All clauses combined fail: {e}") 