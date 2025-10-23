#!/usr/bin/env python3
# state:READONLY

import time
import multiprocessing as mp

q: mp.Queue = mp.Queue()
funcs = {}
wrap_funcs = {}

def func_runner(*args2, func_name=None, que=None, **kwargs3):
    print("func_runner start")
    res = funcs[func_name](*args2, **kwargs3)
    que.put((func_name, res,))
    print("func_runner finish")

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
            except Exception as e:
                print(e)
                p.terminate()
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


if __name__ == "__main__":
    #print(sleep_4_return2())
    #print(return_1())
    for i in range(100):
        print(i, return_1())
        #decorator timing
        #python simple_multiprocessing_timeout.py  2.43s user 0.66s system 97% cpu 3.160 total



        # print(raw_return_1())
        # raw return timing
        #python simple_multiprocessing_timeout.py  0.04s user 0.02s system 70% cpu 0.079 total

        #so each fork takes approximately 30ms. which is signficant, but workable
