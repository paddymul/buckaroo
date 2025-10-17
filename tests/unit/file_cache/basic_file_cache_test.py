#from buckaroo.file_cache import base
from buckaroo.file_cache.base import ColGroup, ProgressNotification, ColumnResults, ColumnResult, FileCache, Executor
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


def simple_column_func(ldf:pl.LazyFrame, cols:ColGroup) -> ColumnResults:
    """
      a very simple column_func that just returns series_hash and len of each column

      eventually this will be replaced by a closure over pluggable analysis framework

      """

    only_cols_ldf = ldf.select(cols)
    res = only_cols_ldf.select(
    pl.all().pl_series_hash.hash_xx().name.suffix("_hash"),
    #pl.col(pl.NUMERIC_DTYPES)
    cs.numeric().sum().name.suffix("_sum"),
    pl.all().len().name.suffix("_len")).collect()
    
    col_results:ColumnResults = {}
    for col in cols:

        hash_:int = cast(int, res[col+"_hash"][0])
        if col+"_sum" in res.columns:
            actual_result = {'len':res[col+"_len"][0], 'sum':res[col+"_sum"][0] }
        else:
            actual_result = {'len':res[col+"_len"][0]}
            
        cr = ColumnResult(
            series_hash=hash_,
            column_name=col,
            expressions=[],
            result=actual_result)
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


    exc = Executor(ldf, simple_column_func, [], listener, fc)
    exc.run()
    assert call_count[0] == 2
    assert fc.get_series_results(13038993034761730339) == {'len':3, 'sum':60}

    assert fc.get_series_results(1505513022777147474) == {'len':3}


def test_simple_executor_listener_calls():
    fc = FileCache()
    call_args = []
    def listener(progress:ProgressNotification) -> None:
        call_args.append(progress)

    exc = Executor(ldf, simple_column_func, [], listener, fc)
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
    assert len(call_args) == 2
    assert call_args[0] == expected_notification_1

#def test_series_

"""
test how the file cache bits work, at least for in memory.

  

  figure out how to check that a series isn't hashed twice


  figure out hwo to do partial cache updates and plumb that in  AnalysisDAG

  AnalysisDag needs to alter the queries/code run based on what is already in the cache


  tests around the log functionality

  tests around the exception catching

  bisect functionality
  
  

  """
