import pandas as pd
import hypothesis

import buckaroo
from hypothesis import strategies as st


def get_strategy(sz):
    OPTIONAL_INTS = st.lists(st.one_of(
        st.integers(min_value=-9223372036854775806, max_value=9223372036854775806),
        st.none()), max_size=sz, min_size=sz)

    OPTIONAL_FLOATS = st.lists(st.one_of(st.floats(), st.none()), max_size=sz, min_size=sz)

    OPTIONAL_TEXT = st.lists(st.one_of(st.none(), st.text()), max_size=sz, min_size=sz)

    OPTIONAL_DICTS = st.lists(
        st.one_of(st.none(), st.dictionaries(st.text(), st.integers())),
        max_size=sz, min_size=sz)

    OPTIONAL_LISTS = st.lists(
        st.one_of(st.none(), st.lists(st.text(), max_size=10, min_size=3)),
        max_size=sz,
        min_size=sz)

    OPTIONAL_ONE_OF_ALL = st.one_of(
        OPTIONAL_DICTS, OPTIONAL_FLOATS,
        OPTIONAL_INTS,
        OPTIONAL_LISTS, OPTIONAL_TEXT)
    return OPTIONAL_ONE_OF_ALL

@hypothesis.settings(deadline=10_000)
@hypothesis.given(ser_1=get_strategy(10), ser_2=get_strategy(10))
def test_buckaroo_hypothesis(ser_1, ser_2):
    df = pd.DataFrame({"a": ser_1, "b":ser_2})
    buckaroo.BuckarooWidget(df, debug=True)

@hypothesis.settings(deadline=10_000)
@hypothesis.given(ser_1=get_strategy(1), ser_2=get_strategy(1))
def test_buckaroo_hypothesis_single_row(ser_1, ser_2):
    df = pd.DataFrame({"a": ser_1, "b":ser_2})

    # debug=True turns off warning quieting and will throw an error
    # instead of collecting errors, it's what we want here. The option
    # could be better named
    buckaroo.BuckarooWidget(df, debug=True)
