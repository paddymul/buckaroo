import polars as pl

from buckaroo.file_cache.base import FileCache, ProgressNotification
from buckaroo.file_cache.multiprocessing_executor import MultiprocessingExecutor
from .executor_test_utils import SimpleColumnExecutor, SlowColumnExecutor


def test_multiprocessing_executor_success():
    df = pl.DataFrame({'a1': [1,2,3], 'b2': [10,20,30]})
    ldf = df.lazy()
    fc = FileCache()
    notes: list[ProgressNotification] = []
    def listener(p: ProgressNotification):
        notes.append(p)
    #FIXME this should be able to work without async_mode=False, but it doesn't .  maybe there is a pytest config
    exc = MultiprocessingExecutor(ldf, SimpleColumnExecutor(), listener, fc, timeout_secs=5.0, async_mode=False)
    exc.run()
    # one notification per column
    assert len(notes) == len(df.columns)
    assert all(n.success for n in notes)
    # cache populated for each col (cannot assert exact keys)
    assert len(fc.summary_stats_cache.keys()) >= len(df.columns)


def test_multiprocessing_executor_timeout():
    df = pl.DataFrame({'a1': [1,2,3], 'b2': [10,20,30]})
    ldf = df.lazy()
    fc = FileCache()
    notes: list[ProgressNotification] = []
    def listener(p: ProgressNotification):
        notes.append(p)

    # Make each column execute longer than the timeout
    #FIXME we should have a test that exercises async_mode=True verifying that the right callbacks are called 
    exc = MultiprocessingExecutor(ldf, SlowColumnExecutor(2.5), listener, fc, timeout_secs=2.0, async_mode=False)
    exc.run()
    # Expect two failures (one per column group) with timeout messages
    assert len(notes) == len(df.columns)
    assert all((not n.success) for n in notes)
    assert all("timeout" in (n.failure_message or "").lower() for n in notes)


def test_multiprocessing_executor_skips_cached_columns(tmp_path):
    """
    Test that MultiprocessingExecutor skips already-computed columns on re-execution.
    
    This verifies the behavior shown in logs where all column groups are skipped
    with "SKIPPING group [...] - no_exec=True (all columns cached)" on re-execution.
    """
    import os
    from buckaroo.file_cache.cache_utils import clear_file_cache
    from buckaroo.file_cache.sqlite_file_cache import SQLiteFileCache
    from buckaroo.file_cache.sqlite_log import SQLiteExecutorLog
    
    # Reset global instances to use temp directory
    import buckaroo.file_cache.cache_utils as cache_utils_module
    cache_utils_module._file_cache = None
    cache_utils_module._executor_log = None
    
    original_home = os.environ.get('HOME')
    os.environ['HOME'] = str(tmp_path)
    
    try:
        # Create test file
        test_file = tmp_path / "test.csv"
        df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        df.write_csv(test_file)
        
        # Use SQLite cache and log (matching production)
        fc = SQLiteFileCache(str(tmp_path / "file_cache.sqlite"))
        executor_log = SQLiteExecutorLog(str(tmp_path / "executor_log.sqlite"))
        
        cache_utils_module._file_cache = fc
        cache_utils_module._executor_log = executor_log
        
        clear_file_cache()
        
        ldf = df.lazy()
        
        notes: list[ProgressNotification] = []
        def listener(p: ProgressNotification):
            notes.append(p)
        
        # First execution - should compute and send notifications
        column_executor = SimpleColumnExecutor()
        exc1 = MultiprocessingExecutor(
            ldf, column_executor, listener, fc,
            executor_log=executor_log,
            file_path=test_file,
            timeout_secs=5.0,
            async_mode=False
        )
        exc1.run()
        
        # First execution should send notifications for both columns
        assert len(notes) == 2, f"First execution should send 2 notifications, got {len(notes)}"
        assert all(n.success for n in notes), "All notifications should be successful"
        
        # Verify series results are in cache (executor caches by series hash)
        # We can't easily check file_cache directly, but we know results were cached
        # because they were upserted during execution
        
        # Reset for second execution
        notes.clear()
        
        # Second execution - should skip all columns (no_exec=True)
        column_executor2 = SimpleColumnExecutor()
        
        notes2: list[ProgressNotification] = []
        def listener2(p: ProgressNotification):
            notes2.append(p)
        
        exc2 = MultiprocessingExecutor(
            ldf, column_executor2, listener2, fc,
            executor_log=executor_log,
            file_path=test_file,
            timeout_secs=5.0,
            async_mode=False
        )
        exc2.run()
        
        # Second execution should NOT send notifications (columns are cached and skipped)
        # The executor should skip execution entirely when all columns are cached
        assert len(notes2) == 0, (
            f"Second execution should skip all columns (no_exec=True), "
            f"but got {len(notes2)} notifications: {notes2}"
        )
        
    finally:
        cache_utils_module._file_cache = None
        cache_utils_module._executor_log = None
        if original_home:
            os.environ['HOME'] = original_home


            
