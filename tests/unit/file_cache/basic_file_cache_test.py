#from buckaroo.file_cache import base
from buckaroo.file_cache.base import (
    ColumnExecutor,
    ExecutorArgs,
    ColumnResults,
    ColumnResult,
    FileCache,
    Executor,
    ProgressNotification,
    Bisector,
    get_columns_from_args,
)
import polars as pl
import polars.selectors as cs
from typing import cast
from datetime import timedelta
# fc = FileCache()    

# def pseudo(fname:str) -> None:
#     fpath = Path(fname)
#     lazy_df = pl.scan_parquet(fpath)
#     if fc.check_file(Path(fname)):
#         summary_stats = fc.get_hashes(fpath)
#         #PolarsBuckaroo(lazy_df, summary_stats)
#     else:
#         #PolarsBuckarooTableOnly(lazy_df, None)
#         def listener(progress:ProgressNotification) -> None:
#             print(progress.success, progress.result)

#         exc = Executor(lazy_df, simple_column_func, [], listener, fc)
#         exc.run()

from tempfile import NamedTemporaryFile
from pathlib import Path

def create_tempfile_with_text(text: str) -> Path:
    # File persists after this function (delete=False). Caller should unlink() when done.
    with NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
        f.write(text)
        f.flush()
        temp_path = Path(f.name)
    return temp_path

def test_filecache():
    fc = FileCache()

    path_1 = create_tempfile_with_text("blah_string")
    assert not fc.check_file(path_1) 

    md_1 = {'first_key':9}
    fc.add_metadata(path_1,  md_1)

    assert fc.check_file(path_1)
    assert fc.get_file_metadata(path_1) == md_1

    md_extra = {'second_key': 'bar'}
    fc.upsert_file_metadata(path_1, md_extra)

    assert fc.get_file_metadata(path_1) == {'first_key':9, 'second_key': 'bar'}
    
    open(path_1, "w").write("new_data")
    #this should now fail because path_1 has a newer m_time then what the cache was relevant for
    assert not fc.check_file(path_1) 
    

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
    """
      fails if any resulting column ends with _hash
      """
    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        cols = execution_args.columns
        only_cols_ldf = ldf.select(cols)
        res = only_cols_ldf.select(*execution_args.expressions).collect()
        for col in res.columns:
            if col.endswith("_hash"):
                1/0
        col_results: ColumnResults = {}
        # compute a fallback length if not present
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
    """
      fails if any resulting column ends with _hash or _sum
      """
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
    """
      used for testing to test bisect for failures
      """
    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        cols = execution_args.columns
        only_cols_ldf = ldf.select(cols)
        res = only_cols_ldf.select(*execution_args.expressions).collect()
        for col in res.columns:
            if col.endswith("_sum"):
                1/0
                
        col_results: ColumnResults = {}
        # compute fallbacks when expressions are absent
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

def test_simple_executor():

    fc = FileCache()
    call_count = [0]
    def listener(progress:ProgressNotification) -> None:
        print("here58", progress.success, progress.result)
        call_count[0]+=1


    exc = Executor(ldf, SimpleColumnExecutor(), listener, fc)
    exc.run()
    assert call_count[0] == 2
    #verify that series are saved to cache, and that we can retrieve them with expected result
    assert fc.get_series_results(13038993034761730339) == {'len':3, 'sum':60}
    assert fc.get_series_results(1505513022777147474) == {'len':3}

def test_simple_executor_log():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        print("here58", progress.success, progress.result)


    exc = Executor(ldf, SimpleColumnExecutor(), listener, fc)
    exc.run()
    evs = exc.executor_log.get_log_events() 

    assert len(evs) == 2
    ev = evs[0]

    assert ev.completed == True

    
    #verify that series are saved to cache, and that we can retrieve them with expected result
    assert fc.get_series_results(13038993034761730339) == {'len':3, 'sum':60}
    assert fc.get_series_results(1505513022777147474) == {'len':3}

def test_simple_executor_on_fail():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        print("here58", progress.success, progress.result)


    exc = Executor(ldf, FailOnSumExecutor(), listener, fc)
    exc.run()
    evs = exc.executor_log.get_log_events() 

    assert len(evs) == 2
    ev = evs[0]

    assert ev.completed == False

    assert exc.executor_log.check_log_for_previous_failure(exc.dfi, ev.args) == True

def test_bisect():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        pass

    # produce a failure event (on _sum)
    exc = Executor(ldf, FailOnSumExecutor(), listener, fc)
    exc.run()
    evs = exc.executor_log.get_log_events()
    failing_events = [ev for ev in evs if ev.completed == False]
    assert len(failing_events) >= 1
    fail_input = failing_events[0]

    # run bisector to minimize failing expressions and maximize success
    bi = Bisector(fail_input, exc.executor_log, FailOnSumExecutor(), ldf)
    fail_ev, success_ev = bi.run()

    assert fail_ev.completed == False
    assert len(fail_ev.args.expressions) == 1
    # verify the failing expr is the sum expression (column name ends with _sum)
    fail_cols = get_columns_from_args(ldf, fail_ev.args)
    assert fail_cols == ['a1_sum']
    assert _expr_labels(fail_ev.args.expressions) == {'sum'}

    assert success_ev.completed == True
    # verify the success exprs are hash and len
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

    bi = Bisector(fail_input, exc.executor_log, FailOnHashOrSumExecutor(), ldf)
    fail_ev, success_ev = bi.run()

    # minimal failing set should be one expression (either hash or sum)
    assert fail_ev.completed == False
    assert len(fail_ev.args.expressions) == 1
    fail_cols = set(get_columns_from_args(ldf, fail_ev.args))
    assert fail_cols in ({'a1_hash'}, {'a1_sum'})
    assert _expr_labels(fail_ev.args.expressions) in ({'hash'}, {'sum'})

    # maximal success should then be the remaining safe expression(s); given both hash and sum fail,
    # only len should remain
    assert success_ev.completed == True
    succ_cols = set(get_columns_from_args(ldf, success_ev.args))
    assert succ_cols == {'a1_len'}
    assert _expr_labels(success_ev.args.expressions) == {'len'}


def test_bisector_on_success_event_noop():
    fc = FileCache()
    def listener(progress:ProgressNotification) -> None:
        pass

    exc = Executor(ldf, SimpleColumnExecutor(), listener, fc)
    exc.run()
    evs = exc.executor_log.get_log_events()
    # pick a completed event
    success_input = [ev for ev in evs if ev.completed == True][0]

    bi = Bisector(success_input, exc.executor_log, SimpleColumnExecutor(), ldf)
    fail_ev, success_ev = bi.run()

    # when starting from a success event, both returned events should be success
    assert success_ev.completed == True
    assert fail_ev.completed == True
    succ_cols = set(get_columns_from_args(ldf, success_ev.args))
    fail_cols = set(get_columns_from_args(ldf, fail_ev.args))
    assert succ_cols == {'a1_hash', 'a1_sum', 'a1_len'}
    assert fail_cols == {'a1_hash', 'a1_sum', 'a1_len'}
    assert _expr_labels(success_ev.args.expressions) == {'hash','sum','len'}
    assert _expr_labels(fail_ev.args.expressions) == {'hash','sum','len'}

def test_simple_executor_listener_calls():
    fc = FileCache()
    call_args = []
    def listener(progress:ProgressNotification) -> None:
        call_args.append(progress)

    exc = Executor(ldf, SimpleColumnExecutor(), listener, fc)
    exc.run()

    expected_notification_1 = ProgressNotification(
        success=True,
        col_group=['a1'],
        execution_args=[],
        result={'a1': ColumnResult(
            series_hash=13038993034761730339,
            column_name='a1',
            expressions=[],
            result={'len': 3,
                    'sum': 60})},
        execution_time=timedelta(microseconds=96),
        failure_message=None)
    # our listener function should be called twice
    assert len(call_args) == 2
    
    assert call_args[0] == expected_notification_1

def test_in_memory_cache():
    """
      This is trying to demonstrate caching series from a dataframe that was never written to a file

      it kind of works
      """
    df = pl.DataFrame({
        'a1': [10,20,30],
        'b2': [50,60,80]
        })
    ldf = df.lazy()

    fc = FileCache()
    assert fc.check_series(df['a1']) == False
    assert fc.check_series(df['b2']) == False

    fc.add_df(df)
    assert fc.check_series(df['a1']) == True

    # buffer info for string series is unreliable commented out for now
    # look at polars-core/src/series/buffer.rs::get_buffers_from_string
    #assert fc.check_series(df['b2']) == True

    # I dont even see this reliably working
    #assert not fc._get_buffer_key(df['b2']) == fc._get_buffer_key(df['b2'])

    #this should show that the same physical memory is used by df2['a1'] as df['a1']
    df2 = df.select(pl.col('a1').alias('alias_a1'),
                    pl.col('b2').alias('alias_b2'))
    
    assert fc.check_series(df2['alias_a1']) == True
    #assert fc.check_series(df2['alias_b2']) == True


#def test_series_

"""


  tests around the log functionality


  test around the multiprocess timeout stuff
  


  tests around the exception catching

  bisect functionality


  figure out how to do partial cache updates and plumb that in  AnalysisDAG

  AnalysisDag needs to alter the queries/code run based on what is already in the cache

  add and test LRU logic

  
# Done
    figure out how to check that a series isn't hashed twice  - kinda
  test how the file cache bits work, at least for in memory (not SQLITE).  

  """
