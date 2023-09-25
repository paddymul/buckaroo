import pandas as pd
from IPython.display import display
from buckaroo.buckaroo_widget import BuckarooWidget


simple_df = pd.DataFrame({'int_col':[1, 2, 3], 'str_col':['a', 'b', 'c']})

def test_basic_instantiation():
    df = simple_df
    w = BuckarooWidget(df)
    assert w.dfConfig['totalRows'] == 3

def test_basic_display():
    df = simple_df
    w = BuckarooWidget(df)
    display(w)

def test_interpreter():    
    #df = pd.read_csv('./examples/data/2014-01-citibike-tripdata.csv')

    w = BuckarooWidget(simple_df)
    assert w.operation_results['generated_py_code'] == '# instantiation, unused'
    w.user_entered_operations = [[{"symbol":"dropcol"},{"symbol":"df"},"str_col"]]

    tdf = w.operation_results['transformed_df']
    assert w.operation_results['transform_error'] == False
    field_names = [ f['name'] for f in tdf['schema']['fields'] ]
    assert 'str_col' not in field_names
    print(w.operation_results['generated_py_code'])
    assert w.operation_results['generated_py_code'] == """def clean(df):
    df.drop('str_col', axis=1, inplace=True)
    return df"""

def test_symbol_meta():    
    """verifies that a symbol with a meta key can be added and
    properly interpretted.  This should probably be a lower level
    parser test

    """


    df = pd.read_csv('./examples/data/2014-01-citibike-tripdata.csv')
    w = BuckarooWidget(df)
    assert w.operation_results['generated_py_code'] == '# instantiation, unused'
    w.operations = [[{"symbol":"dropcol", "meta":{}},{"symbol":"df"},"starttime"]]

    tdf = w.operation_results['transformed_df']
    print("transform_error", w.operation_results['transform_error'])
    assert w.operation_results['transform_error'] == False
    field_names = [ f['name'] for f in tdf['schema']['fields'] ]
    assert 'starttime' not in field_names


def test_interpreter_errors():
    df = pd.read_csv('./examples/data/2014-01-citibike-tripdata.csv')
    w = BuckarooWidget(df)
    assert w.operation_results['generated_py_code'] == '# instantiation, unused'
    w.operations = [
        [{"symbol":"dropcol"},{"symbol":"df"},"starttime"],
        [{"symbol":"dropcol"},{"symbol":"df"},"starttime"]]
    assert w.operation_results['transform_error'] == '''"['starttime'] not found in axis"'''

