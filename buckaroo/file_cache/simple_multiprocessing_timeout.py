#!/usr/bin/env python3
# state:READONLY

import time
import multiprocessing as mp


def sleep_two_seconds(q: mp.Queue) -> None:
    time.sleep(2)
    q.put(("two", "slept 2s"))


def sleep_four_seconds(q: mp.Queue) -> None:
    time.sleep(4)
    q.put(("four", "slept 4s"))

            
        
def main(timeout_seconds: float = 3.0) -> None:
    q: mp.Queue = mp.Queue()
    p_two = mp.Process(target=sleep_two_seconds, args=(q,))
    p_four = mp.Process(target=sleep_four_seconds, args=(q,))

    p_two.start()
    p_four.start()

    start = time.time()
    # Wait up to the timeout across both processes
    p_two.join(timeout_seconds)
    remaining = max(0.0, timeout_seconds - (time.time() - start))
    p_four.join(remaining)

    results: dict[str, str] = {}
    try:
        while True:
            name, msg = q.get_nowait()
            results[name] = msg
    except Exception:
        pass

    # Print result for the 2-second task if completed
    if "two" in results:
        print(results["two"])  # expected: slept 2s
    elif not p_two.is_alive():
        print("two: error")

    # Handle the 4-second task: timeout -> terminate and report
    if p_four.is_alive():
        print(f"four: timed out after {timeout_seconds}s")
        p_four.terminate()
        p_four.join()
    # else:
    #     if "four" in results:
    #         print(results["four"])  # if it somehow finished within timeout
    #     else:
    #         print("four: error")

    # # Ensure cleanup
    # if p_two.is_alive():
    #     p_two.terminate()
    #     p_two.join()


q: mp.Queue = mp.Queue()
funcs = {}
wrap_funcs = {}

def func_runner(*args2, func_name=None, que=None, **kwargs3):
    print("func_runner start")
    res = funcs[func_name](*args2, **kwargs3)
    que.put((func_name, res,))
    print("func_runner finish")

def mp_timeout(orig_f, timeout_secs=3):

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

def sleep_4_return():
    time.sleep(4)
    return 4.5

def sleep_2_return():
    print("sleep_2_return start")
    time.sleep(2)
    print("sleep_2_return after sleep")
    return 2

dec_sleep2 = mp_timeout(sleep_2_return, 3)
dec_sleep4 = mp_timeout(sleep_4_return, 3)

        

        
if __name__ == "__main__":
    # print("here")
    # sleep2_res = dec_sleep2()
    # print("sleep2_res", sleep2_res)

    sleep4_res = dec_sleep4()
    print("sleep3_res", sleep4_res)
    

    #main(3.0)
