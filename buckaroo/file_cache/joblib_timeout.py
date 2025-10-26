from joblib import parallel_config, Parallel, delayed
import time

def sleep2(i):
    if i == 0:
        time.sleep(2)
    return i
    
# # with parallel_config(backend='threading', n_jobs=2):

# #    Parallel(timeout)(delayed(sqrt)(i ** 2) for i in range(10))

# with parallel_config(backend='threading', n_jobs=2):
#    Parallel(timeout=1.0)(delayed(sleep2)(i) for i in range(10))

def joblib_timeout(timeout_secs):

    def inner_timeout(f):
        def actual_func(*args, **kwargs):
            with parallel_config(backend='threading', n_jobs=2):
                res = Parallel(timeout=timeout_secs)(delayed(f)(*args, **kwargs) for i in range(1))
                #res = Parallel(timeout=timeout_secs)(delayed(f)(*args, **kwargs),)
                return res[0]
        return actual_func
    return inner_timeout

@joblib_timeout(5)
def sleep3(i):
    if i == 0:
        time.sleep(2)
    return i

sleep3(0)
