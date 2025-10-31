from datetime import timedelta, datetime as dtdt
from typing import cast

import polars as pl
import polars.selectors as cs

from buckaroo.file_cache.base import (
    ColumnExecutor,
    ExecutorArgs,
    ColumnResults,
    ColumnResult,
    FileCache,
    Executor,
    ProgressNotification,
    get_columns_from_args,
    ExecutorLogEvent,
    SimpleExecutorLog,
)
from buckaroo.file_cache.bisector import (
    ExpressionBisector,
    ColumnBisector,
    RowRangeBisector,
    SamplingRowBisector,
)


class SimpleColumnExecutor(ColumnExecutor[ExecutorArgs]):
    def get_execution_args(self, existing_stats:dict[str,dict[str,object]]) -> ExecutorArgs:
        columns = list(existing_stats.keys())
        return ExecutorArgs(
            columns=columns,
            column_specific_expressions=False,
            include_hash=True,
            expressions=[
                pl.all().pl_series_hash.hash_xx().name.suffix("_hash"),
                cs.numeric().sum().name.suffix("_sum"),
                pl.all().len().name.suffix("_len"),
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
            hash_: int = cast(int, res[col+"_hash"][0])
            if col+"_sum" in res.columns:
                actual_result = {"len": res[col+"_len"][0], "sum": res[col+"_sum"][0]}
            else:
                actual_result = {"len": res[col+"_len"][0]}
            cr = ColumnResult(
                series_hash=hash_,
                column_name=col,
                expressions=[],
                result=actual_result,
            )
            col_results[col] = cr
        return col_results


class FailOnHashExecutor(SimpleColumnExecutor):
    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        cols = execution_args.columns
        only_cols_ldf = ldf.select(cols)
        res = only_cols_ldf.select(*execution_args.expressions).collect()
        for col in res.columns:
            if col.endswith("_hash"):
                1/0
        col_results: ColumnResults = {}
        fallback_len = only_cols_ldf.select(pl.len().alias("n")).collect()["n"][0]
        for col in cols:
            hash_val = res[col+"_hash"][0] if col+"_hash" in res.columns else 0
            len_val = res[col+"_len"][0] if col+"_len" in res.columns else fallback_len
            actual_result = {"len": len_val}
            if col+"_sum" in res.columns:
                actual_result["sum"] = res[col+"_sum"][0]
            cr = ColumnResult(
                series_hash=int(hash_val),
                column_name=col,
                expressions=[],
                result=actual_result,
            )
            col_results[col] = cr
        return col_results


class FailOnHashOrSumExecutor(SimpleColumnExecutor):
    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        cols = execution_args.columns
        only_cols_ldf = ldf.select(cols)
        res = only_cols_ldf.select(*execution_args.expressions).collect()
        for col in res.columns:
            if col.endswith("_sum") or col.endswith("_hash"):
                1/0
        col_results: ColumnResults = {}
        fallback_len = only_cols_ldf.select(pl.len().alias("n")).collect()["n"][0]
        for col in cols:
            hash_val = res[col+"_hash"][0] if col+"_hash" in res.columns else 0
            len_val = res[col+"_len"][0] if col+"_len" in res.columns else fallback_len
            actual_result = {"len": len_val}
            if col+"_sum" in res.columns:
                actual_result["sum"] = res[col+"_sum"][0]
            cr = ColumnResult(
                series_hash=int(hash_val),
                column_name=col,
                expressions=[],
                result=actual_result,
            )
            col_results[col] = cr
        return col_results


class FailOnSumExecutor(SimpleColumnExecutor):
    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        cols = execution_args.columns
        only_cols_ldf = ldf.select(cols)
        res = only_cols_ldf.select(*execution_args.expressions).collect()
        for col in res.columns:
            if col.endswith("_sum"):
                1/0
        col_results: ColumnResults = {}
        fallback_len = only_cols_ldf.select(pl.len().alias("n")).collect()["n"][0]
        for col in cols:
            hash_val = res[col+"_hash"][0] if col+"_hash" in res.columns else 0
            len_val = res[col+"_len"][0] if col+"_len" in res.columns else fallback_len
            actual_result = {"len": len_val}
            if col+"_sum" in res.columns:
                actual_result["sum"] = res[col+"_sum"][0]
            cr = ColumnResult(
                series_hash=int(hash_val),
                column_name=col,
                expressions=[],
                result=actual_result,
            )
            col_results[col] = cr
        return col_results


class FailOnColumnExecutor(SimpleColumnExecutor):
    def __init__(self, bad_col: str) -> None:
        super().__init__()
        self.bad_col = bad_col
    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        if self.bad_col in execution_args.columns:
            1/0
        return super().execute(ldf, execution_args)


class RowRangeAwareFailingExecutor(SimpleColumnExecutor):
    def __init__(self, start_bad: int=3, end_bad:int=7) -> None:
        super().__init__()
        self.start_bad = start_bad
        self.end_bad = end_bad

    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        rs = execution_args.row_start
        re = execution_args.row_end
        if rs is None or re is None:
            1/0
        if rs <= self.start_bad and re >= self.end_bad:
            1/0
        return super().execute(ldf, execution_args)


df = pl.DataFrame({
    'a1': [10,20,30],
    'b2': ["foo", "bar", "baz"]
})
ldf = df.lazy()


def _expr_labels(exprs:list[pl.Expr]) -> set[str]:
    labels:set[str] = set()
    for e in exprs:
        s = str(e)
        if 'sum()' in s:
            labels.add('sum')
        elif 'count()' in s:
            labels.add('len')
        elif 'hash_series' in s or 'hash_xx' in s:
            labels.add('hash')
    return labels


def test_bisect():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        pass

    exc = Executor(ldf, FailOnSumExecutor(), listener, fc)
    exc.run()
    evs = exc.executor_log.get_log_events()
    failing_events = [ev for ev in evs if ev.completed == False]
    assert len(failing_events) >= 1
    fail_input = failing_events[0]

    bi = ExpressionBisector(fail_input, exc.executor_log, FailOnSumExecutor(), ldf)
    fail_ev, success_ev = bi.run()

    assert fail_ev.completed == False
    assert len(fail_ev.args.expressions) == 1
    fail_cols = get_columns_from_args(ldf, fail_ev.args)
    assert fail_cols == ['a1_sum']
    assert _expr_labels(fail_ev.args.expressions) == {'sum'}

    assert success_ev.completed == True
    succ_cols = set(get_columns_from_args(ldf, success_ev.args))
    assert succ_cols == {'a1_hash', 'a1_len'}
    assert _expr_labels(success_ev.args.expressions) == {'hash','len'}


def test_bisector_multiple_failing_expressions():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        pass

    exc = Executor(ldf, FailOnHashOrSumExecutor(), listener, fc)
    exc.run()
    evs = exc.executor_log.get_log_events()
    failing_events = [ev for ev in evs if ev.completed == False]
    assert len(failing_events) >= 1
    fail_input = failing_events[0]

    bi = ExpressionBisector(fail_input, exc.executor_log, FailOnHashOrSumExecutor(), ldf)
    fail_ev, success_ev = bi.run()

    assert fail_ev.completed == False
    assert len(fail_ev.args.expressions) == 1
    fail_cols = set(get_columns_from_args(ldf, fail_ev.args))
    assert fail_cols in ({'a1_hash'}, {'a1_sum'})
    assert _expr_labels(fail_ev.args.expressions) in ({'hash'}, {'sum'})

    assert success_ev.completed == True
    succ_cols = set(get_columns_from_args(ldf, success_ev.args))
    assert succ_cols == {'a1_len'}
    assert _expr_labels(success_ev.args.expressions) == {'len'}


def test_bisector_on_success_event_noop():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        pass

    exc = Executor(ldf, SimpleColumnExecutor(), listener, fc)
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    success_input = ExecutorLogEvent(
        dfi=exc.dfi,
        args=starting_args,
        start_time=dtdt.now(),
        end_time=dtdt.now(),
        completed=True,
    )

    bi = ExpressionBisector(success_input, exc.executor_log, SimpleColumnExecutor(), ldf)
    fail_ev, success_ev = bi.run()

    assert success_ev.completed == True
    assert fail_ev.completed == True
    succ_cols = set(get_columns_from_args(ldf, success_ev.args))
    fail_cols = set(get_columns_from_args(ldf, fail_ev.args))
    assert succ_cols == {'a1_hash', 'a1_sum', 'a1_len', 'b2_hash', 'b2_len'}
    assert fail_cols == {'a1_hash', 'a1_sum', 'a1_len', 'b2_hash', 'b2_len'}
    assert _expr_labels(success_ev.args.expressions) == {'hash','sum','len'}
    assert _expr_labels(fail_ev.args.expressions) == {'hash','sum','len'}


def test_column_bisector():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        pass
    exc = Executor(ldf, FailOnColumnExecutor('a1'), listener, fc)
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    starting_ev = ExecutorLogEvent(
        dfi=exc.dfi,
        args=starting_args,
        start_time=dtdt.now(),
        end_time=None,
        completed=False,
    )
    bi = ColumnBisector(starting_ev, exc.executor_log, FailOnColumnExecutor('a1'), ldf)
    fail_ev, success_ev = bi.run()
    assert fail_ev.completed == False
    assert success_ev.completed == True
    assert fail_ev.args.columns == ['a1']
    assert success_ev.args.columns == ['b2']
    # Expressions should be recomputed for the chosen columns only
    fail_cols = set(get_columns_from_args(ldf, fail_ev.args))
    succ_cols = set(get_columns_from_args(ldf, success_ev.args))
    assert fail_cols == {'a1_hash', 'a1_len'} or fail_cols == {'a1_hash', 'a1_len', 'a1_sum'}
    assert 'b2_hash' not in fail_cols and 'b2_len' not in fail_cols
    assert succ_cols == {'b2_hash', 'b2_len'} or succ_cols == {'b2_hash', 'b2_len', 'b2_sum'}


def test_column_bisector_on_success_event_noop():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        pass
    exc = Executor(ldf, SimpleColumnExecutor(), listener, fc)
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    starting_ev = ExecutorLogEvent(
        dfi=exc.dfi,
        args=starting_args,
        start_time=dtdt.now(),
        end_time=dtdt.now(),
        completed=True,
    )
    bi = ColumnBisector(starting_ev, exc.executor_log, SimpleColumnExecutor(), ldf)
    fail_ev, success_ev = bi.run()
    assert fail_ev.completed == True
    assert success_ev.completed == True
    assert fail_ev.args.columns == ['a1','b2']
    assert success_ev.args.columns == ['a1','b2']


def test_row_range_bisector_minimal_and_success():
    df2 = pl.DataFrame({
        'original_row': list(range(10)),
        'a1': list(range(10)),
        'b2': [str(i) for i in range(10)],
    })
    ldf2 = df2.lazy()
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    starting_ev = ExecutorLogEvent(
        dfi=(id(ldf2), ''),
        args=starting_args,
        start_time=dtdt.now(),
        end_time=None,
        completed=False,
    )
    rr = RowRangeBisector(starting_ev, SimpleExecutorLog(), RowRangeAwareFailingExecutor(), ldf2)  # type: ignore
    fail_ev, success_ev = rr.run()
    assert fail_ev.completed == False
    assert success_ev.completed == True
    assert fail_ev.args.row_start == 3
    assert fail_ev.args.row_end == 7
    assert (success_ev.args.row_start, success_ev.args.row_end) in [(0,3), (7,10)]

def test_row_range_bisector_minimal_and_successB():
    df2 = pl.DataFrame({
        'a1': list(range(10)),
        'b2': [str(i) for i in range(10)],
    })
    ldf2 = df2.lazy()
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = RowRangeAwareFailingExecutor().get_execution_args(existing_stats)  # type: ignore
    starting_ev = ExecutorLogEvent(
        dfi=(id(ldf2), ''),
        args=starting_args,
        start_time=dtdt.now(),
        end_time=None,
        completed=False,
    )
    rr = RowRangeBisector(starting_ev, SimpleExecutorLog(), RowRangeAwareFailingExecutor(), ldf2)  # type: ignore
    fail_ev, success_ev = rr.run()
    assert fail_ev.completed == False
    assert success_ev.completed == True
    assert fail_ev.args.row_start == 3
    assert fail_ev.args.row_end == 7
    assert (success_ev.args.row_start, success_ev.args.row_end) in [(0,3), (7,10)]

def test_row_range_bisector_minimal_and_success2():
    df2 = pl.DataFrame({
        'a1': list(range(100)),
        'b2': [str(i) for i in range(100)],
    })
    ldf2 = df2.lazy()
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    starting_ev = ExecutorLogEvent(
        dfi=(id(ldf2), ''),
        args=starting_args,
        start_time=dtdt.now(),
        end_time=None,
        completed=False,
    )
    rr = RowRangeBisector(starting_ev, SimpleExecutorLog(), RowRangeAwareFailingExecutor(27, 63), ldf2)  # type: ignore
    fail_ev, success_ev = rr.run()
    assert fail_ev.completed == False
    assert success_ev.completed == True
    assert fail_ev.args.row_start == 27
    assert fail_ev.args.row_end == 63
    assert (success_ev.args.row_start, success_ev.args.row_end) in [(0,27), (63,100)]

def test_row_range_bisector_minimal_and_success3():
    df2 = pl.DataFrame({
        'a1': list(range(100)),
        'b2': [str(i) for i in range(100)],
    })
    ldf2 = df2.lazy()
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    starting_ev = ExecutorLogEvent(
        dfi=(id(ldf2), ''),
        args=starting_args,
        start_time=dtdt.now(),
        end_time=None,
        completed=False,
    )
    rr = RowRangeBisector(starting_ev, SimpleExecutorLog(), RowRangeAwareFailingExecutor(0, 33), ldf2)  # type: ignore
    fail_ev, success_ev = rr.run()
    assert fail_ev.completed == False
    assert success_ev.completed == True
    assert fail_ev.args.row_start == 0
    assert fail_ev.args.row_end == 33
    assert (success_ev.args.row_start, success_ev.args.row_end) == (33,100)

    

def test_row_range_bisector_on_success_event_noop():
    df2 = pl.DataFrame({
        'original_row': list(range(10)),
        'a1': list(range(10)),
        'b2': [str(i) for i in range(10)],
    })
    ldf2 = df2.lazy()
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    success_ev = ExecutorLogEvent(
        dfi=(id(ldf2), ''),
        args=starting_args,
        start_time=dtdt.now(),
        end_time=dtdt.now(),
        completed=True,
    )
    rr = RowRangeBisector(success_ev, SimpleExecutorLog(), RowRangeAwareFailingExecutor(), ldf2)  # type: ignore
    fev, sev = rr.run()
    assert fev.completed == True
    assert sev.completed == True


class RowSetAwareFailingExecutor(SimpleColumnExecutor):
    """
      Fails only when both rows 0 and 6 are included in args.extra['row_indices'].
      If 'row_indices' not provided, treat as full set present (fail).
      """

    def __init__(self, bad_rows: list[int]) -> None:
        super().__init__()
        self.bad_rows = bad_rows


    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        present_rows = set(pl.DataFrame(ldf.select(pl.col('original_row')).collect())['original_row'].to_list())
        if set(self.bad_rows).issubset(present_rows):
            1/0
        return super().execute(ldf, execution_args)


def test_sampling_row_bisector_minimal_pair():
    df2 = pl.DataFrame({
        'original_row': list(range(100)),
        'a1': list(range(100)),
        'b2': [str(i) for i in range(100)],
    })
    ldf2 = df2.lazy()
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    starting_ev = ExecutorLogEvent(
        dfi=(id(ldf2), ''),
        args=starting_args,
        start_time=dtdt.now(),
        end_time=None,
        completed=False,
    )
    sb = SamplingRowBisector(starting_ev, SimpleExecutorLog(), RowSetAwareFailingExecutor([0,6]), ldf2)  # type: ignore
    fail_ev, success_ev = sb.run()
    assert fail_ev.completed == False
    assert success_ev.completed == True
    # minimal failing set should be exactly rows {0,6}
    row_indices = set(fail_ev.args.extra['row_indices'])  # type: ignore
    assert row_indices == {0,6}
    succ_indices = set(success_ev.args.extra['row_indices'])  # type: ignore
    assert not ({0,6}.issubset(succ_indices))
    assert len(succ_indices) < 100


def test_sampling_row_bisector_on_success_event_noop():
    df2 = pl.DataFrame({
        'original_row': list(range(100)),
        'a1': list(range(100)),
        'b2': [str(i) for i in range(100)],
    })
    ldf2 = df2.lazy()
    existing_stats = {'a1':{}, 'b2':{}}
    starting_args = SimpleColumnExecutor().get_execution_args(existing_stats)  # type: ignore
    success_ev = ExecutorLogEvent(
        dfi=(id(ldf2), ''),
        args=starting_args,
        start_time=dtdt.now(),
        end_time=dtdt.now(),
        completed=True,
    )
    sb = SamplingRowBisector(success_ev, SimpleExecutorLog(), RowSetAwareFailingExecutor([0,6]), ldf2)  # type: ignore
    fev, sev = sb.run()
    assert fev.completed == True
    assert sev.completed == True


