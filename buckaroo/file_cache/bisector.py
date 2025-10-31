from __future__ import annotations

from abc import ABC, abstractmethod
import itertools
from typing import Any
import polars as pl

from .base import (
    ExecutorLogEvent,
    ExecutorLog,
    ColumnExecutor,
    ExecutorArgs,
    now,
)


class BaseBisector(ABC):
    """
    Shared delta-debugging logic over a sequence of items (by index).

    Subclasses must provide how to build ExecutorArgs from selected indices and
    how many base items exist.
    """

    def __init__(self,
                 event: ExecutorLogEvent,
                 executor_log: ExecutorLog,
                 column_executor: ColumnExecutor[Any],
                 ldf: pl.LazyFrame) -> None:
        self.original_event = event
        self.executor_log = executor_log
        self.column_executor = column_executor
        self.ldf = ldf
        self.dfi = event.dfi

    @abstractmethod
    def base_size(self) -> int:
        ...

    @abstractmethod
    def build_args_from_indices(self, indices: list[int]) -> ExecutorArgs:
        ...

    def try_execute_by_indices(self, indices: list[int]) -> tuple[bool, ExecutorLogEvent]:
        args = self.build_args_from_indices(indices)
        self.executor_log.log_start_col_group(self.dfi, args)
        try:
            self.column_executor.execute(self.ldf, args)
        except Exception:  # noqa: BLE001
            ev = self.executor_log.find_event(self.dfi, args)
            if ev is None:
                ev = ExecutorLogEvent(dfi=self.dfi,
                                      args=args,
                                      start_time=now(),
                                      end_time=None,
                                      completed=False)
            return False, ev
        self.executor_log.log_end_col_group(self.dfi, args)
        ev = self.executor_log.find_event(self.dfi, args)
        if ev is None or not ev.completed:
            raise RuntimeError("Bisector expected a completed log event after successful execute")
        return True, ev

    def minimize_failing_indices(self, all_indices: list[int]) -> list[int]:
        overall_ok, _ = self.try_execute_by_indices(all_indices)
        if overall_ok:
            return []

        n = 2
        current = list(all_indices)
        while len(current) >= 2:
            # split into n chunks
            chunk_size = max(1, len(current) // n)
            subsets: list[list[int]] = [current[i:i + chunk_size] for i in range(0, len(current), chunk_size)]

            some_failure_found = False
            # Try each subset (reduce): if a subset fails, shrink to it
            for subset in subsets:
                subset_succeeds, _ = self.try_execute_by_indices(subset)
                if not subset_succeeds:
                    current = subset
                    n = 2
                    some_failure_found = True
                    break

            if some_failure_found:
                continue

            # Try complements
            for i in range(len(subsets)):
                complement: list[int] = list(itertools.chain.from_iterable(subsets[:i] + subsets[i + 1:]))
                if not complement:
                    continue
                complement_succeeds, _ = self.try_execute_by_indices(complement)
                if not complement_succeeds:
                    current = complement
                    n = max(n - 1, 2)
                    some_failure_found = True
                    break

            if some_failure_found:
                continue

            if n >= len(current):
                break
            n = min(len(current), n * 2)

        return current

    def run(self) -> tuple[ExecutorLogEvent, ExecutorLogEvent]:
        # If original event succeeded, nothing to bisect
        if self.original_event.completed:
            return self.original_event, self.original_event

        all_indices = list(range(self.base_size()))
        # Find minimal failing subset
        minimal_fail_idxs = self.minimize_failing_indices(all_indices)
        if not minimal_fail_idxs:
            # No failure induced by items; treat original as success and return it with itself
            _, success_ev = self.try_execute_by_indices(all_indices)
            return success_ev, success_ev

        # Build maximal success set as complement and verify; otherwise, greedy-build
        complement_idxs = [i for i in all_indices if i not in set(minimal_fail_idxs)]
        complement_succeeds, success_ev = self.try_execute_by_indices(complement_idxs)
        if not complement_succeeds:
            # Greedy build a large success set
            success_set: list[int] = []
            for i in all_indices:
                candidate = success_set + [i]
                candidate_succeeds, _ = self.try_execute_by_indices(candidate)
                if candidate_succeeds:
                    success_set.append(i)
            final_succeeds, success_ev = self.try_execute_by_indices(success_set)
            if not final_succeeds:
                # As a last resort, empty set (should always succeed)
                _, success_ev = self.try_execute_by_indices([])

        # Ensure we return the failing event corresponding to minimal failing subset
        minimal_subset_succeeds, fail_ev = self.try_execute_by_indices(minimal_fail_idxs)
        if minimal_subset_succeeds:
            raise RuntimeError("Bisector invariant violated: minimal failing subset unexpectedly succeeded")

        return fail_ev, success_ev


class ExpressionBisector(BaseBisector):
    """
    Delta-debug the expression list in ExecutorArgs to:
    - find the minimal subset that reproduces the original failure
    - find the maximal subset that still succeeds
    """

    def __init__(self,
                 event: ExecutorLogEvent,
                 executor_log: ExecutorLog,
                 column_executor: ColumnExecutor[Any],
                 ldf: pl.LazyFrame) -> None:
        super().__init__(event, executor_log, column_executor, ldf)
        self._base_expressions: list[pl.Expr] = list(event.args.expressions)

    def build_args_with_expressions(self, expressions: list[pl.Expr]) -> ExecutorArgs:
        src = self.original_event.args
        return ExecutorArgs(
            columns=list(src.columns),
            column_specific_expressions=src.column_specific_expressions,
            include_hash=src.include_hash,
            expressions=list(expressions),
            row_start=src.row_start,
            row_end=src.row_end,
            extra=src.extra,
        )

    def try_execute_with_expressions(self, expressions: list[pl.Expr]) -> tuple[bool, ExecutorLogEvent]:
        expr_to_index = {id(expr): idx for idx, expr in enumerate(self._base_expressions)}
        indices = [expr_to_index[id(e)] for e in expressions]
        return self.try_execute_by_indices(indices)

    def build_args_from_indices(self, indices: list[int]) -> ExecutorArgs:
        exprs = [self._base_expressions[i] for i in indices]
        return self.build_args_with_expressions(exprs)

    def base_size(self) -> int:
        return len(self._base_expressions)


class ColumnBisector(BaseBisector):
    """
    Delta-debug the columns in ExecutorArgs.columns to:
    - find the minimal subset of columns that reproduces the failure
    - find the maximal subset that still succeeds
    """

    def __init__(self,
                 event: ExecutorLogEvent,
                 executor_log: ExecutorLog,
                 column_executor: ColumnExecutor[Any],
                 ldf: pl.LazyFrame) -> None:
        super().__init__(event, executor_log, column_executor, ldf)
        self._base_columns: list[str] = list(event.args.columns)

    def build_args_with_columns(self, columns: list[str]) -> ExecutorArgs:
        src = self.original_event.args
        return ExecutorArgs(
            columns=list(columns),
            column_specific_expressions=src.column_specific_expressions,
            include_hash=src.include_hash,
            expressions=list(src.expressions),
            row_start=src.row_start,
            row_end=src.row_end,
            extra=src.extra,
        )

    def try_execute_with_columns(self, columns: list[str]) -> tuple[bool, ExecutorLogEvent]:
        index_map = {col: idx for idx, col in enumerate(self._base_columns)}
        indices = [index_map[c] for c in columns]
        return self.try_execute_by_indices(indices)

    def build_args_from_indices(self, indices: list[int]) -> ExecutorArgs:
        cols = [self._base_columns[i] for i in indices]
        return self.build_args_with_columns(cols)

    def base_size(self) -> int:
        return len(self._base_columns)


class RowRangeBisector:
    """
    Find a minimal contiguous row range [row_start, row_end) that reproduces a failure,
    and a maximal contiguous row range that succeeds.
    """

    def __init__(self,
                 event: ExecutorLogEvent,
                 executor_log: ExecutorLog,
                 column_executor: ColumnExecutor[Any],
                 ldf: pl.LazyFrame) -> None:
        self.original_event = event
        self.executor_log = executor_log
        self.column_executor = column_executor
        self.ldf = ldf
        self.dfi = event.dfi

        # Determine total rows for this LazyFrame
        self._total_rows: int = self.ldf.collect().height

    def build_args_with_range(self, row_start: int | None, row_end: int | None) -> ExecutorArgs:
        src = self.original_event.args
        return ExecutorArgs(
            columns=list(src.columns),
            column_specific_expressions=src.column_specific_expressions,
            include_hash=src.include_hash,
            expressions=list(src.expressions),
            row_start=row_start,
            row_end=row_end,
            extra=src.extra,
        )

    def _try_execute(self, row_start: int | None, row_end: int | None) -> tuple[bool, ExecutorLogEvent]:
        args = self.build_args_with_range(row_start, row_end)
        self.executor_log.log_start_col_group(self.dfi, args)
        try:
            self.column_executor.execute(self.ldf, args)
        except Exception:  # noqa: BLE001
            ev = self.executor_log.find_event(self.dfi, args)
            if ev is None:
                ev = ExecutorLogEvent(dfi=self.dfi,
                                      args=args,
                                      start_time=now(),
                                      end_time=None,
                                      completed=False)
            return False, ev
        self.executor_log.log_end_col_group(self.dfi, args)
        ev = self.executor_log.find_event(self.dfi, args)
        if ev is None or not ev.completed:
            raise RuntimeError("RowRangeBisector expected a completed log event after successful execute")
        return True, ev

    def _find_minimal_failing_window(self) -> tuple[int, int]:
        # Brute-force increasing window size to guarantee finding a minimal contiguous window
        n = self._total_rows
        for window in range(1, n + 1):
            for start in range(0, n - window + 1):
                end = start + window
                ok, _ = self._try_execute(start, end)
                if not ok:
                    return start, end
        # If no window fails, raise
        raise RuntimeError("RowRangeBisector could not find a failing window; original event may not be a failure")

    def run(self) -> tuple[ExecutorLogEvent, ExecutorLogEvent]:
        # If original event succeeded, nothing to bisect
        if self.original_event.completed:
            return self.original_event, self.original_event

        # Verify that full range fails (or at least current args) and then find minimal failing
        full_ok, _ = self._try_execute(None, None)
        if full_ok:
            # If full succeeds, return success twice
            _, success_ev = self._try_execute(None, None)
            return success_ev, success_ev

        s, e = self._find_minimal_failing_window()
        # Failing event for minimal window
        _, fail_ev = self._try_execute(s, e)

        # Maximal success: choose the larger of the two success windows that avoid [s,e)
        left_size = s
        right_size = self._total_rows - e
        if left_size >= right_size:
            success_ok, success_ev = self._try_execute(0, s)
            if not success_ok:
                # If left unexpectedly fails, try right
                success_ok, success_ev = self._try_execute(e, self._total_rows)
                if not success_ok:
                    # As a safeguard, empty window should succeed
                    success_ok, success_ev = self._try_execute(0, 0)
            return fail_ev, success_ev
        else:
            success_ok, success_ev = self._try_execute(e, self._total_rows)
            if not success_ok:
                success_ok, success_ev = self._try_execute(0, s)
                if not success_ok:
                    success_ok, success_ev = self._try_execute(0, 0)
            return fail_ev, success_ev


class SamplingRowBisector(BaseBisector):
    """
    Delta-debug over arbitrary row indices (non-contiguous) to:
    - find a minimal set of row indices that reproduces the failure
    - find a maximal set of row indices that succeeds

    Selected rows are communicated via ExecutorArgs.extra['row_indices'].
    """

    def __init__(self,
                 event: ExecutorLogEvent,
                 executor_log: ExecutorLog,
                 column_executor: ColumnExecutor[Any],
                 ldf: pl.LazyFrame) -> None:
        super().__init__(event, executor_log, column_executor, ldf)
        self._total_rows: int = self.ldf.collect().height

    def build_args_with_row_indices(self, row_indices: list[int]) -> ExecutorArgs:
        src = self.original_event.args
        extra = dict(src.extra) if isinstance(src.extra, dict) else {}
        extra['row_indices'] = list(row_indices)
        return ExecutorArgs(
            columns=list(src.columns),
            column_specific_expressions=src.column_specific_expressions,
            include_hash=src.include_hash,
            expressions=list(src.expressions),
            row_start=None,
            row_end=None,
            extra=extra,
        )

    def build_args_from_indices(self, indices: list[int]) -> ExecutorArgs:
        return self.build_args_with_row_indices(indices)

    def base_size(self) -> int:
        return self._total_rows


