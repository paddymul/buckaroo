import pytest
from pydantic import BaseModel, ValidationError
import pandas as pd
import numpy as np
from buckaroo.serialization_utils import pd_py_serialize, df_to_obj

def test_py_serialize():
    assert pd_py_serialize({'a': pd.NA, 'b': np.nan}) == "{'a': pd.NA, 'b': np.nan, }"
    assert pd_py_serialize({'a': None, 'b': "string", 'c': 4, 'd': 10.3 }) ==\
        "{'a': None, 'b': 'string', 'c': 4, 'd': 10.3, }"
    
def test_df_to_obj():
    named_index_df = pd.DataFrame(
        dict(names=['one', 'two', 'three'],
             values=[1, 2, 3])).set_index('names')

    serialized_df = df_to_obj(named_index_df)
    assert serialized_df['data'][0]['names'] == 'one'


# def test_int_overflow_validation():
#     class Model(BaseModel):
#         a: int

#     with pytest.raises(ValidationError) as exc_info:
#         Model(a=value)
#     assert exc_info.value.errors(include_url=False) == [
#         {'type': 'finite_number', 'loc': ('a',), 'msg': 'Input should be a finite number', 'input': value}
#     ]

def test_int_overflow_validation():
    value=float('nan')
    class Model(BaseModel):
        a: int
    Model(a=3)
    with pytest.raises(ValidationError) as exc_info:
        Model(a=value)
    assert exc_info.value.errors(include_url=False) == [
        {'type': 'finite_number', 'loc': ('a',), 'msg': 'Input should be a finite number',
         'input': value
         }]

from buckaroo.serialization_utils import ColumnStringHint, ColumnBooleanHint, ColumnHint
def test_column_hints():
    ColumnStringHint(type="string", histogram=[])
    ColumnStringHint(type="string", histogram=[{'name':'foo', 'population':3500}])

    # value=float('nan')

    with pytest.raises(ValidationError) as exc_info:
        errant_histogram_entry = {'name':'foo', 'no_population':3500}
        ColumnStringHint(type="string", histogram=[errant_histogram_entry])
    assert exc_info.value.errors(include_url=False) == [
        {'type': 'missing', 'loc': ('histogram', 0, 'population'),
         'msg': 'Field required','input': errant_histogram_entry}]
    
    
    
    
