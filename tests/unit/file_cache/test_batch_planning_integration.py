"""
Integration test for batch planning with faked column executor.

This test uses a faked executor that has varying sleep times based on which columns
are included. The test verifies the entire planning and execution flow.

Total test time should be < 7 seconds.
"""
import time
from datetime import timedelta
import polars as pl

from buckaroo.file_cache.batch_planning import (
    PlanningContext,
    default_planning_function,
    extract_execution_history,
)
from buckaroo.file_cache.base import (
    ExecutorArgs,
    ColumnExecutor,
    ColumnResults,
    ColumnResult,
    SimpleExecutorLog,
)
from buckaroo.file_cache.mp_timeout_decorator import mp_timeout


class SleepyColumnExecutor(ColumnExecutor[ExecutorArgs]):
    """
    Faked column executor that sleeps based on which columns are included.
    
    Sleep times:
    - Empty columns (baseline): 0.05s
    - Single column: 0.1s per column
    - Multiple columns: 0.1s per column (linear scaling)
    
    This simulates real execution time without actual computation.
    """
    
    def __init__(self, sleep_per_column: float = 0.1, baseline_sleep: float = 0.05):
        self.sleep_per_column = sleep_per_column
        self.baseline_sleep = baseline_sleep
    
    def get_execution_args(self, existing_stats: dict[str, dict[str, object]]) -> ExecutorArgs:
        # Return args for all columns not in existing_stats
        all_cols = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        cols_to_execute = [c for c in all_cols if c not in existing_stats or not existing_stats[c]]
        
        return ExecutorArgs(
            columns=cols_to_execute,
            column_specific_expressions=False,
            include_hash=True,
            expressions=[],
            row_start=None,
            row_end=None,
            extra=None,
            no_exec=False
        )
    
    def execute(self, ldf: pl.LazyFrame, execution_args: ExecutorArgs) -> ColumnResults:
        """Execute with sleep based on number of columns."""
        cols = execution_args.columns
        
        # Calculate sleep time
        if not cols:
            sleep_time = self.baseline_sleep
        else:
            sleep_time = len(cols) * self.sleep_per_column
        
        time.sleep(sleep_time)
        
        # Return fake results
        results: ColumnResults = {}
        for col in cols:
            results[col] = ColumnResult(
                series_hash=hash(col) % (2**63),  # Fake hash
                column_name=col,
                expressions=[],
                result={'mean': 1.0}  # Fake stats
            )
        
        return results


def test_batch_planning_integration():
    """
    Integration test for batch planning with faked executor.
    
    This test:
    1. Creates a faked executor with known sleep times
    2. Uses mp_timeout to execute batches
    3. Extracts history from executor log
    4. Uses planning function to determine next batches
    5. Verifies optimal batching is achieved
    
    Total time should be < 7 seconds.
    """
    # Setup
    df = pl.DataFrame({c: [1, 2, 3] for c in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']})
    ldf = df.lazy()
    executor_log = SimpleExecutorLog()
    dfi = (id(ldf), "")
    
    # Create executor with fast sleeps for testing
    executor = SleepyColumnExecutor(sleep_per_column=0.05, baseline_sleep=0.02)
    timeout_secs = 1.0  # 1 second timeout (plenty for our sleeps)
    
    all_columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    remaining_columns = all_columns.copy()
    baseline_overhead = timedelta(0)
    
    # Phase 1: Measure baseline
    baseline_args = ExecutorArgs(columns=[], column_specific_expressions=False, 
                                 include_hash=True, expressions=[], 
                                 row_start=None, row_end=None, extra=None, no_exec=False)
    executor_log.log_start_col_group(dfi, baseline_args, "TestExecutor")
    start = time.time()
    try:
        timed_exec = mp_timeout(timeout_secs)(executor.execute)
        timed_exec(ldf, baseline_args)
        executor_log.log_end_col_group(dfi, baseline_args)
        baseline_overhead = timedelta(seconds=time.time() - start)
    except Exception:
        # Baseline failed - use default
        baseline_overhead = timedelta(seconds=0.05)
    
    # Phase 2-5: Execute planning loop
    max_iterations = 20  # Safety limit (increased for tuning phases)
    iteration = 0
    
    while remaining_columns and iteration < max_iterations:
        iteration += 1
        
        # Get history from executor log
        history = extract_execution_history(executor_log, dfi)
        
        # Create planning context
        context = PlanningContext(
            all_columns=all_columns,
            baseline_overhead=baseline_overhead,
            timeout_secs=timeout_secs,
            execution_history=history,
            remaining_columns=remaining_columns.copy()  # Copy to avoid mutation issues
        )
        
        # Plan next batches
        plan_result = default_planning_function(context)
        
        if not plan_result.batches:
            break  # Done
        
        # Execute batches
        executed_any = False
        for batch in plan_result.batches:
            if not batch.columns:
                # Empty baseline batch - already handled
                continue
            
            ex_args = ExecutorArgs(
                columns=batch.columns,
                column_specific_expressions=False,
                include_hash=True,
                expressions=[],
                row_start=None,
                row_end=None,
                extra=None,
                no_exec=False
            )
            
            executor_log.log_start_col_group(dfi, ex_args, "TestExecutor")
            start = time.time()
            try:
                timed_exec = mp_timeout(timeout_secs)(executor.execute)
                timed_exec(ldf, ex_args)
                executor_log.log_end_col_group(dfi, ex_args)
                executed_any = True
                # Remove executed columns from remaining
                for col in batch.columns:
                    if col in remaining_columns:
                        remaining_columns.remove(col)
            except Exception:
                # Timeout or other error - don't log end, so it's marked as incomplete/timed_out
                # This is expected behavior for the algorithm (half batch might timeout)
                executed_any = True  # We still attempted execution
                pass
        
        # Safety check: if we didn't execute anything and have remaining columns, break
        if not executed_any and remaining_columns:
            break
    
    # Verify all columns were processed
    assert len(remaining_columns) == 0, f"Not all columns processed: {remaining_columns}"
    
    # Verify we used optimal batching (should have more than 1 batch for 8 columns)
    final_history = extract_execution_history(executor_log, dfi)
    non_baseline_results = [r for r in final_history if r.columns]
    assert len(non_baseline_results) >= 2, "Should have used batching (more than 1 batch)"
    
    # Verify final state: all columns should be processed
    # Note: Some batches might timeout during tuning (half batch, single column) - that's expected
    # The important thing is that we eventually process all columns with optimal batching
    processed_columns = set()
    for result in final_history:
        if result.success and result.columns:
            processed_columns.update(result.columns)
    
    assert processed_columns == set(all_columns), (
        f"Not all columns processed. Processed: {processed_columns}, "
        f"Expected: {set(all_columns)}"
    )
