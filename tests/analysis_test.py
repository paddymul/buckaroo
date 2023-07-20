import numpy as np
import pandas as pd
from buckaroo.analysis import TypingStats, DefaultSummaryStats


text_ser = pd.Series(["foo", "bar", "baz"])
datelike_ser = pd.Series([
    "2014-01-01 00:00:06",
    "2014-01-01 00:00:38",
    "2014-01-01 00:03:59"])
all_nan_ser = pd.Series([np.nan, np.nan])
int_ser = pd.Series([10, 30, -10, 33])
fp_ser = pd.Series([33.2, 83.2, -1.0, 0])

all_sers = [
    text_ser, datelike_ser, all_nan_ser,
    int_ser, fp_ser]

# def test_text_ser():
#     DefaultSummaryStats.summary(text_ser, text_ser, text_ser)

def test_default_summary_stats():
    for ser in all_sers:
        DefaultSummaryStats.summary(ser, ser, ser)

