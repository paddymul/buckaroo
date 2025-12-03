from abc import ABC, abstractmethod

from datetime import datetime as dtdt, timedelta
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any, Optional, TypeAlias, Callable, Dict, Literal,
    Generic, TypeVar)
import logging
import polars as pl
import itertools

now = dtdt.now


SummaryStats:TypeAlias = dict[str, Any]

SimpleBufferKey:TypeAlias = tuple[int, int, int]

#ComplexBufferKey:TypeAlias = tuple[SimpleBufferKey, SimpleBufferKey, SimpleBufferKey]
# I don't know why the above line causes errors but the below key works
BufferKey:TypeAlias = tuple[SimpleBufferKey, ...]
                                          #mtime
FileDFIdentifier: TypeAlias = tuple[Path, int]
                                    #id of dataframe, joined string of all columns
MemoryDFIdentifer:TypeAlias = tuple[int, str]
DFIdentifier: TypeAlias = FileDFIdentifier | MemoryDFIdentifer


def flatten(*lists):
    list(itertools.chain(*lists))
    
class AbstractFileCache(ABC):
    """
    Abstract interface for a file/series cache.
    Concrete implementations include an in-memory cache (MemoryFileCache)
    and a SQLite-backed cache (SQLiteFileCache).
    """
    @abstractmethod
    def add_file(self, path:Path, metadata:dict[str, Any]) -> None: ...

    @abstractmethod
    def add_metadata(self, path:Path, metadata:dict[str, Any]) -> None: ...

    @abstractmethod
    def check_file(self, path:Path) -> bool: ...

    @abstractmethod
    def get_file_metadata(self, path:Path) -> Optional[dict[str, Any]]: ...

    @abstractmethod
    def upsert_file_metadata(self, path:Path, extra_metadata:dict[str, Any]) -> None: ...

    @abstractmethod
    def upsert_key(self, series_hash:int, result:SummaryStats) -> None: ...

    @abstractmethod
    def get_series_results(self, series_hash:int) -> SummaryStats|None: ...

    # New: file-level series hash helpers
    @abstractmethod
    def get_file_series_hashes(self, path: Path) -> Optional[dict[str, int]]: ...

    @abstractmethod
    def upsert_file_series_hashes(self, path: Path, hashes: dict[str, int]) -> None: ...


class MemoryFileCache(AbstractFileCache):
    """
      acutally as written this is more like an in memory cache
      """
    def __init__(self) -> None:
        self.file_cache: dict[str, tuple[float, dict[str, Any]]] = {}
        self.summary_stats_cache: dict[int, Any] = {}
        self.series_hash_cache: dict[BufferKey, int] = {}
        
    def add_file(self, path:Path, metadata:dict[str, Any]) -> None:
        """
        Record a file's current mtime along with provided metadata.
        """
        try:
            mtime = path.stat().st_mtime
        except FileNotFoundError:
            # If file does not exist, do not add to cache
            return
        self.file_cache[str(path)] = (mtime, dict(metadata))

    # Compatibility with tests expecting add_metadata/get_file_metadata/upsert_file_metadata
    def add_metadata(self, path:Path, metadata:dict[str, Any]) -> None:
        self.add_file(path, metadata)

    def check_file(self, path:Path) -> bool :
        """
          is this path in the cache
          is the mtime of this file before the mtime in the cache for this file
          """
        key = str(path)
        if key not in self.file_cache:
            return False
        try:
            current_mtime = path.stat().st_mtime
        except FileNotFoundError:
            # If file is gone, consider cache invalid
            return False
        cached_mtime, _ = self.file_cache[key]
        # Valid only if the file has not been modified since it was cached
        return current_mtime <= cached_mtime

    def get_hashes(self, path:Path):
        """
          return the hashes for this file if available

          hashes only or maybe hashes and column names???
          """
        # Placeholder: not used by current tests
        return None

    def get_file_metadata(self, path:Path) -> Optional[dict[str, Any]]:
        key = str(path)
        entry = self.file_cache.get(key)
        if entry is None:
            return None
        _, metadata = entry
        return metadata

    def upsert_file_metadata(self, path:Path, extra_metadata:dict[str, Any]) -> None:
        key = str(path)
        try:
            current_mtime = path.stat().st_mtime
        except FileNotFoundError:
            return
        if key in self.file_cache:
            _, existing_md = self.file_cache[key]
            merged_md: dict[str, Any] = dict(existing_md)
            merged_md.update(extra_metadata)
            # Update mtime to current file mtime to reflect current file state
            self.file_cache[key] = (current_mtime, merged_md)
        else:
            # If not present, behave like add_file with provided metadata
            self.file_cache[key] = (current_mtime, dict(extra_metadata))
    
    def upsert_key(self, series_hash:int, result:SummaryStats) -> None:
        existing_result = self.summary_stats_cache.get(series_hash, {})
        existing_result.update(result)
        self.summary_stats_cache[series_hash] = existing_result

    def get_series_results(self, series_hash:int) -> SummaryStats|None:
        return self.summary_stats_cache.get(series_hash, None)

    def get_file_series_hashes(self, path: Path) -> Optional[dict[str, int]]:
        md = self.get_file_metadata(path)
        if not md:
            return None
        hashes = md.get('series_hashes')
        return {str(k): int(v) for k, v in hashes.items()}

    def upsert_file_series_hashes(self, path: Path, hashes: dict[str, int]) -> None:
        md = self.get_file_metadata(path) or {}
        cur = dict(md.get('series_hashes') or {})
        cur.update({str(k): int(v) for k, v in hashes.items()})
        merged = dict(md)
        merged['series_hashes'] = cur
        self.upsert_file_metadata(path, merged)
    def _get_buffer_key(self, series:pl.Series) -> BufferKey:
        """

          This kind of works.  We want dataframe and series level metadata
          https://github.com/pola-rs/polars/issues/5117
          these aren't implemented yet
          """

        buffers = series._get_buffers()
        def get_buffer_info(k:Literal["validity"]|Literal["offsets"]) -> SimpleBufferKey:
            if k in buffers and buffers[k] is not None:
                return buffers[k]._get_buffer_info() #type:ignore
            return (0,0,0,)
        validity: SimpleBufferKey = get_buffer_info('validity')
        offsets:SimpleBufferKey = get_buffer_info('offsets')
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
        #existing = list(self.series_hash_cache.keys())
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
            res = df.select(pl.col('a').pl_series_hash.hash_xx()) # type: ignore
            self.series_hash_cache[buffer_info] = res['a'][0]

    def add_df(self, df:pl.DataFrame) -> None:
        for col in df.columns:
            self.add_series(df[col], col)
        
# Backwards-compat alias for existing imports/tests
FileCache = MemoryFileCache

        
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





ColumnGroup:TypeAlias = list[str]

@dataclass
class ProgressNotification:
    # how do we get a failure notification when it results in a crash?
    success: bool
    col_group:ColumnGroup
    execution_args: Any
    result: Any
    #execution_time: int # millisecones?
    execution_time: timedelta
    failure_message: str|None

    def __eq__(self, other):
        props = [self.success == other.success,
                 tuple(self.col_group) == tuple(other.col_group),
                 self.execution_args == other.execution_args,
                 self.result == other.result,
                 self.failure_message == other.failure_message]
        return all(props)
            

ProgressListener:TypeAlias = Callable[[ProgressNotification], None]

ColumnRawResults:TypeAlias = Dict[str, Any]

@dataclass
class ColumnResult:
    series_hash: int #u64 actually
    column_name: str # strictly necessary?
    expressions: list[pl.Expr]
    # I want expressions in plass of execution_args
    # expression names are fine for expressions,  everything else should fall to theColAnalyis class name
    
    result: ColumnRawResults

ColumnResults:TypeAlias = Dict[str, ColumnResult]    
ColumnHashes:TypeAlias = Dict[str, int]

ColumnFunc:TypeAlias = Callable[[pl.LazyFrame, ColumnGroup], ColumnResults]



E = TypeVar('E')

class ColumnExecutor(Generic[E], ABC):

    @abstractmethod
    def get_execution_args(self, existing_stats:dict[str,SummaryStats]) -> E:
        """
          Return execution arguments computed from existing stats.
          """
        ...

    @abstractmethod
    def execute(self, ldf:pl.LazyFrame, execution_args:E) -> ColumnResults:
        """this should generally be a prety simple wrapper around ldf.select/collect
          it can be overriden for testing to throw different errors,

          particularly FatalStop which causes no log to be written.
          That is useful for testing without crashing the python
          process

        """
        ...

@dataclass
class ExecutorArgs:
    columns: ColumnGroup

    #does this expression set include pl.col calls or is it all
    #selectors pl.col calls come up when ColumnExecutor was trying to
    #work around differently cached columns
    column_specific_expressions: bool
    #maybe when column_specific_expressions is false
    #a column group should be included... a union
    

    # do we need to compute hashes for the columns
    include_hash: bool
    expressions: list[pl.Expr]
    row_start: int|None
    row_end: int|None
    extra: Any
    # If True, skip execution - all columns are already cached with complete stats
    no_exec: bool = False


@dataclass
class ExecutorLogEvent:

    dfi: DFIdentifier
    args: ExecutorArgs
    start_time: dtdt
    end_time: Optional[dtdt]
    completed: bool
    executor_class_name: str = ""
    

class ExecutorLog(ABC):

    @abstractmethod
    def log_start_col_group(self, dfi: DFIdentifier, args:ExecutorArgs, executor_class_name:str = "") -> None:
        """
          used so we know that we started execution of a col_group even if it crashes
          """
        ...

    @abstractmethod
    def log_end_col_group(self, dfi: DFIdentifier, args:ExecutorArgs) -> None:
        """
          used so we know that execution finished, Maybe include status
          """
        ...

    @abstractmethod
    def check_log_for_previous_failure(self, dfi: DFIdentifier, args:ExecutorArgs) -> bool:
        """
          check the log for this lazy_dataframe, this set of columns, and this set of column_args
          did it start and not finish, if so, return false
          
          """
        ...

    @abstractmethod
    def get_log_events(self) -> list[ExecutorLogEvent]:
        """
          Get the logged events for this executor.
          """
        ...

    def find_event(self, dfi: DFIdentifier, args: ExecutorArgs) -> Optional[ExecutorLogEvent]:
        """
        Locate the log event for the given dataframe identifier and execution args.
        Matches args by identity to avoid issues comparing polars expressions.
        """
        try:
            events = self.get_log_events()
        except Exception:
            return None
        for ev in events:
            if ev.dfi == dfi and ev.args is args:
                return ev
        return None
    
    def check_log_for_completed(self, dfi: DFIdentifier, args: ExecutorArgs) -> bool:
        """
        Check if this column group was already completed successfully.
        Returns True if there is a completed event with matching args.
        This can be used to skip re-execution of work that's already been done.
        """
        ev = self.find_event(dfi, args)
        if ev:
            return ev.completed
        return False

class SimpleExecutorLog(ExecutorLog):


    
    def __init__(self) -> None:
        self._events: list[ExecutorLogEvent] = []


    def log_start_col_group(self, dfi: DFIdentifier, args:ExecutorArgs, executor_class_name:str = "") -> None:
        #what happens if we try to start the same dfi, args twice???
        ev = ExecutorLogEvent(
            dfi=dfi,
            args=args,
            executor_class_name=executor_class_name,
            completed=False,
            start_time=dtdt.now(),
            end_time=None)
        self._events.append(ev)

    def log_end_col_group(self, dfi: DFIdentifier, args:ExecutorArgs) -> None:
        # Mark the aggregated event as completed when the first column group finishes
        ev = self.find_event(dfi, args)
        if ev:
            ev.end_time = dtdt.now()
            ev.completed = True

        
    def check_log_for_previous_failure(self, dfi: DFIdentifier, args:ExecutorArgs) -> bool:
        # Return True if there is an incomplete event with matching args
        ev = self.find_event(dfi, args)
        if ev:
            return not ev.completed
        return False
    
    def check_log_for_completed(self, dfi: DFIdentifier, args:ExecutorArgs) -> bool:
        """
        Check if this column group was already completed successfully.
        Returns True if there is a completed event with matching args.
        This can be used to skip re-execution of work that's already been done.
        """
        ev = self.find_event(dfi, args)
        if ev:
            return ev.completed
        return False

    def get_log_events(self) -> list[ExecutorLogEvent]:
        """
          get the logged events
          """
        return self._events

    def has_incomplete_for_executor(self, dfi:DFIdentifier, executor_class_name:str) -> bool:
        for ev in self._events:
            if ev.dfi == dfi and ev.executor_class_name == executor_class_name and not ev.completed:
                return True
        return False


class Executor:

    def __init__(self,
        ldf:pl.LazyFrame, column_executor:ColumnExecutor,
        listener:ProgressListener, fc:AbstractFileCache,
        executor_log: ExecutorLog | None = None,
        file_path: str | Path | None = None,
        cached_merged_sd: dict[str, dict[str, Any]] | None = None,
        orig_to_rw_map: dict[str, str] | None = None) -> None:
        self.ldf = ldf
        self.column_executor = column_executor
        self.listener = listener
        self.fc = fc
        self.executor_log = executor_log or SimpleExecutorLog()

        #FIXME wtf is this.  it's either none or a path.  why not just use the path?
        self.file_path: Path | None = Path(file_path) if isinstance(file_path, (str, Path)) else None

        self.dfi = (id(self.ldf), str(self.file_path) if self.file_path else "",)
        self.executor_class_name = self.__class__.__name__
        
        # Store cached merged_sd and mapping for checking complete columns
        self.cached_merged_sd = cached_merged_sd or {}
        self.orig_to_rw_map = orig_to_rw_map or {}

    def run(self) -> None:
        """Execute column analysis, skipping cached columns.
        
        Calls ColumnExecutor.get_execution_args() for each column group with cached results.
        ColumnExecutor sets no_exec flag if all columns in the group are complete.
        If all column groups have no_exec=True, returns early without doing any work.
        Otherwise, executes only groups that need execution.
        """
        #had_failure = False
        last_ex_args: ExecutorArgs | None = None
        
        # First pass: call get_execution_args for all column groups to check if all columns are cached
        logger = logging.getLogger("buckaroo.executor")
        
        logger.info(f"Executor.run() START - file_path={self.file_path}")
        logger.debug(f"  cached_merged_sd keys: {list(self.cached_merged_sd.keys()) if self.cached_merged_sd else []}")
        
        all_execution_args: list[ExecutorArgs] = []
        total_cols_checked = 0
        total_cols_to_execute = 0
        
        for col_group in self.get_column_chunks():
            # Build existing stats by consulting file cache using per-file series hashes
            file_hashes: dict[str, int] = {}
            if self.file_path and self.fc.check_file(self.file_path):
                fh = self.fc.get_file_series_hashes(self.file_path) or {}
                file_hashes = {str(k): int(v) for k, v in fh.items()}

            # Build existing_cached dict with ALL columns in the group
            # ColumnExecutor will filter out cached columns individually
            existing_cached: dict[str, Any] = {}
            for col in col_group:
                total_cols_checked += 1
                # Get cached results from series hash if available
                h = file_hashes.get(col)
                if h:
                    cached_results = self.fc.get_series_results(h)
                    existing_cached[col] = cached_results or {}
                else:
                    existing_cached[col] = {'__missing_hash__': True}
            
            # Call ColumnExecutor.get_execution_args - it will filter out cached columns
            ex_args = self.column_executor.get_execution_args(existing_cached)
            all_execution_args.append(ex_args)
            total_cols_to_execute += len(ex_args.columns)
        
        logger.info(f"Executor.run() FIRST PASS: checked {total_cols_checked} columns across {len(all_execution_args)} groups")
        logger.info(f"  Total columns to execute: {total_cols_to_execute}")
        
        # Check if ALL execution args have empty columns (all columns were filtered out)
        # This means all columns across all groups are cached, so skip execution entirely
        all_cached = all_execution_args and all(len(ex_args.columns) == 0 for ex_args in all_execution_args)
        if all_cached:
            logger.info(f"Executor.run() EARLY RETURN: All {total_cols_checked} columns are cached across {len(all_execution_args)} column groups, skipping execution entirely")
            return
        
        logger.info(f"Executor.run() CONTINUING: {total_cols_to_execute} columns need execution, proceeding to second pass")
        
        # Second pass: execute only groups that need execution
        for col_group in self.get_column_chunks():
            # Build existing stats by consulting file cache using per-file series hashes
            file_hashes: dict[str, int] = {}
            if self.file_path and self.fc.check_file(self.file_path):
                fh = self.fc.get_file_series_hashes(self.file_path) or {}
                file_hashes = {str(k): int(v) for k, v in fh.items()}

            # Build existing_cached dict with ALL columns in the group
            existing_cached: dict[str, Any] = {}
            missing_hash_columns: list[str] = []
            for col in col_group:
                h = file_hashes.get(col)
                if h:
                    cached_results = self.fc.get_series_results(h)
                    existing_cached[col] = cached_results or {}
                else:
                    existing_cached[col] = {'__missing_hash__': True}
                    missing_hash_columns.append(col)
            
            # Get execution args - ColumnExecutor already filtered out cached columns
            ex_args = self.column_executor.get_execution_args(existing_cached)
            
            # Check if original column group was already completed in executor log
            # Create ExecutorArgs with original group columns to check completion
            original_group_args = ExecutorArgs(
                columns=list(col_group),
                column_specific_expressions=ex_args.column_specific_expressions,
                include_hash=ex_args.include_hash,
                expressions=ex_args.expressions,
                row_start=ex_args.row_start,
                row_end=ex_args.row_end,
                extra=ex_args.extra,
                no_exec=False
            )
            
            if self.executor_log.check_log_for_completed(self.dfi, original_group_args):
                logger.info(f"Executor.run() SKIPPING group {col_group} - already completed (found in executor log)")
                continue
            
            # If no columns need execution (all were filtered out), skip this column group
            if not ex_args.columns:
                logger.debug(f"  Skipping column group {col_group} - all columns cached")
                continue
            
            logger.info(f"Executor.run() EXECUTING group {col_group} with {len(ex_args.columns)} columns: {ex_args.columns}")
            # annotate args with missing-hash info so executors can act accordingly
            extra_map: dict[str, Any] = dict(ex_args.extra) if isinstance(ex_args.extra, dict) else {}
            extra_map['missing_hash_columns'] = list(missing_hash_columns)
            if self.file_path:
                extra_map['file_path'] = str(self.file_path)
            ex_args.extra = extra_map

            last_ex_args = ex_args
            if self.executor_log.check_log_for_previous_failure(self.dfi, ex_args):
                # Halt execution immediately on previous failure to make cache write failures very obvious.
                # Note: This means subsequent column groups that haven't failed won't be processed.
                # If writing to the cache fails here, there could still be valid column groups that
                # aren't written to the cache that could succeed, but we intentionally fail fast.

                #FIXME Acutally here start running the bisectors especially for Multiprocess executor
                return
            
            self.executor_log.log_start_col_group(self.dfi, ex_args, self.executor_class_name)
            t1 = now()

            try:
                res = self.column_executor.execute(self.ldf, ex_args)
                t2 = now()
                notification = ProgressNotification(
                    success=True,
                    col_group=col_group,
                    execution_args=[], #FIXME
                    result=res,
                    execution_time=t2-t1,
                    failure_message=None)

                for col, col_result in res.items():
                    self.fc.upsert_key(col_result.series_hash, col_result.result)
                    # cache insert errors should be really rare, if we get here, something weird has happened and trying to defensivly code around it is a fools errand

                #FIXME,  make sure this means that the spurious 0s generated by PAFcolumnexecutor for series hashes aren't inserted    
                # If file hashes were missing and we have a file path, persist newly discovered hashes
                if self.file_path and missing_hash_columns:
                    new_hashes: dict[str, int] = {}
                    for c in missing_hash_columns:
                        if c in res and res[c].series_hash:
                            new_hashes[c] = int(res[c].series_hash)
                    if new_hashes:
                        self.fc.upsert_file_series_hashes(self.file_path, new_hashes)

                self.listener(notification)
                self.executor_log.log_end_col_group(self.dfi, last_ex_args)    
            except Exception as e:
                t3 = now()
                notification = ProgressNotification(
                    success=False,
                    col_group=col_group,
                    execution_args=[], #FIXME
                    result=None,
                    execution_time=t3-t1,
                    failure_message=str(e))
                self.listener(notification)
                #had_failure = True
                # continue to next column group without marking completion
                continue

                
    def get_column_raw_results(self, columns:ColumnGroup) -> ColumnRawResults:
        hashes_for_cols: dict[str,int]= {} # how are we getting the hashes for this ldf?

        existing_cached = {}
        for col in columns:
            hash_ = hashes_for_cols.get(col)
            if hash_:
                existing_cached[col] = self.fc.get_series_results(hash_) or {}
            else:
                existing_cached[col] = {}
        return existing_cached

    def get_executor_args(self, columns:ColumnGroup) -> ExecutorArgs:
        existing_cached = self.get_column_raw_results(columns)
        args = self.column_executor.get_execution_args(existing_cached)
        return args
    


    def get_column_chunks(self) -> list[ColumnGroup]:
        """
          dumb impl
          """
        return [[column] for column in self.ldf.collect_schema().names()]

    
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

#         exc = Executor(lazy_df, simple_column_func, listener, fc)
#         exc.run()
        
"""
Goals:
  be able to interogate the execution log and basically run git-bisect until you get to the minimal reproducable failure.

  this implementation is synchronous and simple


  """
def get_columns_from_args(ldf: pl.LazyFrame, args: ExecutorArgs) -> list[str]:
    """
    Compute the output column names produced by applying the given ExecutorArgs
    to the provided LazyFrame.

    This mirrors the execution flow used by ColumnExecutor implementations that
    first select the target columns, then apply the expressions.
    """
    only_cols = ldf.select(args.columns)
    res = only_cols.select(*args.expressions).collect()
    return list(res.columns)
