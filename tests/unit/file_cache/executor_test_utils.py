import polars as pl
import polars.selectors as cs
import time
from pathlib import Path
from typing import Callable

from buckaroo.file_cache.base import (
    ColumnExecutor,
    ExecutorArgs,
    ColumnResults,
    ColumnResult,
    FileCache,
    ProgressNotification,
)


class SimpleColumnExecutor(ColumnExecutor[ExecutorArgs]):
    def get_execution_args(self, existing_stats:dict[str,dict[str,object]]) -> ExecutorArgs:
        columns = list(existing_stats.keys())
        return ExecutorArgs(
            columns=columns,
            column_specific_expressions=False,
            include_hash=True,
            expressions=[
                cs.numeric().sum().name.suffix("_sum"),
                pl.len().name.suffix("_len"),
            ],
            row_start=None,
            row_end=None,
            extra=None,
        )

    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        cols = execution_args.columns
        only_cols_ldf = ldf.select(cols)
        res = only_cols_ldf.select(*execution_args.expressions).collect()

        col_results: ColumnResults = {}
        for col in cols:
            # Use a deterministic series_hash for tests without relying on pl_series_hash
            hash_: int = hash(col) & ((1 << 63) - 1)
            actual_result = {"len": res[col+"_len"][0] if col+"_len" in res.columns else 0}
            if col+"_sum" in res.columns:
                actual_result["sum"] = res[col+"_sum"][0]
            cr = ColumnResult(
                series_hash=hash_,
                column_name=col,
                expressions=[],
                result=actual_result,
            )
            col_results[col] = cr
        return col_results


class SlowColumnExecutor(SimpleColumnExecutor):
    def __init__(self, delay_sec: float) -> None:
        super().__init__()
        self.delay_sec = delay_sec
    def execute(self, ldf: pl.LazyFrame, execution_args: ExecutorArgs) -> ColumnResults:
        time.sleep(self.delay_sec)
        return super().execute(ldf, execution_args)


# Helper functions for PAFColumnExecutor tests
def create_listener(collected: list) -> Callable[[ProgressNotification], None]:
    """Create a listener that collects ProgressNotifications."""
    def listener(p: ProgressNotification) -> None:
        collected.append(p)
    return listener


def extract_results(notifications: list) -> dict:
    """Extract results from notifications into a dict keyed by column."""
    results = {}
    for note in notifications:
        if note.success and note.result:
            for col, col_result in note.result.items():
                if col not in results:
                    results[col] = {}
                results[col].update(col_result.result or {})
    return results


def get_cached_merged_sd(fc: FileCache, test_file: Path) -> dict:
    """Get cached merged_sd from file cache."""
    if fc.check_file(test_file):
        md = fc.get_file_metadata(test_file)
        if md and 'merged_sd' in md:
            return md.get('merged_sd', {})
    return {}


def build_existing_cached(fc: FileCache, test_file: Path, columns: list) -> dict:
    """Build existing_cached dict simulating what Executor does."""
    existing_cached = {}
    if fc.check_file(test_file):
        file_hashes = fc.get_file_series_hashes(test_file) or {}
        for col in columns:
            h = file_hashes.get(col)
            if h:
                cached_results = fc.get_series_results(h)
                existing_cached[col] = cached_results or {}
            else:
                existing_cached[col] = {'__missing_hash__': True}
    else:
        for col in columns:
            existing_cached[col] = {'__missing_hash__': True}
    return existing_cached


def has_stat(results: dict, column: str, stat_name: str) -> bool:
    """Check if a specific stat is present in results for a column."""
    return stat_name in results.get(column, {})


def assert_stats_present(results: dict, column: str, expected: list, unexpected: list = None) -> None:
    """Assert that expected stats are present and unexpected are not."""
    for stat in expected:
        assert has_stat(results, column, stat), f"{stat} missing for {column}"
    if unexpected:
        for stat in unexpected:
            assert not has_stat(results, column, stat), f"{stat} should not be present for {column}"

