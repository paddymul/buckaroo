import os
import polars as pl
from polars import functions as F

import buckaroo.file_cache.cache_utils as cache_utils_module
from buckaroo.file_cache.base import Executor, FileCache, ProgressNotification
from buckaroo.file_cache.cache_utils import clear_file_cache, get_global_file_cache
from buckaroo.dataflow.styling_core import merge_sds
from buckaroo.file_cache.paf_column_executor import PAFColumnExecutor
from buckaroo.pluggable_analysis_framework.polars_analysis_management import PolarsAnalysis
from buckaroo.pluggable_analysis_framework.utils import json_postfix
from tests.unit.file_cache.executor_test_utils import (
    assert_stats_present,
    build_existing_cached,
    create_listener,
    extract_results,
    get_cached_merged_sd,
)


class SelectOnlyAnalysis(PolarsAnalysis):
    provides_defaults = {'null_count':0}
    select_clauses = [
        F.all().null_count().name.map(json_postfix('null_count')),
        F.all().mean().name.map(json_postfix('mean')),
    ]


def test_paf_column_executor_basic():
    df = pl.DataFrame({'a1': [1,2,3], 'b2': [10, None, 30]})
    ldf = df.lazy()
    fc = FileCache()
    collected: list[ProgressNotification] = []
    def listener(p:ProgressNotification) -> None:
        collected.append(p)

    exec_ = PAFColumnExecutor([SelectOnlyAnalysis])
    ex = Executor(ldf, exec_, listener, fc)
    ex.run()

    # Should have produced two notifications and cached per-series results
    assert len(collected) == 2

    # Validate we got notifications per column (success or failure)
    assert all(p.col_group in [['a1'], ['b2']] for p in collected)


class ComputedOnlyAnalysis(PolarsAnalysis):
    """
    Minimal analysis that only provides a default and a computed_summary
    value, with no select_clauses or column_ops. This is used to verify
    that PAFColumnExecutor (via polars_series_stats_from_select_result)
    actually invokes computed_summary for each column.
    """

    provides_defaults = {'foo': 0}
    select_clauses: list[pl.Expr] = []

    @staticmethod
    def computed_summary(summary_dict):
        # Increment foo to a non-default value so we can assert it was called.
        return {'foo': summary_dict.get('foo', 0) + 1}


def test_paf_column_executor_runs_computed_summary():
    """
    Ensure that PAFColumnExecutor results include values produced by
    computed_summary, not just raw select_clauses/column_ops output.
    """
    df = pl.DataFrame({'a1': [1, 2, 3], 'b2': [10, 20, 30]})
    ldf = df.lazy()
    fc = FileCache()
    collected: list[ProgressNotification] = []

    def listener(p: ProgressNotification) -> None:
        collected.append(p)

    exec_ = PAFColumnExecutor([ComputedOnlyAnalysis])
    ex = Executor(ldf, exec_, listener, fc)
    ex.run()

    # One notification per column, and each should contain ColumnResults
    assert len(collected) == 2
    for note in collected:
        assert note.success
        assert isinstance(note.result, dict)
        # Each ColumnResult.result should contain foo==1 (default 0 + 1)
        for col, col_result in note.result.items():
            assert col in ('a1', 'b2')
            assert col_result.result.get('foo') == 1


# Analysis classes that produce unique stat keys to track execution
class AnalysisA(PolarsAnalysis):
    """Analysis A produces a unique stat key 'analysis_a_stat'"""
    provides_defaults = {}
    select_clauses = [
        F.all().mean().name.map(json_postfix('analysis_a_stat')),
    ]


class AnalysisB(PolarsAnalysis):
    """Analysis B produces a unique stat key 'analysis_b_stat'"""
    provides_defaults = {}
    select_clauses = [
        F.all().sum().name.map(json_postfix('analysis_b_stat')),
    ]


class AnalysisC(PolarsAnalysis):
    """Analysis C produces a unique stat key 'analysis_c_stat'"""
    provides_defaults = {}
    select_clauses = [
        F.all().min().name.map(json_postfix('analysis_c_stat')),
    ]


class AnalysisD(PolarsAnalysis):
    """Analysis D produces a unique stat key 'analysis_d_stat'"""
    provides_defaults = {}
    select_clauses = [
        F.all().max().name.map(json_postfix('analysis_d_stat')),
    ]


def test_paf_column_executor_with_different_analysis_sets(tmp_path):
    """
    Test caching behavior when running PAFColumnExecutor with different analysis sets.
    
    Scenario:
    1. Run with analyses a,b,c through an executor, verify the results
    2. Run with analyses b,c,d - verify that only d is run, and b and c are not run,
       but that the results are available
    3. Run a,b,c again - verify that no analysis is run
    
    Expected behavior based on codebase:
    - Second run (b,c,d): should return a,b,c,d (all cached from run 1 + newly computed d)
    - Third run (a,b,c): should return a,b,c,d (all cached from previous runs)
    """
    # Set up isolated cache
    cache_utils_module._file_cache = None
    cache_utils_module._executor_log = None
    
    original_home = os.environ.get('HOME')
    os.environ['HOME'] = str(tmp_path)
    
    try:
        # Create test data
        df = pl.DataFrame({'test_col': [1, 2, 3, 4, 5]})
        test_file = tmp_path / "test_data.csv"
        df.write_csv(test_file)
        
        fc = get_global_file_cache()
        clear_file_cache()
        ldf = df.lazy()
        test_column = 'test_col'
        orig_to_rw_map = {test_column: test_column}
        
        # STEP 1: Run with analyses a,b,c
        collected1 = []
        exec1 = PAFColumnExecutor([AnalysisA, AnalysisB, AnalysisC])
        ex1 = Executor(ldf, exec1, create_listener(collected1), fc, file_path=test_file)
        ex1.run()
        
        results_1 = extract_results(collected1)
        assert len(results_1) > 0, "Run 1 should produce results"
        assert_stats_present(results_1, test_column, 
                           ['analysis_a_stat', 'analysis_b_stat', 'analysis_c_stat'],
                           ['analysis_d_stat'])
        
        # Build and save merged_sd from run 1 (simulating ColumnExecutorDataflow)
        aggregated_summary_1 = {}
        for note in collected1:
            if note.success and note.result:
                for orig_col, col_res in note.result.items():
                    stats = col_res.result or {}
                    rw = orig_to_rw_map.get(orig_col, orig_col)
                    entry = aggregated_summary_1.get(rw)
                    if entry is None:
                        entry = {'orig_col_name': orig_col, 'rewritten_col_name': rw}
                        aggregated_summary_1[rw] = entry
                    entry.update(stats)
        
        # Save merged_sd to cache (simulating what ColumnExecutorDataflow does)
        if aggregated_summary_1:
            merged_sd_1 = merge_sds({}, aggregated_summary_1, {})
            fc.upsert_file_metadata(test_file, {'merged_sd': merged_sd_1})
        
        # STEP 2: Run with analyses b,c,d
        cached_merged_sd_2 = get_cached_merged_sd(fc, test_file)
        existing_cached = build_existing_cached(fc, test_file, [test_column])
        
        exec2 = PAFColumnExecutor(
            [AnalysisB, AnalysisC, AnalysisD],
            cached_merged_sd=cached_merged_sd_2,
            orig_to_rw_map=orig_to_rw_map
        )
        
        # Check which columns will be executed
        exec_args_2 = exec2.get_execution_args(existing_cached)
        columns_to_execute_2 = exec_args_2.columns
        
        # Verify that test_column should be executed because analysis_d_stat doesn't exist in cache
        rw_col = orig_to_rw_map.get(test_column, test_column)
        cached_stats_2 = cached_merged_sd_2.get(rw_col, {})
        assert 'analysis_d_stat' not in cached_stats_2, "analysis_d_stat should not exist in cache before run 2"
        
        # Since analysis_d_stat doesn't exist, the column should be executed
        # (even though it has stats for a,b,c, it doesn't have stats for d)
        assert test_column in columns_to_execute_2, f"test_column should be in columns_to_execute because analysis_d_stat is not cached. Got: {columns_to_execute_2}"
        assert not exec_args_2.no_exec, "no_exec should be False because analysis_d_stat needs to be computed"
        
        collected2 = []
        ex2 = Executor(ldf, exec2, create_listener(collected2), fc, file_path=test_file)
        ex2.run()
        
        # Verify that analysis_d_stat was executed (should be in notifications)
        results_2 = extract_results(collected2)
        assert 'analysis_d_stat' in results_2.get(test_column, {}), "Run 2 should have executed and produced analysis_d_stat"
        
        # Build aggregated_summary for run 2 (simulating ColumnExecutorDataflow)
        # Start with cached data
        aggregated_summary_2 = {}
        if cached_merged_sd_2:
            for rw_col_iter, cached_stats in cached_merged_sd_2.items():
                if isinstance(cached_stats, dict):
                    aggregated_summary_2[rw_col_iter] = cached_stats.copy()
        
        # Add newly computed results
        for note in collected2:
            if note.success and note.result:
                for orig_col, col_res in note.result.items():
                    stats = col_res.result or {}
                    rw = orig_to_rw_map.get(orig_col, orig_col)
                    entry = aggregated_summary_2.get(rw)
                    if entry is None:
                        entry = {'orig_col_name': orig_col, 'rewritten_col_name': rw}
                        aggregated_summary_2[rw] = entry
                    entry.update(stats)
        
        # Save merged_sd after run 2
        if aggregated_summary_2:
            merged_sd_2 = merge_sds({}, aggregated_summary_2, {})
            fc.upsert_file_metadata(test_file, {'merged_sd': merged_sd_2})
        
        # Verify results: should have a,b,c (from cache) + d (newly computed)
        merged_stats_2 = aggregated_summary_2.get(rw_col, {})
        assert 'analysis_a_stat' in merged_stats_2, "Run 2 should preserve analysis_a_stat from run 1"
        assert 'analysis_b_stat' in merged_stats_2, "Run 2 should preserve analysis_b_stat from run 1"
        assert 'analysis_c_stat' in merged_stats_2, "Run 2 should preserve analysis_c_stat from run 1"
        assert 'analysis_d_stat' in merged_stats_2, "Run 2 should add analysis_d_stat (was executed and merged)"
        
        # STEP 3: Run with analyses a,b,c again
        cached_merged_sd_3 = get_cached_merged_sd(fc, test_file)
        exec3 = PAFColumnExecutor(
            [AnalysisA, AnalysisB, AnalysisC],
            cached_merged_sd=cached_merged_sd_3,
            orig_to_rw_map=orig_to_rw_map
        )
        
        # All should be cached, so no execution needed
        exec_args_3 = exec3.get_execution_args(existing_cached)
        assert exec_args_3.no_exec, "Run 3 should set no_exec=True since all analyses are cached"
        assert len(exec_args_3.columns) == 0, "Run 3 should have no columns to execute"
        
        collected3 = []
        ex3 = Executor(ldf, exec3, create_listener(collected3), fc, file_path=test_file)
        ex3.run()
        
        # Verify no execution occurred (all cached)
        assert len(collected3) == 0, "Run 3 should produce no notifications since all analyses are cached"
        
        # Build final aggregated_summary (all from cache)
        aggregated_summary_3 = {}
        if cached_merged_sd_3:
            for rw_col, cached_stats in cached_merged_sd_3.items():
                if isinstance(cached_stats, dict):
                    aggregated_summary_3[rw_col] = cached_stats.copy()
        
        # Verify final state - should have a,b,c,d (all from previous runs)
        merged_stats_3 = aggregated_summary_3.get(rw_col, {})
        assert 'analysis_a_stat' in merged_stats_3, "Final state should have analysis_a_stat"
        assert 'analysis_b_stat' in merged_stats_3, "Final state should have analysis_b_stat"
        assert 'analysis_c_stat' in merged_stats_3, "Final state should have analysis_c_stat"
        assert 'analysis_d_stat' in merged_stats_3, "Final state should have analysis_d_stat (from run 2)"
        
    finally:
        cache_utils_module._file_cache = None
        cache_utils_module._executor_log = None
        if original_home:
            os.environ['HOME'] = original_home

