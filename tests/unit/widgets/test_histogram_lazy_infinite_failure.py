"""
Tests to capture histogram computation failures in LazyInfinitePolarsBuckarooWidget.

The issue: Histograms return empty arrays in LazyInfinitePolarsBuckarooWidget
but work correctly in regular PolarsBuckarooWidget.

This test suite narrows down the problem through the execution stack:
1. Regular PolarsBuckarooWidget (should work)
2. LazyInfinitePolarsBuckarooWidget (should fail)
3. PAFColumnExecutor directly
4. ColumnExecutorDataflow
5. MultiprocessingExecutor
"""
import polars as pl
import numpy as np
from buckaroo.polars_buckaroo import PolarsBuckarooWidget
from buckaroo.lazy_infinite_polars_widget import LazyInfinitePolarsBuckarooWidget
from buckaroo.customizations.polars_analysis import HistogramAnalysis, PL_Analysis_Klasses
from buckaroo.file_cache.paf_column_executor import PAFColumnExecutor
from buckaroo.dataflow.column_executor_dataflow import ColumnExecutorDataflow
from buckaroo.file_cache.base import Executor, FileCache, ProgressNotification
from buckaroo.file_cache.multiprocessing_executor import MultiprocessingExecutor
from buckaroo.pluggable_analysis_framework.polars_analysis_management import PolarsAnalysis


def create_test_df_with_numeric_histogram():
    """Create a DataFrame with numeric columns that should produce histograms."""
    return pl.DataFrame({
        'numeric_col': [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0] * 10,
        'categorical_col': ['a', 'b', 'c'] * 33 + ['a'],
    })


def test_regular_polars_buckaroo_histogram_success():
    """
    Test that regular PolarsBuckarooWidget correctly computes histograms.
    This should work and produce non-empty histogram arrays.
    """
    df = create_test_df_with_numeric_histogram()
    widget = PolarsBuckarooWidget(df)
    
    # Wait a bit for computation (if async)
    import time
    time.sleep(0.5)
    
    merged_sd = widget.dataflow.merged_sd
    
    # Check that histogram data exists and is non-empty
    numeric_col_key = None
    for key, value in merged_sd.items():
        if isinstance(value, dict) and value.get('orig_col_name') == 'numeric_col':
            numeric_col_key = key
            break
    
    assert numeric_col_key is not None, "numeric_col should be in merged_sd"
    
    numeric_stats = merged_sd[numeric_col_key]
    
    # Histogram should be computed (non-empty list)
    assert 'histogram' in numeric_stats, "histogram should be in stats"
    histogram = numeric_stats['histogram']
    assert isinstance(histogram, list), "histogram should be a list"
    assert len(histogram) > 0, f"histogram should be non-empty, got: {histogram}"
    
    # Histogram bins should exist
    assert 'histogram_bins' in numeric_stats, "histogram_bins should be in stats"
    histogram_bins = numeric_stats['histogram_bins']
    assert histogram_bins != ['faked'], "histogram_bins should not be the default 'faked' value"
    
    # Categorical histogram should also exist (even for numeric, as fallback)
    assert 'categorical_histogram' in numeric_stats, "categorical_histogram should be in stats"


def test_lazy_infinite_polars_buckaroo_histogram_failure():
    """
    Test that LazyInfinitePolarsBuckarooWidget fails to compute histograms correctly.
    This should produce empty histogram arrays (the bug we're trying to fix).
    """
    df = create_test_df_with_numeric_histogram()
    ldf = df.lazy()
    
    widget = LazyInfinitePolarsBuckarooWidget(ldf)
    
    # Wait for computation
    import time
    time.sleep(2.0)  # May need more time for async execution
    
    merged_sd = widget._df.merged_sd or {}
    
    # Find the numeric column in merged_sd
    numeric_col_key = None
    for key, value in merged_sd.items():
        if isinstance(value, dict) and value.get('orig_col_name') == 'numeric_col':
            numeric_col_key = key
            break
    
    assert numeric_col_key is not None, "numeric_col should be in merged_sd"
    
    numeric_stats = merged_sd[numeric_col_key]
    
    # The bug: histogram arrays are empty
    assert 'histogram' in numeric_stats, "histogram key should exist"
    histogram = numeric_stats['histogram']
    
    # This is the failure mode: empty arrays
    if isinstance(histogram, list) and len(histogram) == 0:
        # This is the bug - histograms are empty
        assert False, (
            f"BUG CONFIRMED: histogram is empty array. "
            f"Full stats: {numeric_stats}. "
            f"This should contain histogram data like in regular PolarsBuckarooWidget."
        )
    
    # If we get here, the bug might be fixed or the test needs adjustment
    assert len(histogram) > 0, f"histogram should be non-empty, got: {histogram}"


def test_paf_column_executor_histogram_failure():
    """
    Test PAFColumnExecutor directly to see if it's missing histogram_args.
    This narrows down whether the issue is in the column executor.
    """
    df = create_test_df_with_numeric_histogram()
    ldf = df.lazy()
    
    executor = PAFColumnExecutor(PL_Analysis_Klasses)
    
    # Get execution args for the numeric column
    existing_stats = {'numeric_col': {}}
    exec_args = executor.get_execution_args(existing_stats)
    
    # Execute
    results = executor.execute(ldf, exec_args)
    
    # Check results
    assert 'numeric_col' in results, "numeric_col should be in results"
    col_result = results['numeric_col']
    stats = col_result.result
    
    # The issue: histogram_args should be computed via column_ops, but may be missing
    assert 'histogram_args' in stats, (
        f"BUG: histogram_args missing from PAFColumnExecutor results. "
        f"Available keys: {list(stats.keys())}. "
        f"This suggests column_ops are not being executed."
    )
    
    histogram_args = stats.get('histogram_args')
    if histogram_args:
        # Should have the expected structure
        assert 'meat_histogram' in histogram_args, "histogram_args should have meat_histogram"
        assert 'normalized_populations' in histogram_args, "histogram_args should have normalized_populations"


def test_column_executor_dataflow_histogram_failure():
    """
    Test ColumnExecutorDataflow to see if histogram computation fails at this level.
    """
    df = create_test_df_with_numeric_histogram()
    ldf = df.lazy()
    
    dataflow = ColumnExecutorDataflow(ldf, analysis_klasses=PL_Analysis_Klasses)
    
    # Collect results via listener
    collected_results = {}
    
    def listener(note: ProgressNotification):
        if note.success and note.result:
            for col, col_result in note.result.items():
                if col not in collected_results:
                    collected_results[col] = {}
                collected_results[col].update(col_result.result or {})
    
    dataflow.compute_summary_with_executor(progress_listener=listener)
    
    # Check results
    assert 'numeric_col' in collected_results, "numeric_col should be in results"
    stats = collected_results['numeric_col']
    
    # Check if histogram_args is missing
    if 'histogram_args' not in stats:
        assert False, (
            f"BUG: histogram_args missing from ColumnExecutorDataflow results. "
            f"Available keys: {list(stats.keys())}. "
            f"This suggests column_ops execution is failing in the dataflow."
        )
    
    # Check merged_sd
    merged_sd = dataflow.merged_sd or {}
    numeric_col_key = None
    for key, value in merged_sd.items():
        if isinstance(value, dict) and value.get('orig_col_name') == 'numeric_col':
            numeric_col_key = key
            break
    
    if numeric_col_key:
        numeric_stats = merged_sd[numeric_col_key]
        histogram = numeric_stats.get('histogram', [])
        if isinstance(histogram, list) and len(histogram) == 0:
            assert False, (
                f"BUG: histogram is empty in merged_sd. "
                f"Full stats: {numeric_stats}"
            )


def test_multiprocessing_executor_histogram_failure():
    """
    Test MultiprocessingExecutor to see if the issue is specific to multiprocessing.
    """
    df = create_test_df_with_numeric_histogram()
    ldf = df.lazy()
    
    executor = PAFColumnExecutor(PL_Analysis_Klasses)
    fc = FileCache()
    
    collected_results = {}
    
    def listener(note: ProgressNotification):
        if note.success and note.result:
            for col, col_result in note.result.items():
                if col not in collected_results:
                    collected_results[col] = {}
                collected_results[col].update(col_result.result or {})
    
    mp_executor = MultiprocessingExecutor(
        ldf, executor, listener, fc, timeout_secs=30.0, async_mode=False
    )
    mp_executor.run()
    
    # Check results
    assert 'numeric_col' in collected_results, "numeric_col should be in results"
    stats = collected_results['numeric_col']
    
    # Check if histogram_args is missing
    if 'histogram_args' not in stats:
        assert False, (
            f"BUG: histogram_args missing from MultiprocessingExecutor results. "
            f"Available keys: {list(stats.keys())}. "
            f"This suggests column_ops are not being executed in multiprocessing context."
        )


def test_column_ops_general_failure():
    """
    Test that demonstrates the type of failure (missing column_ops results)
    but not attached to histogram analysis specifically.
    
    This uses a simple custom analysis with column_ops to show the general pattern.
    """
    from buckaroo.pluggable_analysis_framework.polars_utils import NUMERIC_POLARS_DTYPES
    
    class ColumnOpsAnalysis(PolarsAnalysis):
        """Simple analysis that uses column_ops to compute a custom metric."""
        provides_defaults = {'custom_metric': None}
        column_ops = {
            'custom_metric': (
                NUMERIC_POLARS_DTYPES,
                lambda ser: {'sum': float(ser.sum()), 'mean': float(ser.mean())}
            )
        }
    
    df = pl.DataFrame({
        'numeric_col': [1.0, 2.0, 3.0, 4.0, 5.0],
        'string_col': ['a', 'b', 'c', 'd', 'e'],
    })
    ldf = df.lazy()
    
    executor = PAFColumnExecutor([ColumnOpsAnalysis])
    existing_stats = {'numeric_col': {}}
    exec_args = executor.get_execution_args(existing_stats)
    results = executor.execute(ldf, exec_args)
    
    # Check if custom_metric was computed
    assert 'numeric_col' in results, "numeric_col should be in results"
    stats = results['numeric_col'].result
    
    if 'custom_metric' not in stats:
        assert False, (
            f"BUG DEMONSTRATED: column_ops result 'custom_metric' is missing. "
            f"Available keys: {list(stats.keys())}. "
            f"This shows the general pattern: column_ops are not being executed. "
            f"Same issue affects histogram_args in HistogramAnalysis."
        )
    
    # If present, verify it has the expected structure
    custom_metric = stats.get('custom_metric')
    if custom_metric:
        assert 'sum' in custom_metric, "custom_metric should have 'sum'"
        assert 'mean' in custom_metric, "custom_metric should have 'mean'"
