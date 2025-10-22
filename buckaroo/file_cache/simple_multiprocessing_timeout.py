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

# def mp_timeout(f):
#     def wrapped(*args, **kwargs):

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

        

        
if __name__ == "__main__":
    main(3.0)
