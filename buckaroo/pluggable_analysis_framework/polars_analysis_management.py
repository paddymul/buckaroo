
import json
from collections import defaultdict 

import polars as pl

from polars import functions as F

def json_postfix(postfix):
    return lambda nm: json.dumps([nm, postfix])


def split_to_dicts(stat_df):
    summary = defaultdict(lambda : {})
    for col in stat_df.columns:
        orig_col, measure = json.loads(col)
        summary[orig_col][measure] = stat_df[col][0]
    return summary

class PolarsAnalysis:

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
    pl.Float32, pl.Float64, 
]

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

    #summary = defaultdict(lambda : {})
    for pa in unordered_objs:
        for measure_name, action_tuple in pa.column_ops.items():
            col_selector, func = action_tuple
            sub_df = df.select(pl.col(col_selector))
            for col in sub_df.columns:
                print("measure_name", measure_name, "col", col, "df[col]", df[col])
                summary_dict[col][measure_name] = func(df[col])
                pass
    return summary_dict, errs



# def orig_produce_series_df(df, ordered_objs, df_name='test_df', debug=False):
#     """ just executes the series methods

#     """
#     errs = {}
#     series_stats = defaultdict(lambda: {})
#     for ser_name in df.columns:
#         ser = df[ser_name]
#         #FIXME: actually sample the series.  waiting until I have time
#         #to proeprly benchmark
#         sampled_ser = ser
#         for a_kls in ordered_objs:
#             try:
#                 if a_kls.quiet or a_kls.quiet_warnings:
#                     if debug is False:
#                         warnings.filterwarnings('ignore')
                        
#                     col_stat_dict = a_kls.series_summary(sampled_ser, ser)
#                     warnings.filterwarnings('default')
#                 else:
#                     col_stat_dict = a_kls.series_summary(sampled_ser, ser)

#                 series_stats[ser_name].update(col_stat_dict)
#             except Exception as e:
#                 if not a_kls.quiet:
#                     errs[ser_name + ":series_summary"] = e, a_kls
#                 if debug:
#                     traceback.print_exc()
#                 continue
#     return series_stats, errs

# def produce_summary_df(df, series_stats, ordered_objs, df_name='test_df', debug=False):
#     """
#     takes a dataframe and a list of analyses that have been ordered by a graph sort,
#     then it produces a summary dataframe
#     """
#     errs = {}
#     summary_col_dict = {}
#     #figure out how to add in "index"... but just for table_hints
#     for ser_name in df.columns:
#         base_summary_dict = series_stats[ser_name]
#         for a_kls in ordered_objs:
#             try:
#                 if a_kls.quiet or a_kls.quiet_warnings:
#                     if debug is False:
#                         warnings.filterwarnings('ignore')
#                     summary_res = a_kls.computed_summary(base_summary_dict)
#                     warnings.filterwarnings('default')
#                 else:
#                     summary_res = a_kls.computed_summary(base_summary_dict)
#                 for k,v in summary_res.items():
#                     base_summary_dict.update(summary_res)
#             except Exception as e:
#                 if not a_kls.quiet:
#                     errs[ser_name + ":computed_summary"] = e, a_kls
#                 if debug:
#                     traceback.print_exc()
#                 continue
#         summary_col_dict[ser_name] = base_summary_dict
#     return summary_col_dict, errs

# def full_produce_summary_df(df, ordered_objs, df_name='test_df', debug=False):
#     series_stat_dict, series_errs = produce_series_df(df, ordered_objs, df_name, debug)
#     summary_df, summary_errs = produce_summary_df(
#         df, series_stat_dict, ordered_objs, df_name, debug)
#     series_errs.update(summary_errs)
#     table_hint_col_dict = {}
#     for ser_name in df.columns:
#         table_hint_col_dict[ser_name] = pick(
#             d_update(BASE_COL_HINT, summary_df[ser_name]),
#             BASE_COL_HINT.keys())

#     return summary_df, table_hint_col_dict, series_errs

# class NonExistentSummaryRowException(Exception):
#     pass

# class AnalsysisPipeline(object):
#     """
#     manage the ordering of a set of col_analysis objects
#     allow for computing summary_stats (and other oberservation sets) based on col_analysis objects
#     allow col_anlysis objects to be added
#     """
#     def __init__(self, analysis_objects, unit_test_objs=True):
#         self.summary_stats_display = "all"
#         self.unit_test_objs = unit_test_objs
#         self.verify_analysis_objects(analysis_objects)

#     def process_summary_facts_set(self):
#         all_provided = []
#         for a_obj in self.ordered_a_objs:
#             all_provided.extend(a_obj.provides_summary)
#             if a_obj.summary_stats_display:
#                 self.summary_stats_display = a_obj.summary_stats_display

#         self.provided_summary_facts_set = set(all_provided)

#         #all is a special value that will dipslay every row
#         if self.summary_stats_display and not self.summary_stats_display == "all":
#             #verify that we have a way of computing all of the facts we are displaying
#             if not self.provided_summary_facts_set.issuperset(set(self.summary_stats_display)):
#                 missing = set(self.summary_stats_display) - set(self.provided_summary_facts_set)
#                 raise NonExistentSummaryRowException(missing)

#     def verify_analysis_objects(self, analysis_objects):
#         self.ordered_a_objs = order_analysis(analysis_objects)
#         check_solvable(self.ordered_a_objs)
#         self.process_summary_facts_set()

#     def unit_test(self):
#         """test a single, or each col_analysis object with a set of commonly difficult series.
#         not implemented yet.

#         This helps interactive development by doing a smoke test on
#         each new iteration of summary stats function.

#         """
#         try:
#             output_df, table_hint_dict, errs = full_produce_summary_df(PERVERSE_DF, self.ordered_a_objs)
#             if len(errs) == 0:
#                 return True, []
#             else:
#                 return False, errs
#         except KeyError:
#             pass


#     def process_df(self, input_df, debug=False):
#         output_df, table_hint_dict, errs = full_produce_summary_df(input_df, self.ordered_a_objs, debug=debug)
#         return output_df, table_hint_dict, errs

#     def add_analysis(self, new_aobj):
#         new_cname = new_aobj.cname()
#         new_aobj_set = []
#         for aobj in self.ordered_a_objs:
#             if aobj.cname() == new_cname:
#                 continue
#             new_aobj_set.append(aobj)
#         new_aobj_set.append(new_aobj)
#         self.verify_analysis_objects(new_aobj_set)
#         passed_unit_test, errs = self.unit_test()
#         if passed_unit_test is False:
#             return False, errs
#         return True, []
            

# class DfStats(object):
#     '''
#     DfStats exists to handle inteligent downampling and applying the ColAnalysis functions
#     '''

#     def __init__(self, df_stats_df, col_analysis_objs, operating_df_name=None, debug=False):
#         self.df = self.get_operating_df(df_stats_df, force_full_eval=False)
#         self.col_order = self.df.columns
#         self.ap = AnalsysisPipeline(col_analysis_objs)
#         self.operating_df_name = operating_df_name
#         self.debug = debug

#         self.sdf, self.table_hints, errs = self.ap.process_df(self.df, self.debug)
#         if errs:
#             output_full_reproduce(errs, self.sdf, operating_df_name)
        
#     def get_operating_df(self, df, force_full_eval):
#         rows = len(df)
#         cols = len(df.columns)
#         item_count = rows * cols

#         if item_count > FAST_SUMMARY_WHEN_GREATER:
#             return df.sample(np.min([50_000, len(df)]))
#         else:
#             return df

#     @property
#     def presentation_sdf(self):
#         if self.ap.summary_stats_display == "all":
#             return self.sdf
#         return safe_summary_df(self.sdf, self.ap.summary_stats_display)

#     def add_analysis(self, a_obj):
#         passed_unit_tests, ut_errs = self.ap.add_analysis(a_obj)
#         #if you're adding analysis interactively, of course you want debug info... I think
#         self.sdf, self.table_hints, errs = self.ap.process_df(self.df, debug=True)
#         if passed_unit_tests is False:
#             print("Unit tests failed")
#         if errs:
#             print("Errors on original dataframe")

#         if ut_errs or errs:
#             output_reproduce_preamble()
#         if ut_errs:
#             # setting debug=False here because we're already printing reproduce instructions, let the users produce their own stacktrace.. I think
#             ut_summary_df, _unused_table_hint_dict, ut_errs2 = produce_summary_df(
#                 PERVERSE_DF, self.ap.ordered_a_objs, debug=False)
#             output_full_reproduce(ut_errs, ut_summary_df, "PERVERSE_DF")
#         if errs:
#             output_full_reproduce(errs, self.sdf, self.operating_df_name)

