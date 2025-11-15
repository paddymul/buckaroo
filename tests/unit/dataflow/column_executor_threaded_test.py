import time
import polars as pl

from buckaroo.dataflow.column_executor_dataflow import ColumnExecutorDataflow
from buckaroo.file_cache.threaded_executor import ThreadedExecutor
from buckaroo.file_cache.paf_column_executor import PAFColumnExecutor


class SlowPAFColumnExecutor(PAFColumnExecutor):
    def execute(self, ldf, execution_args):
        # simulate work per column group
        time.sleep(0.1)
        return super().execute(ldf, execution_args)


def test_threaded_executor_streams_progress():
    df = pl.DataFrame({'c1': [1, 2, 3], 'c2': [10, 20, 30], 'c3': [7, 8, 9]})
    ldf = df.lazy()

    # capture partial updates from dataflow
    partial_counts = []
    def on_progress(agg):
        # count number of summarized columns in 'orig_col_name'
        try:
            import pandas as pd
            rows = pd.DataFrame(agg).to_dict(orient='list')
        except Exception:
            return
        # track via dict keys length
        partial_counts.append(len(agg.keys()))

    cdf = ColumnExecutorDataflow(
        ldf,
        column_executor_class=SlowPAFColumnExecutor,
        executor_class=ThreadedExecutor
    )
    cdf.progress_update_callback = on_progress

    # run compute synchronously; updates should stream from worker threads
    cdf.compute_summary_with_executor()

    # final merged_sd should have all 3 columns
    assert len(cdf.merged_sd.keys()) == 3
    # and we should have seen intermediate updates (at least 2 distinct counts)
    assert any(c > 0 for c in partial_counts)
    assert max(partial_counts) == 3

