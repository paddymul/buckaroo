import os
import sys
import threading
import multiprocessing
import time
from datetime import datetime

import polars as pl

from buckaroo.file_cache.base import FileCache, ProgressNotification
from buckaroo.file_cache.multiprocessing_executor import MultiprocessingExecutor
from .executor_test_utils import SimpleColumnExecutor, SlowColumnExecutor


def _print_ci_diagnostics(test_name: str):
    """Print diagnostic information for CI debugging"""
    print(f"\n{'='*80}")
    print(f"CI DIAGNOSTICS: {test_name}")
    print(f"{'='*80}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"OS name: {os.name}")
    print(f"CI environment: {os.environ.get('CI', 'Not set')}")
    print(f"GitHub Actions: {os.environ.get('GITHUB_ACTIONS', 'Not set')}")
    print(f"Runner OS: {os.environ.get('RUNNER_OS', 'Not set')}")
    print(f"CPU count: {multiprocessing.cpu_count()}")
    print(f"Multiprocessing start method: {multiprocessing.get_start_method()}")
    print(f"Active threads: {threading.active_count()}")
    print(f"Thread names: {[t.name for t in threading.enumerate()]}")
    print(f"Process PID: {os.getpid()}")
    print(f"Parent PID: {os.getppid()}")
    print(f"{'='*80}\n", flush=True)


def test_multiprocessing_executor_success():
    _print_ci_diagnostics("test_multiprocessing_executor_success")
    
    df = pl.DataFrame({'a1': [1,2,3], 'b2': [10,20,30]})
    ldf = df.lazy()
    fc = FileCache()
    notes: list[ProgressNotification] = []
    
    def listener(p: ProgressNotification):
        notes.append(p)
        print(f"[LISTENER] Received notification: success={p.success}, "
              f"col_group={p.col_group}, failure_message={p.failure_message}, "
              f"execution_time={p.execution_time}, thread={threading.current_thread().name}", 
              flush=True)
    
    print(f"[TEST] Creating MultiprocessingExecutor: async_mode=False, timeout_secs=5.0", flush=True)
    print(f"[TEST] DataFrame columns: {df.columns}", flush=True)
    print(f"[TEST] Threads before run: {threading.active_count()} ({[t.name for t in threading.enumerate()]})", flush=True)
    
    t_start = time.time()
    exc = MultiprocessingExecutor(ldf, SimpleColumnExecutor(), listener, fc, timeout_secs=5.0, async_mode=False)
    print(f"[TEST] Executor created, calling run()...", flush=True)
    exc.run()
    t_end = time.time()
    
    print(f"[TEST] Run completed in {t_end - t_start:.3f}s", flush=True)
    print(f"[TEST] Threads after run: {threading.active_count()} ({[t.name for t in threading.enumerate()]})", flush=True)
    print(f"[TEST] Total notifications received: {len(notes)}", flush=True)
    print(f"[TEST] Notifications: {[(n.success, n.col_group, n.failure_message) for n in notes]}", flush=True)
    
    # one notification per column
    assert len(notes) == len(df.columns), f"Expected {len(df.columns)} notifications, got {len(notes)}"
    assert all(n.success for n in notes), f"Not all notifications succeeded: {[(n.success, n.failure_message) for n in notes]}"
    # cache populated for each col (cannot assert exact keys)
    assert len(fc.summary_stats_cache.keys()) >= len(df.columns), f"Expected at least {len(df.columns)} cache entries, got {len(fc.summary_stats_cache.keys())}"
    print(f"[TEST] Test assertions passed", flush=True)


def test_multiprocessing_executor_timeout():
    _print_ci_diagnostics("test_multiprocessing_executor_timeout")
    
    df = pl.DataFrame({'a1': [1,2,3], 'b2': [10,20,30]})
    ldf = df.lazy()
    fc = FileCache()
    notes: list[ProgressNotification] = []
    
    def listener(p: ProgressNotification):
        notes.append(p)
        print(f"[LISTENER] Received notification: success={p.success}, "
              f"col_group={p.col_group}, failure_message={p.failure_message}, "
              f"execution_time={p.execution_time}, thread={threading.current_thread().name}", 
              flush=True)

    # Make each column execute longer than the timeout
    #FIXME we should have a test that exercises async_mode=True verifying that the right callbacks are called 
    print(f"[TEST] Creating MultiprocessingExecutor: async_mode=False, timeout_secs=2.0, executor delay=2.5s", flush=True)
    print(f"[TEST] DataFrame columns: {df.columns}", flush=True)
    print(f"[TEST] Threads before run: {threading.active_count()} ({[t.name for t in threading.enumerate()]})", flush=True)
    
    t_start = time.time()
    exc = MultiprocessingExecutor(ldf, SlowColumnExecutor(2.5), listener, fc, timeout_secs=2.0, async_mode=False)
    print(f"[TEST] Executor created, calling run()...", flush=True)
    exc.run()
    t_end = time.time()
    
    print(f"[TEST] Run completed in {t_end - t_start:.3f}s (expected ~2s for timeout)", flush=True)
    print(f"[TEST] Threads after run: {threading.active_count()} ({[t.name for t in threading.enumerate()]})", flush=True)
    print(f"[TEST] Total notifications received: {len(notes)}", flush=True)
    print(f"[TEST] Notifications: {[(n.success, n.col_group, n.failure_message) for n in notes]}", flush=True)
    
    # Expect two failures (one per column group) with timeout messages
    assert len(notes) == len(df.columns), f"Expected {len(df.columns)} notifications, got {len(notes)}"
    assert all((not n.success) for n in notes), f"Expected all notifications to fail, got: {[(n.success, n.failure_message) for n in notes]}"
    assert all("timeout" in (n.failure_message or "").lower() for n in notes), f"Expected all failures to be timeouts, got: {[n.failure_message for n in notes]}"
    print(f"[TEST] Test assertions passed", flush=True)


