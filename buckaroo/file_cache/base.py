from datetime import datetime as dtdt
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, TypeAlias, Callable, cast, List, Dict, Tuple
import polars as pl
from pl_series_hash import hash_xx
import itertools

now = dtdt.now


SummaryStats:TypeAlias = dict[str, Any]

SimpleBufferKey:TypeAlias = tuple[int, int, int]
ComplexBufferKey:TypeAlias = tuple[SimpleBufferKey, SimpleBufferKey, SimpleBufferKey]
#BufferKey:TypeAlias = SimpleBufferKey|ComplexBufferKey
BufferKey = ComplexBufferKey 

def flatten(*lists):
    list(itertools.chain(*nested_list))
class FileCache:
    """
      acutally as written this is more like an in memory cache
      """
    def __init__(self) -> None:
        self.file_cache: dict[str, int] = {}
        self.summary_stats_cache: dict[int, Any] = {}
        self.series_hash_cache: dict[BufferKey, int] = {}

        
    def add_file(self, path:Path) -> None:
        pass

    def check_file(self, path:Path) -> bool :
        """
          is this path in the cache
          is the mtime of this file before the mtime in the cache for this file
          """
        return False

    def get_hashes(self, path:Path):
        """
          return the hashes for this file if available

          hashes only or maybe hashes and column names???
          """
        pass
    
    def upsert_key(self, series_hash:int, result:SummaryStats) -> None:
        existing_result = self.summary_stats_cache.get(series_hash, {})
        existing_result.update(result)
        self.summary_stats_cache[series_hash] = existing_result

    def get_series_results(self, series_hash:int) -> SummaryStats|None:
        return self.summary_stats_cache.get(series_hash, None)

    def _get_buffer_key(self, series:pl.Series) -> BufferKey:
        """

          This kind of works.  We want dataframe and series level metadata
          https://github.com/pola-rs/polars/issues/5117
          these aren't implemented yet
          """

        buffers = series._get_buffers()
        if 'validity' in buffers and buffers['validity'] is not None:
            validity:SimpleBufferKey = buffers['validity']._get_buffer_info()
        else:
            validity:SimpleBufferKey = (0,0,0,)
        if 'offsets' in buffers and buffers['offsets'] is not None:
            offsets:SimpleBufferKey = buffers['offsets']._get_buffer_info()
        else:
            offsets:SimpleBufferKey = (0,0,0,)
        values = buffers['values']._get_buffer_info()
        
        # assert isinstance(values, tuple)
        # assert len(values) == 3
        # assert isinstance(validity, tuple)
        # assert len(validity) == 3
        # assert isinstance(offsets, tuple)
        # assert len(offsets) == 3

        return tuple([values, validity, offsets])
    
    def check_series(self, series:pl.Series) -> bool:
        """
        Do we have a series_hash for this series (based on it's memory address)  

          """
        key = self._get_buffer_key(series)
        existing = list(self.series_hash_cache.keys())
        #print("key", key, "existing", existing, "in", key in existing)
        return key in self.series_hash_cache

    def add_series(self, series:pl.Series, col=None) -> None:
        """
          make sure that the hash for this in memory series is put in the local hash cache

          we can't attach metadata to a series, but we can track the series by memory location
          """
        # if col:
        #     print("add col", col, self._get_buffer_key(series))
        if not self.check_series(series):
            buffer_info = self._get_buffer_key(series)
            df = pl.DataFrame({'a':series})
            res = df.select(pl.col('a').pl_series_hash.hash_xx())
            self.series_hash_cache[buffer_info] = res['a'][0]

    def add_df(self, df:pl.DataFrame) -> None:
        for col in df.columns:
            self.add_series(df[col], col)
        


        
class AnnotatedFile:

    def get_metadata(self):

        """
          mtime at least
          maybe column list
          maybe hashes for columns
          """
        pass
    


# call PlugableAnalysisFramework2 TypedAnalysisDAG    
class PAF2:
    """
      Plugable analys framework 2

      figures out provides/requires from type hints.  DataClasses or type hints used

      add a function decorator for defaults provided in case of function failure

      add a function decorator for defaults required in case of upstream failure

      """
    pass




"""
pseudo code implementation

  make sure to use OpenAI

add rex=execution to foind error columsn/rwos

  split ldf by rows and columns and se if a failure reporduce

  write rust/crash/panic plugin that determinatcally fails this lets us check this type of 

  """

ColGroup:TypeAlias = list[str]

@dataclass
class ProgressNotification:
    # how do we get a failure notification when it results in a crash?
    success: bool
    col_group:ColGroup
    execution_args: Any
    result: Any
    execution_time: int # millisecones?
    failure_message: str|None

    def __eq__(self, other):
        props = [self.success == other.success,
                 tuple(self.col_group) == tuple(other.col_group),
                 self.execution_args == other.execution_args,
                 self.result == other.result,
                 self.failure_message == other.failure_message]
        return all(props)
            

ProgressListener:TypeAlias = Callable[[ProgressNotification], None]

@dataclass
class ColumnResult:
    series_hash: int #u64 actually
    column_name: str # strictly necessary?
    expressions: list[pl.Expr]
    # I want expressions in plass of execution_args
    # expression names are fine for expressions,  everything else should fall to theColAnalyis class name
    
    result: dict[str, Any] #

ColumnResults:TypeAlias = Dict[str, ColumnResult]    
ColumnFunc:TypeAlias = Callable[[pl.LazyFrame, ColGroup], ColumnResults]


def simple_column_func(ldf:pl.LazyFrame, cols:ColGroup) -> ColumnResults:
    """
      a very simple column_func that just returns series_hash and len of each column

      eventually this will be replaced by a closure over pluggable analysis framework

      """

    only_cols_ldf = ldf.select([cols])
    res = only_cols_ldf.select(
    pl.all().pl_series_hash.hash_xx().suffix("_hash"),
    pl.all().len().suffix("_len")).collect()

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
            

class Executor:

    def __init__(self,
        ldf:pl.LazyFrame, column_func:ColumnFunc,
        expressions: list[pl.Expr],
        listener:ProgressListener, fc:FileCache) -> None:
        self.ldf = ldf
        self.column_func = column_func
        self.listener = listener
        self.expressions = expressions
        self.fc = fc


    def run(self) -> None:

        for col_group in self.get_column_chunks():
            if self.check_log_for_previous_failure(col_group):
                log_fail_result = dict()
                for col in col_group:
                    log_fail_result[col] = ColumnResult(
                        series_hash=0, #it's unclear if we can get a series hash in failure case
                        column_name=col,
                        expressions=self.expressions,
                    result=dict())
            
            self.log_start_col_group(col_group)
            t1 = now()

            try:
                res = self.exec_column_group(col_group)
                t2 = now()
                notification = ProgressNotification(
                    success=True,
                    col_group=col_group,
                    execution_args=[str(ex) for ex in self.expressions],
                    result=res,
                    execution_time=t2-t1,
                    failure_message=None)

                for col, col_result in res.items():
                    self.fc.upsert_key(col_result.series_hash, col_result.result)

                self.listener(notification)
                self.log_end_col_group(col_group)
            except Exception as e:
                t3 = now()
                notification = ProgressNotification(
                    success=True,
                    col_group=col_group,
                    execution_args=[str(ex) for ex in self.expressions],
                    result=None,
                    execution_time=t3-t1,
                    failure_message=str(e))
                print("e", e)
                raise
                
                
    def exec_column_group(self, columns:ColGroup) -> ColumnResults:
        return self.column_func(self.ldf, columns)

    def log_start_col_group(self, columns:list[str]) -> None:
        """
          used so we know that we started execution of a col_group even if it crashes
          """
        pass

    def log_end_col_group(self, columns:list[str]) -> None:
        """
          used so we know that execution finished, Maybe include status
          """
        pass

    def check_log_for_previous_failure(self, columns:ColGroup) -> bool:
        """
          check the log for this lazy_dataframe, this set of columns, and this set of column_args
          did it start and not finish, if so, return false
          
          """
        return False

    def get_column_chunks(self) -> list[ColGroup]:
        """
          dumb impl
          """
        return [[column] for column in self.ldf.columns]

    
fc = FileCache()    

def pseudo(fname:str) -> None:
    fpath = Path(fname)
    lazy_df = pl.scan_parquet(fpath)
    if fc.check_file(Path(fname)):
        summary_stats = fc.get_hashes(fpath)
        #PolarsBuckaroo(lazy_df, summary_stats)
    else:
        #PolarsBuckarooTableOnly(lazy_df, None)
        def listener(progress:ProgressNotification) -> None:
            print(progress.success, progress.result)

        exc = Executor(lazy_df, simple_column_func, [], listener, fc)
        exc.run()
        
"""
Goals:
  be able to interogate the execution log and basically run git-bisect until you get to the minimal reproducable failure.

  this implementation is synchronous and simple

  Future implementtions will work out of process.  Hoepfully multiprocessing works
  

  """
        
        

    
# key ((4695495808, 0, 3), (0, 0, 0), (0, 0, 0)) 
# [((4695495808, 0, 3), (0, 0, 0), (0, 0, 0)), ((5182046224, 0, 9), (0, 0, 0), (4695495904, 0, 4))] in True

# key ((4966039552, 0, 9), (0, 0, 0), (4695495904, 0, 4)) 
# existing [((4695495808, 0, 3), (0, 0, 0), (0, 0, 0)), ((5182046224, 0, 9), (0, 0, 0), (4695495904, 0, 4))] in False
