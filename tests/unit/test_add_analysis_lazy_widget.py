#!/usr/bin/env python
# coding: utf-8
"""
Test for adding analyses to LazyInfinitePolarsBuckarooWidget.

This test verifies:
1. add_analysis adds a new analysis class
2. The executor recomputes stats after add_analysis
3. Pinned rows are updated correctly
4. Stats from polars expressions (select_clauses) are computed
5. Stats from computed_summary that depend on cached analyses are computed
"""

import polars as pl
import polars.selectors as cs

from buckaroo.lazy_infinite_polars_widget import LazyInfinitePolarsBuckarooWidget
from buckaroo.pluggable_analysis_framework.polars_analysis_management import PolarsAnalysis
from buckaroo.pluggable_analysis_framework.utils import json_postfix
from buckaroo.styling_helpers import obj_
from tests.unit.file_cache.executor_test_utils import wait_for_nested_executor_finish


class SumAnalysis(PolarsAnalysis):
    """
    Analysis that computes the sum of numeric columns.
    This uses a polars expression (select_clauses) that is executed.
    """
    provides_defaults = {'sum': 0}
    
    select_clauses = [
        cs.numeric().sum().name.map(json_postfix('sum')),
    ]


class MeanPerLengthAnalysis(PolarsAnalysis):
    """
    Analysis that computes mean per length (mean / length).
    This depends on 'mean' and 'length' from BasicAnalysis which should
    already be in the cache.
    """
    requires_summary = ['mean', 'length']
    provides_defaults = {'mean_per_length': 0.0}
    
    @staticmethod
    def computed_summary(summary_dict):
        """
        Compute mean_per_length using cached values from BasicAnalysis.
        This demonstrates how a computed field can depend on another analysis
        that has already been processed and is in the cache.
        """
        mean = summary_dict.get('mean', 0)
        length = summary_dict.get('length', 1)
        if length > 0:
            return {'mean_per_length': mean / length}
        return {'mean_per_length': 0.0}


def test_add_analysis_with_polars_expression():
    """
    Test adding an analysis with a polars expression (select_clauses).
    """
    # Create sample data
    df = pl.DataFrame({
        'age': [25, 30, 35, 40, 45] * 20,
        'score': [85.5, 92.0, 78.3, 88.7, 95.2] * 20,
        'weight': [60.0, 70.0, 80.0, 90.0, 100.0] * 20,
    })
    
    # Create widget
    ldf = df.lazy()
    widget = LazyInfinitePolarsBuckarooWidget(ldf)
    
    # Wait for initial computation
    wait_for_nested_executor_finish(widget, timeout_secs=10.0)
    
    # Verify initial state - 'sum' should not be present
    merged_sd = widget._df.merged_sd
    assert merged_sd is not None
    # Check one column to see if 'sum' is missing
    first_col = list(merged_sd.keys())[0]
    assert 'sum' not in merged_sd[first_col], "sum should not be present before adding SumAnalysis"
    
    # Add SumAnalysis
    widget.add_analysis(
        SumAnalysis,
        pinned_row_configs=[obj_('sum')]
    )
    
    # Wait for recomputation - use a longer timeout and check for sum specifically
    import time
    start_time = time.time()
    timeout = 15.0
    found_sum = False
    while time.time() - start_time < timeout:
        merged_sd_after = widget._df.merged_sd or {}
        # Check if 'sum' is present in any column
        for col_name, col_stats in merged_sd_after.items():
            if isinstance(col_stats, dict) and 'sum' in col_stats:
                found_sum = True
                break
        if found_sum:
            break
        time.sleep(0.1)
    
    assert found_sum, "sum should be present after adding SumAnalysis and recomputing"
    
    # Verify 'sum' is now present in merged_sd
    merged_sd_after = widget._df.merged_sd
    assert merged_sd_after is not None
    
    # Check that 'sum' is present for numeric columns
    for col_name, col_stats in merged_sd_after.items():
        if isinstance(col_stats, dict):
            orig_col = col_stats.get('orig_col_name', '')
            # age, score, weight are numeric and should have sum
            if orig_col in ['age', 'score', 'weight']:
                assert 'sum' in col_stats, f"sum should be present for {orig_col}"
                # Verify sum is a number (not the default 0)
                sum_val = col_stats.get('sum')
                assert isinstance(sum_val, (int, float)), f"sum should be numeric for {orig_col}"
                # For our test data, sums should be positive
                if orig_col == 'age':
                    assert sum_val > 0, f"age sum should be positive, got {sum_val}"
    
    # Verify pinned_rows includes 'sum'
    pinned_rows = widget.df_display_args['main']['df_viewer_config'].get('pinned_rows', [])
    pinned_keys = [pr.get('primary_key_val') for pr in pinned_rows if isinstance(pr, dict)]
    assert 'sum' in pinned_keys, "sum should be in pinned_rows"


def test_add_analysis_with_computed_field():
    """
    Test adding an analysis with a computed field that depends on cached analysis.
    """
    # Create sample data
    df = pl.DataFrame({
        'age': [25, 30, 35, 40, 45] * 20,
        'score': [85.5, 92.0, 78.3, 88.7, 95.2] * 20,
    })
    
    # Create widget
    ldf = df.lazy()
    widget = LazyInfinitePolarsBuckarooWidget(ldf)
    
    # Wait for initial computation (BasicAnalysis should compute 'mean' and 'length')
    wait_for_nested_executor_finish(widget, timeout_secs=10.0)
    
    # Verify initial state - 'mean_per_length' should not be present
    merged_sd = widget._df.merged_sd
    assert merged_sd is not None
    first_col = list(merged_sd.keys())[0]
    assert 'mean_per_length' not in merged_sd[first_col], "mean_per_length should not be present before adding MeanPerLengthAnalysis"
    
    # Verify 'mean' and 'length' are present (from BasicAnalysis)
    assert 'mean' in merged_sd[first_col], "mean should be present from BasicAnalysis"
    assert 'length' in merged_sd[first_col], "length should be present from BasicAnalysis"
    
    # Add MeanPerLengthAnalysis
    widget.add_analysis(
        MeanPerLengthAnalysis,
        pinned_row_configs=[obj_('mean_per_length')]
    )
    
    # Wait for recomputation - check for mean_per_length specifically
    import time
    start_time = time.time()
    timeout = 15.0
    found_mean_per_length = False
    while time.time() - start_time < timeout:
        merged_sd_after = widget._df.merged_sd or {}
        # Check if 'mean_per_length' is present in any column
        for col_name, col_stats in merged_sd_after.items():
            if isinstance(col_stats, dict) and 'mean_per_length' in col_stats:
                found_mean_per_length = True
                break
        if found_mean_per_length:
            break
        time.sleep(0.1)
    
    assert found_mean_per_length, "mean_per_length should be present after adding MeanPerLengthAnalysis and recomputing"
    
    # Verify 'mean_per_length' is now present
    merged_sd_after = widget._df.merged_sd
    assert merged_sd_after is not None
    
    for col_name, col_stats in merged_sd_after.items():
        if isinstance(col_stats, dict):
            orig_col = col_stats.get('orig_col_name', '')
            if orig_col in ['age', 'score']:
                assert 'mean_per_length' in col_stats, f"mean_per_length should be present for {orig_col}"
                mean_per_length = col_stats.get('mean_per_length')
                assert isinstance(mean_per_length, (int, float)), f"mean_per_length should be numeric for {orig_col}"
                # Verify it's computed correctly: mean_per_length = mean / length
                mean = col_stats.get('mean', 0)
                length = col_stats.get('length', 1)
                expected = mean / length if length > 0 else 0.0
                assert abs(mean_per_length - expected) < 0.001, \
                    f"mean_per_length should equal mean/length for {orig_col}: {mean_per_length} != {expected}"
    
    # Verify pinned_rows includes 'mean_per_length'
    pinned_rows = widget.df_display_args['main']['df_viewer_config'].get('pinned_rows', [])
    pinned_keys = [pr.get('primary_key_val') for pr in pinned_rows if isinstance(pr, dict)]
    assert 'mean_per_length' in pinned_keys, "mean_per_length should be in pinned_rows"


def test_add_multiple_analyses():
    """
    Test adding multiple analyses sequentially.
    """
    # Create sample data
    df = pl.DataFrame({
        'age': [25, 30, 35, 40, 45] * 20,
        'score': [85.5, 92.0, 78.3, 88.7, 95.2] * 20,
    })
    
    # Create widget
    ldf = df.lazy()
    widget = LazyInfinitePolarsBuckarooWidget(ldf)
    
    # Wait for initial computation
    wait_for_nested_executor_finish(widget, timeout_secs=10.0)
    
    # Add SumAnalysis
    widget.add_analysis(SumAnalysis, pinned_row_configs=[obj_('sum')])
    import time
    start_time = time.time()
    timeout = 15.0
    found_sum = False
    while time.time() - start_time < timeout:
        merged_sd = widget._df.merged_sd or {}
        for col_stats in merged_sd.values():
            if isinstance(col_stats, dict) and 'sum' in col_stats:
                found_sum = True
                break
        if found_sum:
            break
        time.sleep(0.1)
    assert found_sum, "sum should be present after adding SumAnalysis"
    
    # Add MeanPerLengthAnalysis
    widget.add_analysis(MeanPerLengthAnalysis, pinned_row_configs=[obj_('mean_per_length')])
    start_time = time.time()
    found_mean_per_length = False
    while time.time() - start_time < timeout:
        merged_sd = widget._df.merged_sd or {}
        for col_stats in merged_sd.values():
            if isinstance(col_stats, dict) and 'mean_per_length' in col_stats:
                found_mean_per_length = True
                break
        if found_mean_per_length:
            break
        time.sleep(0.1)
    assert found_mean_per_length, "mean_per_length should be present after adding MeanPerLengthAnalysis"
    
    # Verify both stats are present
    merged_sd = widget._df.merged_sd
    assert merged_sd is not None
    
    first_col = list(merged_sd.keys())[0]
    col_stats = merged_sd[first_col]
    assert 'sum' in col_stats, "sum should be present after adding SumAnalysis"
    assert 'mean_per_length' in col_stats, "mean_per_length should be present after adding MeanPerLengthAnalysis"
    
    # Verify both are in pinned_rows
    pinned_rows = widget.df_display_args['main']['df_viewer_config'].get('pinned_rows', [])
    pinned_keys = [pr.get('primary_key_val') for pr in pinned_rows if isinstance(pr, dict)]
    assert 'sum' in pinned_keys, "sum should be in pinned_rows"
    assert 'mean_per_length' in pinned_keys, "mean_per_length should be in pinned_rows"

