
import json
from collections import defaultdict 

import polars as pl
from polars import functions as F

from buckaroo.pluggable_analysis_framework.utils import json_postfix

from .pluggable_analysis_framework import ColAnalysis
from .analysis_management import (produce_summary_df, AnalsysisPipeline, DfStats)
from .utils import (BASE_COL_HINT)
from buckaroo.serialization_utils import pick, d_update
from buckaroo.pluggable_analysis_framework.safe_summary_df import safe_summary_df
from typing import Mapping, Any, Callable, Tuple, List


def split_to_dicts(stat_df:pl.DataFrame) -> Mapping[str, Mapping[str, Any]]:
    summary = defaultdict(lambda : {})
    for col in stat_df.columns:
        orig_col, measure = json.loads(col)
        summary[orig_col][measure] = stat_df[col][0]
    return summary

class PolarsAnalysis(ColAnalysis):
    select_clauses:pl.Expr = []
    column_ops: Mapping[str, Tuple[pl.PolarsDataType, Callable[[pl.Series], any]]] = {}

class BasicAnalysis(PolarsAnalysis):

    select_clauses = [
        F.all().null_count().name.map(json_postfix('null_count')),
        F.all().mean().name.map(json_postfix('mean')),
        F.all().quantile(.99).name.map(json_postfix('quin99')),
        F.all().value_counts(sort=True).slice(0,10).implode().name.map(json_postfix('value_counts'))
    ]

def normalize_polars_histogram(ph:pl.DataFrame, ser:pl.Series):
    edges = ph['break_point'].to_list()
    edges[0], edges[-1] = ser.min(), ser.max()
    #col_series.hist(bin_count=10)
    col_only_df = ph.select(pl.col("^.*_count$"))
    counts = col_only_df[col_only_df.columns[0]].to_list()
    #counts = ph['_count'].to_list()
    return counts[1:], edges

NUMERIC_POLARS_DTYPES:List[pl.PolarsDataType] = [
    pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    pl.Float32, pl.Float64]

class HistogramAnalysis(PolarsAnalysis):
    column_ops = {
        'hist': (NUMERIC_POLARS_DTYPES, 
                 lambda col_series: normalize_polars_histogram(col_series.hist(bin_count=10), col_series))}


def produce_series_df(df:pl.DataFrame, unordered_objs:PolarsAnalysis, df_name='test_df', debug=False):
    """ just executes the series methods

    """
    errs = {}
    all_clauses = []
    for obj in unordered_objs:
        all_clauses.extend(obj.select_clauses)
    result_df = df.lazy().select(all_clauses).collect()
    summary_dict = split_to_dicts(result_df)

    for pa in unordered_objs:
        for measure_name, action_tuple in pa.column_ops.items():
            col_selector, func = action_tuple
            sub_df = df.select(pl.col(col_selector))
            for col in sub_df.columns:
                print("measure_name", measure_name, "col", col, "df[col]", df[col])
                summary_dict[col][measure_name] = func(df[col])
                pass
    return summary_dict, errs

def full_produce_summary_df(df:pl.DataFrame, ordered_objs:PolarsAnalysis, df_name='test_df', debug=False):
    series_stat_dict, series_errs = produce_series_df(df, ordered_objs, df_name, debug)
    summary_df, summary_errs = produce_summary_df(
        df, series_stat_dict, ordered_objs, df_name, debug)
    series_errs.update(summary_errs)
    table_hint_col_dict = {}
    for ser_name in df.columns:
        table_hint_col_dict[ser_name] = pick(
            d_update(BASE_COL_HINT, summary_df[ser_name]),
            BASE_COL_HINT.keys())

    return summary_df, table_hint_col_dict, series_errs



class PolarsAnalsysisPipeline(AnalsysisPipeline):
    """
    manage the ordering of a set of col_analysis objects
    allow for computing summary_stats (and other oberservation sets) based on col_analysis objects
    allow col_anlysis objects to be added
    """
    full_produce_func = [full_produce_summary_df]

    def add_analysis(self, new_aobj):
        new_cname = new_aobj.cname()
        new_aobj_set = []
        for aobj in self.ordered_a_objs:
            if aobj.cname() == new_cname:
                continue
            new_aobj_set.append(aobj)
        new_aobj_set.append(new_aobj)
        self.verify_analysis_objects(new_aobj_set)

        # passed_unit_test, errs = self.unit_test()
        # if passed_unit_test is False:
        #     return False, errs
        return True, []
            

class PlDfStats(DfStats):
    '''
    DfStats exists to handle inteligent downampling and applying the ColAnalysis functions
    '''
    ap_class = PolarsAnalsysisPipeline
    
    @property
    def presentation_sdf(self):
        import pandas as pd
        if self.ap.summary_stats_display == "all":
            return pd.DataFrame(self.sdf)
        return safe_summary_df(self.sdf, self.ap.summary_stats_display)