
import json
from collections import defaultdict 

import polars as pl
from polars import functions as F

from .pluggable_analysis_framework import ColAnalysis
from .analysis_management import (produce_summary_df, AnalsysisPipeline)
from .utils import (BASE_COL_HINT, 
                    FAST_SUMMARY_WHEN_GREATER, PERVERSE_DF)
from buckaroo.serialization_utils import pick, d_update
from buckaroo.pluggable_analysis_framework.safe_summary_df import output_full_reproduce, output_reproduce_preamble, safe_summary_df



def json_postfix(postfix):
    return lambda nm: json.dumps([nm, postfix])


def split_to_dicts(stat_df):
    summary = defaultdict(lambda : {})
    for col in stat_df.columns:
        orig_col, measure = json.loads(col)
        summary[orig_col][measure] = stat_df[col][0]
    return summary

class PolarsAnalysis(ColAnalysis):
    select_clauses = []
    column_ops = {}

class BasicAnalysis(PolarsAnalysis):

    select_clauses = [
        F.all().null_count().name.map(json_postfix('null_count')),
        F.all().mean().name.map(json_postfix('mean')),
        F.all().quantile(.99).name.map(json_postfix('quin99')),
        F.all().value_counts(sort=True).slice(0,10).implode().name.map(json_postfix('value_counts'))
    ]

def normalize_polars_histogram(ph, ser):
    edges = ph['break_point'].to_list()
    edges[0], edges[-1] = ser.min(), ser.max()
    #col_series.hist(bin_count=10)
    col_only_df = ph.select(pl.col("^.*_count$"))
    counts = col_only_df[col_only_df.columns[0]].to_list()
    #counts = ph['_count'].to_list()
    return counts[1:], edges

NUMERIC_POLARS_DTYPES = [
    pl.Int8, pl.Int16, pl.Int32, pl.Int64, 
    pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64,
    pl.Float32, pl.Float64]

class HistogramAnalysis(PolarsAnalysis):
    column_ops = {'hist': (NUMERIC_POLARS_DTYPES, lambda col_series: normalize_polars_histogram(col_series.hist(bin_count=10), col_series))}


def produce_series_df(df, unordered_objs, df_name='test_df', debug=False):
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

def full_produce_summary_df(df, ordered_objs, df_name='test_df', debug=False):
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

    # def __init__(self, analysis_objects, unit_test_objs=True):
    #     self.summary_stats_display = "all"
    #     self.unit_test_objs = unit_test_objs
    #     self.verify_analysis_objects(analysis_objects)

    # def process_summary_facts_set(self):
    #     all_provided = []
    #     for a_obj in self.ordered_a_objs:
    #         all_provided.extend(a_obj.provides_summary)
    #         if a_obj.summary_stats_display:
    #             self.summary_stats_display = a_obj.summary_stats_display

    #     self.provided_summary_facts_set = set(all_provided)

    #     #all is a special value that will dipslay every row
    #     if self.summary_stats_display and not self.summary_stats_display == "all":
    #         #verify that we have a way of computing all of the facts we are displaying
    #         if not self.provided_summary_facts_set.issuperset(set(self.summary_stats_display)):
    #             missing = set(self.summary_stats_display) - set(self.provided_summary_facts_set)
    #             raise NonExistentSummaryRowException(missing)

    # def verify_analysis_objects(self, analysis_objects):
    #     self.ordered_a_objs = order_analysis(analysis_objects)
    #     check_solvable(self.ordered_a_objs)
    #     self.process_summary_facts_set()

    def unit_test(self):
        """test a single, or each col_analysis object with a set of commonly difficult series.
        not implemented yet.

        This helps interactive development by doing a smoke test on
        each new iteration of summary stats function.

        """
        try:
            output_df, table_hint_dict, errs = full_produce_summary_df(PERVERSE_DF, self.ordered_a_objs)
            if len(errs) == 0:
                return True, []
            else:
                return False, errs
        except KeyError:
            pass


    def process_df(self, input_df, debug=False):
        output_df, table_hint_dict, errs = full_produce_summary_df(input_df, self.ordered_a_objs, debug=debug)
        return output_df, table_hint_dict, errs

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
            

class PlDfStats(object):
    '''
    DfStats exists to handle inteligent downampling and applying the ColAnalysis functions
    '''

    def __init__(self, df_stats_df, col_analysis_objs, operating_df_name=None, debug=False):
        self.df = self.get_operating_df(df_stats_df, force_full_eval=False)
        self.col_order = self.df.columns
        self.ap = PolarsAnalsysisPipeline(col_analysis_objs)
        self.operating_df_name = operating_df_name
        self.debug = debug

        self.sdf, self.table_hints, errs = self.ap.process_df(self.df, self.debug)
        if errs:
            output_full_reproduce(errs, self.sdf, operating_df_name)
        
    def get_operating_df(self, df, force_full_eval):
        rows = len(df)
        cols = len(df.columns)
        item_count = rows * cols

        if item_count > FAST_SUMMARY_WHEN_GREATER:
            return df.sample(min([50_000, len(df)]))
        else:
            return df

    @property
    def presentation_sdf(self):
        import pandas as pd
        if self.ap.summary_stats_display == "all":
            return pd.DataFrame(self.sdf)
        return safe_summary_df(self.sdf, self.ap.summary_stats_display)

    def add_analysis(self, a_obj):
        passed_unit_tests, ut_errs = self.ap.add_analysis(a_obj)
        #if you're adding analysis interactively, of course you want debug info... I think
        self.sdf, self.table_hints, errs = self.ap.process_df(self.df, debug=True)
        if passed_unit_tests is False:
            print("Unit tests failed")
        if errs:
            print("Errors on original dataframe")

        if ut_errs or errs:
            output_reproduce_preamble()
        if ut_errs:
            # setting debug=False here because we're already printing reproduce instructions, let the users produce their own stacktrace.. I think
            ut_summary_df, _unused_table_hint_dict, ut_errs2 = produce_summary_df(
                PERVERSE_DF, self.ap.ordered_a_objs, debug=False)
            output_full_reproduce(ut_errs, ut_summary_df, "PERVERSE_DF")
        if errs:
            output_full_reproduce(errs, self.sdf, self.operating_df_name)

