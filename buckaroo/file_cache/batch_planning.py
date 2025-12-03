"""
Batch planning system for multiprocessing executor.

This module provides a pluggable planning system that determines optimal column batch sizes
for multiprocessing execution, balancing overhead vs. timeout risk.

The planning algorithm:
1. Measures baseline mp_timeout overhead (no-op call)
2. Tries half the columns as first batch
3. If succeeds before timeout, processes other half
4. If fails due to timeout, tries single column to measure per-column time
5. Uses this data to determine optimal batch size for remaining columns
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from buckaroo.file_cache.base import ExecutorLog, DFIdentifier


@dataclass
class ExecutionResult:
    """Result of executing a batch of columns."""
    columns: list[str]
    success: bool
    execution_time: timedelta
    timed_out: bool
    error: str | None = None


@dataclass
class PlanningContext:
    """Context for planning column batches."""
    all_columns: list[str]
    baseline_overhead: timedelta  # Time for no-op mp_timeout call
    timeout_secs: float  # Timeout in seconds (like mp_timeout expects)
    execution_history: list[ExecutionResult]
    remaining_columns: list[str]  # Columns not yet executed


@dataclass
class ColumnBatch:
    """A planned batch of columns to execute."""
    columns: list[str]
    expected_duration: Optional[timedelta] = None  # Optional estimate


@dataclass
class PlanningResult:
    """Result of planning step."""
    batches: list[ColumnBatch]
    phase: str  # "baseline", "half_batch", "single_column", "optimized", "complete", "error"
    notes: str = ""  # Optional notes about planning decisions


PlanningFunction = Callable[[PlanningContext], PlanningResult]


def extract_execution_history(executor_log: 'ExecutorLog', dfi: 'DFIdentifier') -> list[ExecutionResult]:
    """
    Extract execution history from executor log.
    
    Converts ExecutorLogEvent objects to ExecutionResult objects for planning.
    Filters to events matching the dfi.
    
    Args:
        executor_log: ExecutorLog instance
        dfi: DFIdentifier tuple (id(ldf), file_path_str)
    
    Returns:
        List of ExecutionResult objects, ordered by execution time.
    """
    # Import at runtime to avoid circular import
    
    try:
        events = executor_log.get_log_events()
    except Exception:
        return []
    
    results = []
    for event in events:
        # Filter to matching dfi
        if event.dfi != dfi:
            continue
        
        # Determine if timed out (started but not completed, and end_time is None)
        timed_out = not event.completed and event.end_time is None
        
        # Calculate execution time
        if event.end_time:
            execution_time = event.end_time - event.start_time
        else:
            # If not completed, use a default timeout duration
            # For planning purposes, we'll use a large time if timed out
            execution_time = timedelta(seconds=30.0)  # Default timeout
        
        results.append(ExecutionResult(
            columns=list(event.args.columns),
            success=event.completed,
            execution_time=execution_time,
            timed_out=timed_out,
            error=None  # ExecutorLogEvent doesn't store error messages
        ))
    
    return results


def simple_one_column_planning(context: PlanningContext) -> PlanningResult:
    """
    Simple planning function that returns one column at a time.
    
    This is the default for backward compatibility - it maintains
    the original behavior of one column per batch.
    """
    remaining = context.remaining_columns
    
    if not remaining:
        return PlanningResult(batches=[], phase="complete", notes="No columns remaining")
    
    # Return first column as a single batch
    return PlanningResult(
        batches=[ColumnBatch(columns=[remaining[0]])],
        phase="simple",
        notes="One column at a time (simple planning)"
    )


def default_planning_function(context: PlanningContext) -> PlanningResult:
    """
    Default planning function implementing the tuning algorithm.
    
    Algorithm:
    1. If no history, start with baseline measurement (no-op)
    2. If baseline done but no batch history, try half the columns
    3. If half batch timed out, try single column
    4. If we have timing data, calculate optimal batch size for remaining columns
    
    Returns:
        PlanningResult with batches to execute next
    """
    remaining = context.remaining_columns
    history = context.execution_history
    timeout_secs = context.timeout_secs
    
    if not remaining:
        return PlanningResult(batches=[], phase="complete", notes="No columns remaining")
    
    # Phase 1: Measure baseline overhead if not done
    baseline_results = [r for r in history if not r.columns]  # No-op calls have empty columns
    if not baseline_results:
        return PlanningResult(
            batches=[ColumnBatch(columns=[])],  # Empty batch for baseline
            phase="baseline",
            notes="Measuring mp_timeout baseline overhead"
        )
    
    # Phase 2: Try half batch if not done
    half_batch_results = [r for r in history if len(r.columns) == len(context.all_columns) // 2]
    if not half_batch_results:
        half_size = max(1, len(remaining) // 2)
        return PlanningResult(
            batches=[ColumnBatch(columns=remaining[:half_size])],
            phase="half_batch",
            notes=f"Trying half batch ({half_size} columns)"
        )
    
    half_result = half_batch_results[0]
    
    # Phase 3: If half batch succeeded, process other half
    if half_result.success and not half_result.timed_out:
        # Find which columns were in the half batch
        half_batch_cols = set(half_result.columns)
        # Get remaining columns that weren't in the half batch
        other_half = [c for c in remaining if c not in half_batch_cols]
        if other_half:
            return PlanningResult(
                batches=[ColumnBatch(columns=other_half)],
                phase="other_half",
                notes="Half batch succeeded, processing other half"
            )
        # All done
        return PlanningResult(batches=[], phase="complete", notes="All columns processed")
    
    # Phase 4: Half batch timed out, try single column
    single_col_results = [r for r in history if len(r.columns) == 1]
    if not single_col_results:
        # Try first remaining column
        return PlanningResult(
            batches=[ColumnBatch(columns=[remaining[0]])],
            phase="single_column",
            notes="Half batch timed out, measuring single column time"
        )
    
    single_result = single_col_results[0]
    
    # Phase 5: Calculate optimal batch size from data
    if not single_result.success or single_result.timed_out:
        # Single column also timed out - this shouldn't happen per requirements
        # but we'll handle it by going to expression bisector (not handled here)
        return PlanningResult(
            batches=[],
            phase="error",
            notes="Single column timed out - should use expression bisector"
        )
    
    # We have: baseline_overhead, single_column_time, timeout
    # Calculate how many columns we can fit in remaining time
    baseline = context.baseline_overhead
    single_time = single_result.execution_time
    timeout = timedelta(seconds=timeout_secs)
    
    # Per-column time (excluding baseline overhead)
    if single_time > baseline:
        per_column_time = single_time - baseline
    else:
        # Baseline is larger than single column time (unlikely but handle it)
        per_column_time = single_time
    
    # Available time per batch (leave some margin)
    margin = timedelta(seconds=1.0)  # 1 second margin
    available_time = timeout - baseline - margin
    
    if available_time <= timedelta(0):
        # Timeout is too small, can only do 1 column at a time
        optimal_batch_size = 1
    else:
        # Calculate how many columns fit
        optimal_batch_size = max(1, int(available_time.total_seconds() / per_column_time.total_seconds()))
    
    # Don't exceed remaining columns
    optimal_batch_size = min(optimal_batch_size, len(remaining))
    
    # Create batches for remaining columns
    batches = []
    for i in range(0, len(remaining), optimal_batch_size):
        batch_cols = remaining[i:i + optimal_batch_size]
        expected_duration = baseline + (per_column_time * len(batch_cols))
        batches.append(ColumnBatch(
            columns=batch_cols,
            expected_duration=expected_duration
        ))
    
    return PlanningResult(
        batches=batches,
        phase="optimized",
        notes=f"Optimal batch size: {optimal_batch_size} columns "
              f"(baseline={baseline.total_seconds():.2f}s, "
              f"per_col={per_column_time.total_seconds():.2f}s, "
              f"timeout={timeout_secs:.2f}s)"
    )
