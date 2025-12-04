"""
Test that cache prevents recomputation on re-execution.
"""
# state:READONLY

from buckaroo.file_cache.cache_utils import get_global_file_cache
from buckaroo.read_utils import read_df
from tests.unit.file_cache.test_fixtures import (
    isolated_cache,
    create_test_csv,
    create_widget_with_sync_executor,
    track_executor_calls,
)


def test_cache_prevents_recomputation_on_second_execution(tmp_path):
    """Test that when a file is cached, second execution doesn't recompute stats."""
    with isolated_cache(tmp_path):
        # Create test file
        test_file = create_test_csv(tmp_path, "test.csv", {
            'a': [1, 2, 3],
            'b': [4, 5, 6]
        })
        
        with track_executor_calls() as tracker:
            # First execution - should compute
            ldf1 = read_df(str(test_file))
            w1 = create_widget_with_sync_executor(ldf1, test_file)
            
            first_run_calls = len(tracker['run_calls'])
            first_execute_calls = len(tracker['execute_calls'])
            print(f"First run - executor.run called {first_run_calls} times, execute called {first_execute_calls} times")
            assert first_run_calls == 1, "Executor.run should have been called on first run"
            # With 2 columns, we get 2 execute calls (one per column group)
            assert first_execute_calls == 2, f"Executor should have executed computation for 2 columns, got {first_execute_calls}"
            
            # Verify stats were computed (2 columns = 2 entries in merged_sd)
            assert len(w1._df.merged_sd) == 2, f"Stats should be computed for 2 columns on first run, got {len(w1._df.merged_sd)}"
            
            # Verify cache was populated
            fc = get_global_file_cache()
            assert fc.check_file(test_file), "File should be in cache after first run"
            md = fc.get_file_metadata(test_file)
            assert md is not None and 'merged_sd' in md, "merged_sd should be in cache"
            
            # Reset executor call counters
            tracker['run_calls'].clear()
            tracker['execute_calls'].clear()
            
            # Second execution - should use cache, NOT recompute
            ldf2 = read_df(str(test_file))
            w2 = create_widget_with_sync_executor(ldf2, test_file)
            
            second_run_calls = len(tracker['run_calls'])
            second_execute_calls = len(tracker['execute_calls'])
            print(f"Second run - executor.run called {second_run_calls} times, execute called {second_execute_calls} times")
            
            # Executor.run() may be called but should return early without executing
            # The important thing is that execute() should NOT be called (no actual computation)
            assert second_execute_calls == 0, (
                f"Executor should NOT execute computation on second run (cache should be used), "
                f"but execute was called {second_execute_calls} times: {tracker['execute_calls']}"
            )
            
            # Verify stats are still available (from cache)
            assert len(w2._df.merged_sd) > 0, "Stats should be available from cache on second run"
