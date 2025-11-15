from __future__ import annotations

from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed

import polars as pl

from .base import (
    Executor,
    ColumnExecutor,
    FileCache,
    ProgressNotification,
    ProgressListener,
    SimpleExecutorLog,
)


class ThreadedExecutor(Executor):
    """
    Executor that runs column groups in parallel using a thread pool.
    It preserves ProgressNotification semantics and file cache upserts.
    """
    def __init__(
        self,
        ldf: pl.LazyFrame,
        column_executor: ColumnExecutor,
        listener: ProgressListener,
        fc: FileCache,
        executor_log: Optional[SimpleExecutorLog] = None,
        max_workers: Optional[int] = None,
    ) -> None:
        super().__init__(ldf, column_executor, listener, fc, executor_log)
        self.max_workers = max_workers

    def run(self) -> None:
        col_groups = self.get_column_chunks()
        if not col_groups:
            return
        workers = self.max_workers or min(8, len(col_groups))

        # Submit all column groups
        with ThreadPoolExecutor(max_workers=workers) as pool:
            future_to_args = {}
            for col_group in col_groups:
                ex_args = self.get_executor_args(col_group)
                self.executor_log.log_start_col_group(self.dfi, ex_args)
                fut = pool.submit(self.column_executor.execute, self.ldf, ex_args)
                future_to_args[fut] = (col_group, ex_args)

            # Handle completions in actual completion order
            for fut in as_completed(future_to_args):
                col_group, ex_args = future_to_args[fut]
                try:
                    res = fut.result()
                    # upsert results into the file cache
                    for _col, col_result in res.items():
                        self.fc.upsert_key(col_result.series_hash, col_result.result)
                    # notify listener
                    self.listener(ProgressNotification(
                        success=True,
                        col_group=col_group,
                        execution_args=[],  # FIXME: could add more details
                        result=res,
                        execution_time=(self.executor_log.find_event(self.dfi, ex_args).end_time  # type: ignore
                                        if self.executor_log.find_event(self.dfi, ex_args) else None) or 0,
                        failure_message=None
                    ))
                    self.executor_log.log_end_col_group(self.dfi, ex_args)
                except Exception as e:
                    self.listener(ProgressNotification(
                        success=False,
                        col_group=col_group,
                        execution_args=[],
                        result=None,
                        execution_time=0,
                        failure_message=str(e)
                    ))
                    # do not mark completed on failure
                    continue


