import re
import pandas as pd
import numpy as np
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (
    ColAnalysis,
)
from buckaroo.jlisp.lisp_utils import s
from buckaroo.customizations.heuristics import BaseHeuristicCleaningGenOps
from functools import lru_cache
from pandas.util import hash_pandas_object


class SeriesWrapper:
    def __init__(self, series):
        self.series = series
        if not getattr(series, '_hash', False):
            series._hash = int(hash_pandas_object(series).sum())
        self._hash = series._hash

    def __eq__(self, other):
        return isinstance(other, SeriesWrapper) and self.series.equals(other.series)

    def __hash__(self):
        return self._hash
def cache_series_func(f, max_size=256):
    _cache = {}

    def unwrapped_hashable_func(ser):
        return f(ser.series)
    cached_func= lru_cache(max_size)(unwrapped_hashable_func)

    def ret_func(ser):
        if isinstance(ser, SeriesWrapper):
            return cached_func(ser)
        elif isinstance(ser, pd.Series):
            cser = SeriesWrapper(ser)
            #print("11", cser, hash(cser))
            return cached_func(cser)
        else:
            raise Exception(f"Unknown type of {type(ser)}")
    return ret_func

# I don't want to apply these caching functions more generally because
# I'm worried about putting a large object inot the cache results.
# Since these return scalars, it's fairly cheap, and these functions
# are specifically slow , I"m fine with it

# importantly these functions are run interactively

@cache_series_func
def regular_int_parse_frac(ser):
    null_count = (~ser.apply(pd.to_numeric, errors="coerce").isnull()).sum()
    return null_count / len(ser)


digits_and_period = re.compile(r"[^\d\.]")

@cache_series_func
def strip_int_parse_frac(ser):
    if pd.api.types.is_object_dtype(ser):
        ser = ser.astype("string")
    if not pd.api.types.is_string_dtype(ser):
        return 0
    ser = ser.sample(np.min([300, len(ser)]))
    stripped = ser.str.replace(digits_and_period, "", regex=True)

    # don't like the string conversion here, should still be vectorized
    int_parsable = ser.astype(str).str.isdigit()
    parsable = int_parsable | (stripped != "")
    return parsable.sum() / len(ser)


TRUE_SYNONYMS = ["true", "yes", "on", "1"]
FALSE_SYNONYMS = ["false", "no", "off", "0"]
BOOL_SYNONYMS = TRUE_SYNONYMS + FALSE_SYNONYMS

@cache_series_func
def str_bool_frac(ser):
    ser = ser.sample(np.min([300, len(ser)]))
    if pd.api.types.is_object_dtype(ser):
        ser = ser.astype("string")
    if not pd.api.types.is_string_dtype(ser):
        return 0
    matches = ser.str.lower().str.strip().isin(BOOL_SYNONYMS)
    return matches.sum() / len(ser)

@cache_series_func
def us_dates_frac(ser):
    parsed_dates = pd.to_datetime(ser, errors="coerce", format="%m/%d/%Y")
    return (~parsed_dates.isna()).sum() / len(ser)

@cache_series_func
def euro_dates_frac(ser):
    parsed_dates = pd.to_datetime(ser, errors="coerce", format="%d/%m/%Y")
    return (~parsed_dates.isna()).sum() / len(ser)

class HeuristicFracs(ColAnalysis):
    provides_defaults = dict(
        str_bool_frac=0,
        regular_int_parse_frac=0,
        strip_int_parse_frac=0,
        us_dates_frac=0,
    )

    @staticmethod
    def series_summary(sampled_ser, ser):
        if not (
            pd.api.types.is_string_dtype(ser)
            or pd.api.types.is_object_dtype(ser)
        ):
            return {}

        return dict(
            str_bool_frac=str_bool_frac(ser),
            regular_int_parse_frac=regular_int_parse_frac(ser),
            strip_int_parse_frac=strip_int_parse_frac(ser),
            us_dates_frac=us_dates_frac(ser),
        )

frac_name_to_command = {
    "str_bool_frac": "str_bool",
    "regular_int_parse_frac": "regular_int_parse",
    "strip_int_parse_frac": "strip_int_parse",
    "us_dates_frac": "us_date",
}


class ConvservativeCleaningGenops(BaseHeuristicCleaningGenOps):
    requires_summary = [
        "str_bool_frac",
        "regular_int_parse_frac",
        "strip_int_parse_frac",
        "us_dates_frac",
    ]

    rules = {
        "str_bool_frac": [s("f>"), 0.9],
        "regular_int_parse_frac": [s("f>"), 0.9],
        "strip_int_parse_frac": [s("f>"), 0.9],
        "none": [s("none-rule")],
        "us_dates_frac": [s("primary"), [s("f>"), 0.8]],
    }
    rules_op_names = frac_name_to_command


class AggresiveCleaningGenOps(BaseHeuristicCleaningGenOps):
    requires_summary = [
        "str_bool_frac",
        "regular_int_parse_frac",
        "strip_int_parse_frac",
        "us_dates_frac",
    ]
    rules = {
        "str_bool_frac": [s("f>"), 0.6],
        "regular_int_parse_frac": [s("f>"), 0.9],
        "strip_int_parse_frac": [s("f>"), 0.75],
        "none": [s("none-rule")],
        "us_dates_frac": [s("primary"), [s("f>"), 0.7]],
    }

    rules_op_names = frac_name_to_command    
