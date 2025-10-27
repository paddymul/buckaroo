from buckaroo.file_cache.simple_multiprocessing_timeout import (
    mp_timeout_dec, TimeoutException, simple, sleep1, t_sleep1, t_simple,
    mp_sys_exit, t_sys_exit,
    mp_polars_longread, t_polars_longread
)
from buckaroo.file_cache.joblib_timeout import (
    jl_simple, jl_sleep1, jl_sys_exit, jl_crash_exit, jl_polars_longread, jl_polars_crash
)
import pytest

# def test_timeout_pass():

#     assert simple() == 5

# def test_timeout_fail():
#     with pytest.raises(TimeoutException):
#         sleep1()
        
# def test_fail_then_normal():
#     with pytest.raises(TimeoutException):
#         sleep1()
#     assert simple() == 5

# def test_mp_sys_exit():
#     with pytest.raises(TimeoutException):
#         mp_sys_exit()


    
# def test_threading_timeout_pass():
#     assert t_simple() == 5

    
# def test_threading_timeout_fail():
#     with pytest.raises(TimeoutException):
#         t_sleep1()

# # this fails and always will because of threading
       
# def Xtest_threading_sys_exit():
#     with pytest.raises(TimeoutException):
#         t_sys_exit()
        
# def test_mp_polars_timeout():
#     with pytest.raises(TimeoutException):
#         mp_polars_longread()

# def test_t_polars_timeout():
#     with pytest.raises(TimeoutException):
#         t_polars_longread()
    


def test_jl_timeout_pass():
    assert t_simple() == 5

    
def test_jl_timeout_fail():
    with pytest.raises(TimeoutException):
        jl_sleep1()

# this fails and always will because of threading
       
# def test_jl_sys_exit():
#     with pytest.raises(TimeoutException):
#         jl_sys_exit()

def test_jl_crash_exit():
    with pytest.raises(TimeoutException):
        jl_crash_exit()

def test_jl_polars_crash():
    with pytest.raises(TimeoutException):
        jl_polars_crash()

def test_jl_polars_timeout():
    with pytest.raises(TimeoutException):
        jl_polars_longread()
        
def test_jl_fail_then_normal():
    with pytest.raises(TimeoutException):
        jl_sleep1()
    assert jl_simple() == 5
