import pandas as pd
import hypothesis

import buckaroo
from hypothesis import strategies as st


'''
import pandera as pa
schema = pa.DataFrameSchema(
    {
        "val1": pa.Column(int, pa.Check.in_range(-2, 3)),
        "val2": pa.Column(int, pa.Check.in_range(-2, 3)),
        "str": pa.Column(str, pa.Check.in_range(-2, 3)),
    }
)

out_schema = schema.add_columns(
    {
        "val3": pa.Column(float, pa.Check.in_range(-2, 3)),
    },
)




@hypothesis.given(schema.strategy(size=5))
def test_processing_fn(dataframe):
    buckaroo.BuckarooWidget(dataframe, debug=True)
    #processing_fn(dataframe)
'''

#copied from pandas 2.???
#fails occasionally on my mac osx arm
OPTIONAL_INTS = st.lists(st.one_of(st.integers(), st.none()), max_size=10, min_size=3)

OPTIONAL_FLOATS = st.lists(st.one_of(st.floats(), st.none()), max_size=10, min_size=3)

OPTIONAL_TEXT = st.lists(st.one_of(st.none(), st.text()), max_size=10, min_size=3)

OPTIONAL_DICTS = st.lists(
    st.one_of(st.none(), st.dictionaries(st.text(), st.integers())),
    max_size=10,
    min_size=3,
)

OPTIONAL_LISTS = st.lists(
    st.one_of(st.none(), st.lists(st.text(), max_size=10, min_size=3)),
    max_size=10,
    min_size=3,
)

OPTIONAL_ONE_OF_ALL = st.one_of(
    OPTIONAL_DICTS, #OPTIONAL_FLOATS,
    OPTIONAL_INTS,
    OPTIONAL_LISTS,# OPTIONAL_TEXT
)

@hypothesis.given(data=OPTIONAL_ONE_OF_ALL)
def test_where_inplace_casting(data):
    # GH 22051
    df = pd.DataFrame({"a": data})
    buckaroo.BuckarooWidget(df, debug=True)
    # df_copy = df.where(pd.notnull(df), None).copy()
    # df.where(pd.notnull(df), None, inplace=True)
    # tm.assert_equal(df, df_copy)
