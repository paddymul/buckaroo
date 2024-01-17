import pandas as pd
#from buckaroo.dataflow import DataFlow
from buckaroo.dataflow_traditional import DataFlow


simple_df = pd.DataFrame({'int_col':[1, 2, 3], 'str_col':['a', 'b', 'c']})



def test_dataflow_operating_df():
    d_flow = DataFlow()
    d_flow.exisitng_operations = []
    assert d_flow.sampled_df is not simple_df
    d_flow.raw_df = simple_df
    print("operating_df", d_flow.sampled_df)
    assert d_flow.sampled_df is simple_df

    d_flow.sample_method = "first"
    assert len(d_flow.sampled_df) == 1
    
    d_flow.sample_method = "default"
    assert d_flow.sampled_df is simple_df

    
def test_dataflow_cleaned():

    d_flow = DataFlow()
    d_flow.exisitng_operations = []
    #these two should be None to start
    assert d_flow.cleaned_df is None
    assert d_flow.cleaned_sd is None
    d_flow.raw_df = simple_df
    assert d_flow.cleaned_df is simple_df
    
    
