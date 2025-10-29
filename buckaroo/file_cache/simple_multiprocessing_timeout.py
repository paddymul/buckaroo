#!/usr/bin/env python3
# state:READONLY
import polars as pl
import time
import multiprocessing as mp
import queue
import threading
import sys
from datetime import datetime as dtdt
# This is my onw adhoc version of a multiprocessing based timeout guard.
# Joblib seems to be much better written around this.  specifically I think it works with functions defined inside of jupyter notebooks, this implementation needs to have functions defined in a module



q: mp.Queue = mp.Queue()
funcs = {}
wrap_funcs = {}

def func_runner(*args2, func_name=None, que=None, **kwargs3):
    print("func_runner start")
    res = funcs[func_name](*args2, **kwargs3)
    que.put((func_name, res,))
    print("func_runner finish")

class TimeoutException(Exception):
    pass
    
def mp_timeout_dec(timeout_secs):
    def mp_timeout(orig_f):

        func_name = orig_f.__name__
        funcs[func_name] = orig_f
        def actual_func(*args, **kwargs):
            print("actual_func start")
            kwargs2 = kwargs.copy()
            kwargs2['que'] = q
            kwargs2['func_name'] = func_name
            p = mp.Process(target=func_runner, args=args, kwargs=kwargs2)
            p.start()
            p.join(timeout_secs)
            try:
                name, outer_res = q.get_nowait()
                print("name")
                return outer_res
            except queue.Empty as e:
                p.terminate()
                p.join()
                raise TimeoutException("Timeout fail") from None
            except Exception as e:
                print("type(e)", type(e))
                if not isinstance(e, TimeoutException):
                    print(e)
                    p.terminate()
                    p.join()
                    raise
        return actual_func
    return mp_timeout
    
def threading_timeout_dec(timeout_secs):
    def mp_timeout(orig_f):

        func_name = orig_f.__name__
        funcs[func_name] = orig_f
        def actual_func(*args, **kwargs):
            print("actual_func start")
            kwargs2 = kwargs.copy()
            kwargs2['que'] = q
            kwargs2['func_name'] = func_name
            p = threading.Thread(target=func_runner, args=args, kwargs=kwargs2)
            p.start()
            p.join(timeout_secs)
            try:
                name, outer_res = q.get_nowait()
                print("name")
                return outer_res
            except queue.Empty as e:
                p.join()
                raise TimeoutException("Timeout fail") from None
            except Exception as e:
                print("type(e)", type(e))
                if not isinstance(e, TimeoutException):
                    print(e)
                    p.join()
                    raise
        return actual_func
    return mp_timeout
    

@mp_timeout_dec(1)
def return_1():
    #time.sleep(.5)
    return 1

def raw_return_1():
    return 1


@mp_timeout_dec(1)
def sleep_and_fail():
    time.sleep(2)
    return 1


#the following two functions are used by tests.  They must defined outside of the test file
@mp_timeout_dec(1)
def simple():
    return 5


@mp_timeout_dec(.5)
def sleep1():
    time.sleep(1)
    return 5

@mp_timeout_dec(.5)
def mp_sys_exit():
    sys.exit()


@threading_timeout_dec(1)
def t_simple():
    return 5


@threading_timeout_dec(.5)
def t_sleep1():
    time.sleep(1)
    return 5

@threading_timeout_dec(.5)
def t_sys_exit():
    sys.exit()

@mp_timeout_dec(.1)
def mp_polars_longread():
    
    t1 = dtdt.now()
    print("start read at ", t1)
    pl.read_csv("~/3m_july.csv")
    t2 = dtdt.now()
    print("finished read, took", t2-t1)
    return 4

@threading_timeout_dec(.1)
def t_polars_longread():
    pl.read_csv("~/3m_july.csv")
    return 4


if __name__ == "__main__":
    #print(sleep_4_return2())
    #print(return_1())

    sleep_and_fail()
    
    # for i in range(100):
    #     print(i, return_1())
        #decorator timing
        #python simple_multiprocessing_timeout.py  2.43s user 0.66s system 97% cpu 3.160 total



        # print(raw_return_1())
        # raw return timing
        #python simple_multiprocessing_timeout.py  0.04s user 0.02s system 70% cpu 0.079 total

        #so each fork takes approximately 30ms. which is signficant, but workable
