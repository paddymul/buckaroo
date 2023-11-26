import pandas as pd
import hypothesis

import buckaroo
from hypothesis import given, strategies as st
from hypothesis.extra.pandas import data_frames, column


@hypothesis.given(
    # TODO: write strategy to support n-Columns
    df=st.one_of(data_frames(columns=[column(elements=st.integers())]),
                 data_frames(columns=[column(elements=st.floats())]),
                 data_frames(columns=[column(elements=st.text())]),
                 data_frames(columns=[column(elements=
                                             st.dictionaries(st.text(), st.integers()))]),
                 data_frames(columns=[column(elements=
                                             st.lists(st.text()))])),
    sampled=st.booleans(),
    summaryStats=st.booleans(),
    reorderdColumns=st.booleans(),
    showCommands=st.booleans(),
    auto_clean=st.booleans(),
    postProcessingF=st.none(),
    debug=st.booleans(),
)
def test_fuzz_BuckarooWidget(
        df,
        sampled,
        summaryStats,
        reorderdColumns,
        showCommands,
        auto_clean,
        postProcessingF,
        debug,
):
    buckaroo.BuckarooWidget(
        df=df,
        sampled=sampled,
        summaryStats=summaryStats,
        reorderdColumns=reorderdColumns,
        showCommands=showCommands,
        auto_clean=auto_clean,
        postProcessingF=postProcessingF,
        debug=debug,
    )
