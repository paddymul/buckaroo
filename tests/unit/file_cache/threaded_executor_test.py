import time
import polars as pl
from typing import List, Type

from buckaroo.file_cache.threaded_executor import ThreadedExecutor
from buckaroo.file_cache.paf_column_executor import PAFColumnExecutor
from buckaroo.file_cache.base import ProgressNotification
from buckaroo.dataflow.column_executor_dataflow import ColumnExecutorDataflow
from buckaroo.pluggable_analysis_framework.polars_analysis_management import PolarsAnalysis


class SleepyPAF(PAFColumnExecutor):
    """
    Sleeps a variable amount per column to force out-of-order completion.
    """
    def __init__(self, analyses: List[Type[PolarsAnalysis]]) -> None:
        super().__init__(analyses)
        self._sleep_map = {}

    def execute(self, ldf: pl.LazyFrame, execution_args):
        # sleep based on the first column name length to vary order
        cols = execution_args.columns
        delay = 0.05 * len(cols[0]) if cols else 0.01
        time.sleep(delay)
        return super().execute(ldf, execution_args)


class FailingPAF(PAFColumnExecutor):
    """
    Fails for a specific target column name; succeeds for others.
    """
    def __init__(self, analyses: List[Type[PolarsAnalysis]], fail_col: str) -> None:
        super().__init__(analyses)
        self.fail_col = fail_col

    def execute(self, ldf: pl.LazyFrame, execution_args):
        cols = execution_args.columns
        if self.fail_col in cols:
            raise RuntimeError("intentional failure for testing")
        return super().execute(ldf, execution_args)


def test_threaded_executor_notes_match_results():
    df = pl.DataFrame({'a': [1,2,3], 'long_name': [10,20,30], 'b': [7,8,9]})
    ldf = df.lazy()

    notes: list[ProgressNotification] = []
    def capture_note(note: ProgressNotification):
        notes.append(note)

    cdf = ColumnExecutorDataflow(
        ldf,
        column_executor_class=SleepyPAF,
        executor_class=ThreadedExecutor
    )
    cdf.compute_summary_with_executor(progress_listener=capture_note)

    # We should have at least as many success notes as columns (depending on grouping size)
    success_notes = [n for n in notes if n.success]
    assert len(success_notes) >= 3
    # Each note's result keys should match the col_group reported
    for n in success_notes:
        if n.result is None:
            continue
        result_cols = set(n.result.keys())
        reported_cols = set(n.col_group)
        assert result_cols == reported_cols


def test_threaded_executor_isolates_failures():
    df = pl.DataFrame({'ok1': [1,2,3], 'boom': [10,20,30], 'ok2': [7,8,9]})
    ldf = df.lazy()

    from buckaroo.file_cache.threaded_executor import ThreadedExecutor

    notes: list[ProgressNotification] = []
    def capture_note(note: ProgressNotification):
        notes.append(note)

    cdf = ColumnExecutorDataflow(
        ldf,
        column_executor_class=lambda analyses: FailingPAF(analyses, fail_col='boom'),
        executor_class=ThreadedExecutor
    )
    # Progress listener to capture both success/failure notes
    cdf.compute_summary_with_executor(progress_listener=capture_note)

    # Verify at least one failure note for 'boom', and successes for ok1/ok2
    fail_notes = [n for n in notes if not n.success]
    assert any('boom' in n.col_group for n in fail_notes)
    success_notes = [n for n in notes if n.success]
    all_success_cols = set()
    for n in success_notes:
        all_success_cols.update(n.col_group)
    assert 'ok1' in all_success_cols and 'ok2' in all_success_cols
    # final merged_sd excludes failed column
    assert 'boom' not in cdf.merged_sd

