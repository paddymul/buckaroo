from __future__ import annotations

from datetime import datetime as dtdt
from typing import Optional, Any
from pathlib import Path
import os
import threading
import logging

import polars as pl

from .base import (
    Executor as BaseExecutor,
    ColumnExecutor,
    ExecutorArgs,
    FileCache,
    ProgressNotification,
    ProgressListener,
    SimpleExecutorLog,
)
from .mp_timeout_decorator import mp_timeout, TimeoutException, ExecutionFailed
from .batch_planning import PlanningFunction, default_planning_function, simple_one_column_planning


def _execute_column(column_executor: ColumnExecutor, ldf: pl.LazyFrame, ex_args):
    return column_executor.execute(ldf, ex_args)


class MultiprocessingExecutor(BaseExecutor):
    """
    Executor that runs each column group in a separate process with a timeout.
    Uses mp_timeout (cloudpickle + multiprocessing) to isolate crashes and cap runtime.
    """
    def __init__(
        self,
        ldf: pl.LazyFrame,
        column_executor: ColumnExecutor,
        listener: ProgressListener,
        fc: FileCache,
        executor_log: Optional[SimpleExecutorLog] = None,
        file_path: str | Path | None = None,
        timeout_secs: float = 30.0,
        async_mode: bool = True,
        cached_merged_sd: dict[str, dict[str, Any]] | None = None,
        orig_to_rw_map: dict[str, str] | None = None,
        planning_function: Optional[PlanningFunction] = None,
    ) -> None:
        # Use simple_one_column_planning by default for backward compatibility
        # Can be overridden with default_planning_function for batch optimization
        planning_func = planning_function or simple_one_column_planning
        super().__init__(ldf, column_executor, listener, fc, executor_log, file_path=file_path, 
                        cached_merged_sd=cached_merged_sd, orig_to_rw_map=orig_to_rw_map,
                        planning_function=planning_func)
        self.timeout_secs = timeout_secs
        self.async_mode = async_mode

    def run(self) -> None:
        logger = logging.getLogger("buckaroo.multiprocessing_executor")
        executor_id = id(self)
        executor_pid = os.getpid()
        log_msg = f"MultiprocessingExecutor.run() START - executor_id={executor_id}, pid={executor_pid}, async_mode={self.async_mode}"
        logger.info(log_msg)
        print(f"[buckaroo] {log_msg}")  # Print for visibility
        
        def _work():
            worker_pid = os.getpid()
            worker_thread_id = threading.get_ident()
            log_msg = f"MultiprocessingExecutor._work() START - executor_id={executor_id}, original_pid={executor_pid}, worker_pid={worker_pid}, worker_thread_id={worker_thread_id}"
            logger.info(log_msg)
            print(f"[buckaroo] {log_msg}")  # Print for visibility
            
            # Use get_next_column_chunk() to get batches one at a time
            while True:
                group = self.get_next_column_chunk()
                if group is None:
                    break
                ex_args = self.get_executor_args(group)
                
                # Check if already failed (don't retry)
                if self.executor_log.check_log_for_previous_failure(self.dfi, ex_args):
                    log_msg = f"MultiprocessingExecutor._work() SKIPPING group {group} - previous failure detected"
                    logger.info(log_msg)
                    print(f"[buckaroo] {log_msg}")
                    self._update_planning_state_after_execution(list(group))
                    continue
                
                # Check if already completed
                original_group_args = ExecutorArgs(
                    columns=list(group),
                    column_specific_expressions=ex_args.column_specific_expressions,
                    include_hash=ex_args.include_hash,
                    expressions=ex_args.expressions,
                    row_start=ex_args.row_start,
                    row_end=ex_args.row_end,
                    extra=ex_args.extra,
                    no_exec=False
                )
                
                if self.executor_log.check_log_for_completed(self.dfi, original_group_args):
                    log_msg = f"MultiprocessingExecutor._work() SKIPPING group {group} - already completed (found in executor log)"
                    logger.info(log_msg)
                    print(f"[buckaroo] {log_msg}")
                    self._update_planning_state_after_execution(list(group))
                    continue
                
                # Check if no_exec (all columns cached via merged_sd)
                if ex_args.no_exec:
                    log_msg = f"MultiprocessingExecutor._work() SKIPPING group {group} - no_exec=True (all columns cached)"
                    logger.info(log_msg)
                    print(f"[buckaroo] {log_msg}")
                    self._update_planning_state_after_execution(list(group))
                    continue
                
                # No columns to execute
                if not ex_args.columns:
                    log_msg = f"MultiprocessingExecutor._work() SKIPPING group {group} - no columns to execute"
                    logger.debug(log_msg)
                    print(f"[buckaroo] {log_msg}")
                    self._update_planning_state_after_execution(list(group))
                    continue
                
                self.executor_log.log_start_col_group(self.dfi, ex_args, self.executor_class_name)
                t1 = dtdt.now()
                try:
                    timed_exec = mp_timeout(self.timeout_secs)(_execute_column)
                    res = timed_exec(self.column_executor, self.ldf, ex_args)
                    # persist results
                    for _col, col_result in res.items():
                        self.fc.upsert_key(col_result.series_hash, col_result.result)
                    t2 = dtdt.now()

                    listener_id = id(self.listener)
                    log_msg = f"MultiprocessingExecutor._work() CALLING LISTENER - executor_id={executor_id}, worker_pid={worker_pid}, listener_id={listener_id}, col_group={group}, columns_computed={len(res)}"
                    logger.info(log_msg)
                    print(f"[buckaroo] {log_msg}")  # Print for visibility
                    self.listener(ProgressNotification(
                        success=True,
                        col_group=group,
                        execution_args=[],
                        result=res,
                        execution_time=t2-t1,  # timedelta
                        failure_message=None
                    ))
                    self.executor_log.log_end_col_group(self.dfi, ex_args)
                    # Update planning state after successful execution
                    executed_columns = list(res.keys())
                    self._update_planning_state_after_execution(executed_columns)
                except TimeoutException:
                    t2 = dtdt.now()
                    self.listener(ProgressNotification(
                        success=False,
                        col_group=group,
                        execution_args=[],
                        result=None,
                        execution_time=t2-t1,  # timedelta
                        failure_message=f"timeout after {self.timeout_secs}s",
                    ))
                    # Update planning state to prevent infinite loop
                    self._update_planning_state_after_execution(list(group))
                    continue
                except ExecutionFailed:
                    t2 = dtdt.now()
                    # ExecutionFailed means the worker process exited abnormally (non-zero exit,
                    # crash/SystemExit, or failed to serialize/return a result). Other exceptions
                    # caught below are raised in the parent process during orchestration.
                    self.listener(ProgressNotification(
                        success=False,
                        col_group=group,
                        execution_args=[],
                        result=None,
                        execution_time=t2-t1,  # timedelta
                        failure_message="execution failed in worker",
                    ))
                    # Update planning state to prevent infinite loop
                    self._update_planning_state_after_execution(list(group))
                    continue
                except Exception as e:
                    t2 = dtdt.now()
                    self.listener(ProgressNotification(
                        success=False,
                        col_group=group,
                        execution_args=[],
                        result=None,
                        execution_time=t2-t1,  # timedelta
                        failure_message=str(e),
                    ))
                    # Update planning state to prevent infinite loop
                    self._update_planning_state_after_execution(list(group))
                    continue

        if self.async_mode:
            listener_id = id(self.listener)
            log_msg = f"MultiprocessingExecutor.run() STARTING BACKGROUND THREAD - executor_id={executor_id}, pid={executor_pid}, listener_id={listener_id}, async_mode=True"
            logger.info(log_msg)
            print(f"[buckaroo] {log_msg}")  # Print for visibility
            t = threading.Thread(target=_work, daemon=True)
            t.start()
            thread_id = t.ident
            log_msg = f"MultiprocessingExecutor.run() THREAD STARTED - executor_id={executor_id}, thread_id={thread_id}, listener_id={listener_id}, returning immediately (async_mode=True)"
            logger.info(log_msg)
            print(f"[buckaroo] {log_msg}")  # Print for visibility
            return
        else:
            _work()


