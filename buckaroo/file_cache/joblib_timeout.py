import ctypes
import sys
import time
from joblib import parallel_config, Parallel, delayed
from joblib.externals.loky.process_executor  import TerminatedWorkerError
from buckaroo.file_cache.simple_multiprocessing_timeout import TimeoutException
import polars as pl
from multiprocessing import context

from pl_series_hash import crash

def sleep2(i):
    if i == 0:
        time.sleep(2)
    return i

def joblib_timeout(timeout_secs):

    def inner_timeout(f):
        def actual_func(*args, **kwargs):
            try:
                with parallel_config(backend='loky', n_jobs=2):
                    res = Parallel(timeout=timeout_secs)(delayed(f)(*args, **kwargs) for i in range(1))
                    #res = Parallel(timeout=timeout_secs)(delayed(f)(*args, **kwargs),)
                    return res[0]
            except context.TimeoutError as e:
                raise TimeoutException("Timeout fail") from None
            except TerminatedWorkerError as e:
                raise TimeoutException("Timeout fail") from None
            except Exception as e:
                raise
        return actual_func
    return inner_timeout

@joblib_timeout(1)
def jl_polars_longread(i=0):
    if i == 0:
        print("reading large file")
        pl.read_csv("~/3m_july.csv")
    return 5

@joblib_timeout(1)
def jl_simple():
    return 5


@joblib_timeout(.5)
def jl_sleep1():
    time.sleep(1)
    return 5

@joblib_timeout(.5)
def jl_crash_exit():
    #this actually crashes python
    ctypes.string_at(0)
    # i = ctypes.c_char('a')
    # j = ctypes.pointer(i)
    # c = 0
    # while True:
    #     j[c] = 'a'
    #     c += 1
    # j
@joblib_timeout(.5)
def jl_sys_exit():
    #this actually crashes python
    sys.exit()

@joblib_timeout(.5)
def jl_polars_crash():
    df_1 = pl.DataFrame({"u64": pl.Series([5, 3, 20], dtype=pl.UInt64)})
    df_1.select(hash_col=crash("u64"))
