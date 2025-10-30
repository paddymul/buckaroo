#from buckaroo.file_cache import base
from buckaroo.file_cache.base import (
    ColumnExecutor,
    ExecutorArgs,
    ColumnResults,
    ColumnResult,
    FileCache,
    Executor,
    ProgressNotification,
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



class FailOnSumExecutor(SimpleColumnExecutor):
    """
      used for testing to test bisect for failures
      """
    def execute(self, ldf:pl.LazyFrame, execution_args:ExecutorArgs) -> ColumnResults:
        cols = execution_args.columns
        only_cols_ldf = ldf.select(cols)
        res = only_cols_ldf.select(*execution_args.expressions).collect()
        for col in columns:
            if col.endswith("_sum"):
                1/0
                
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

    
df = pl.DataFrame({
    'a1': [10,20,30],
    'b2': ["foo", "bar", "baz"]
    })
ldf = df.lazy()
        
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

    assert len(evs) == 1
    ev = evs[0]

    assert ev.completed == True

    expected_executor_args = None # don't know what this should be, please fill in
    assert expected_executor_args == ev.args
    
    #verify that series are saved to cache, and that we can retrieve them with expected result
    assert fc.get_series_results(13038993034761730339) == {'len':3, 'sum':60}
    assert fc.get_series_results(1505513022777147474) == {'len':3}

# def test_simple_executor_on_fail():
#     fc = FileCache()
#     def listener(progress:ProgressNotification) -> None:
#         print("here58", progress.success, progress.result)


#     exc = Executor(ldf, SimpleColumnExecutor(), listener, fc)
#     exc.run()
#     evs = exc.executor_log.get_log_events() 

#     assert evs.length == 1
#     ev = evs[0]

#     assert ev.completed == True

#     expected_executor_args = None # don't know what this should be, please fill in
#     assert expected_executor_args == ev.args
    
#     #verify that series are saved to cache, and that we can retrieve them with expected result
#     assert fc.get_series_results(13038993034761730339) == {'len':3, 'sum':60}
#     assert fc.get_series_results(1505513022777147474) == {'len':3}

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
