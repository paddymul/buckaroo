#from buckaroo.file_cache import base
from buckaroo.file_cache.base import ColGroup, ProgressNotification, ColumnResults, ColumnResult, FileCache, Executor
import polars as pl
from typing import cast
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
    pl.all().len().name.suffix("_len")).collect()
    
    col_results:ColumnResults = {}
    for col in cols:

        hash_:int = cast(int, res[col+"_hash"][0])
        cr = ColumnResult(
            series_hash=hash_,
            column_name=col,
            expressions=[],
            result={'len':res[col+"_len"][0]})
        col_results[col] = cr
    return col_results

        
def test_simple_executor():

    df = pl.DataFrame({
        'a1': [10,20,30],
        'b2': ["foo", "bar", "baz"]
        })
    ldf = df.lazy()

    fc = FileCache()
    call_count = [0]
    def listener(progress:ProgressNotification) -> None:
        print("here58", progress.success, progress.result)
        call_count[0]+=1


    exc = Executor(ldf, simple_column_func, [], listener, fc)
    exc.run()

    assert call_count[0] == 2
    
