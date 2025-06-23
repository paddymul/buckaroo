import traceback
from typing_extensions import TypeAlias

import polars as pl

from buckaroo.df_util import old_col_new_col
from buckaroo.pluggable_analysis_framework.polars_utils import split_to_dicts


from .col_analysis import ColAnalysis, SDType
from .analysis_management import (produce_summary_df, AnalysisPipeline, DfStats)
from buckaroo.pluggable_analysis_framework.safe_summary_df import safe_summary_df
from typing import Mapping, Any, Callable, Tuple, List, MutableMapping, Type



class PolarsAnalysis(ColAnalysis):
    select_clauses:List[pl.Expr] = []
    column_ops: Mapping[str, Tuple[List[pl.DataType], Callable[[pl.Series], Any]]] = {}

PAObjs: TypeAlias = List[Type[PolarsAnalysis]]

def polars_produce_series_df(df:pl.DataFrame,
                             unordered_objs:PAObjs,
                      df_name:str='test_df', debug:bool=False) -> SDType:
    """ just executes the series methods

    """
    errs: MutableMapping[str, str] = {}
    all_clauses = []
    for obj in unordered_objs:
        all_clauses.extend(obj.select_clauses)

    try:
        print("all_clauses", all_clauses)
        for clause in all_clauses:
            res = df.lazy().select(clause).collect()
            print("polars_analysis_management 38", clause, len(res))
        print("&"*80)
        result_df = df.lazy().select(all_clauses).collect()
    except Exception as e:
        if debug:
            df.write_parquet('error.parq')
        traceback.print_exc()
        return dict([[k, str(e)] for k in df.columns]), {}

    orig_col_to_rewritten = {}
    summary_dict = {}
    for orig_ser_name, rewritten_col_name in old_col_new_col(df):
        orig_col_to_rewritten[orig_ser_name] = rewritten_col_name
        summary_dict[rewritten_col_name] = {}
        summary_dict[rewritten_col_name]['orig_col_name'] = orig_ser_name
        summary_dict[rewritten_col_name]['rewritten_col_name'] = rewritten_col_name


        for a_klass in unordered_objs:
            summary_dict[rewritten_col_name].update(a_klass.provides_defaults)
    first_run_dict = split_to_dicts(result_df)

    for col, measures in first_run_dict.items():
        rw_col = orig_col_to_rewritten[col]
        summary_dict[rw_col].update(measures)

    for pa in unordered_objs:
        for measure_name, action_tuple in pa.column_ops.items():
            col_selector, func = action_tuple
            if col_selector == "all":
                sub_df = df.select(pl.all())
            else:
                sub_df = df.select(pl.col(col_selector))
            for col in sub_df.columns:
                rw_col = orig_col_to_rewritten[col]
                summary_dict[rw_col][measure_name] = func(df[col])
                pass
    return summary_dict, errs


class PolarsAnalysisPipeline(AnalysisPipeline):
    """
    manage the ordering of a set of col_analysis objects
    allow for computing summary_stats (and other oberservation sets) based on col_analysis objects
    allow col_anlysis objects to be added
    """
 
    @staticmethod
    def full_produce_summary_df(
            df:pl.DataFrame, ordered_objs:List[PolarsAnalysis],
            df_name:str='test_df', debug:bool=False):
        print("full_produce_summary_df")
        series_stat_dict, series_errs = polars_produce_series_df(df, ordered_objs, df_name, debug)
        print("about to call produce_summary_df")
        summary_dict, summary_errs = produce_summary_df(
            df, series_stat_dict, ordered_objs, df_name, debug)
        series_errs.update(summary_errs)
        return summary_dict, series_errs



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
    ap_class = PolarsAnalysisPipeline
    
    @property
    def presentation_sdf(self):
        import pandas as pd
        if self.ap.summary_stats_display == "all":
            return pd.DataFrame(self.sdf)
        return safe_summary_df(self.sdf, self.ap.summary_stats_display)
