import traceback
from typing_extensions import TypeAlias

import polars as pl

from buckaroo.df_util import old_col_new_col
from buckaroo.pluggable_analysis_framework.polars_utils import split_to_dicts


from .col_analysis import ColAnalysis, SDType
from .analysis_management import (produce_summary_df, AnalysisPipeline, DfStats)
from buckaroo.pluggable_analysis_framework.safe_summary_df import safe_summary_df
from typing import Mapping, Any, Callable, Tuple, List, MutableMapping, Type
import warnings



class PolarsAnalysis(ColAnalysis):
    select_clauses:List[pl.Expr] = []
    column_ops: Mapping[str, Tuple[List[pl.DataType], Callable[[pl.Series], Any]]] = {}

PAObjs: TypeAlias = List[Type[PolarsAnalysis]]

def polars_produce_series_df(df:pl.DataFrame,
                             unordered_objs:PAObjs,
                      df_name:str='test_df', debug:bool=False) -> SDType:
    """ just executes the series methods

    """
    if debug:
        raise Exception("Debug mode enabled - throwing error for testing")
    
    errs: MutableMapping[str, str] = {}
    all_clauses = []
    for obj in unordered_objs:
        all_clauses.extend(obj.select_clauses)

    try:

        # Execute clauses individually and combine horizontally
        individual_results = []
        for clause in all_clauses:
            try:
                res = df.lazy().select(clause).collect()
                individual_results.append(res)
            except Exception as clause_error:
                if debug:
                    print(f"ERROR in individual execution of {clause}: {clause_error}")
                    traceback.print_exc()
                continue
        
        # Combine results horizontally 
        if individual_results:
            result_df = individual_results[0]
            for additional_result in individual_results[1:]:
                result_df = result_df.hstack(additional_result)
        else:
            # If no clauses worked, create empty result
            result_df = pl.DataFrame()
            
        if debug:
            print(f"DEBUG: result_df shape: {result_df.shape}")
            print(f"DEBUG: result_df columns: {result_df.columns}")
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
    
    print(f"DEBUG: summary_dict after defaults: {list(summary_dict.keys())}")
    for col, data in summary_dict.items():
        print(f"DEBUG: {col} keys: {list(data.keys())}")
    
    first_run_dict = split_to_dicts(result_df)
    print(f"DEBUG: first_run_dict keys: {list(first_run_dict.keys())}")

    # Map from original column names to rewritten column names
    for orig_col, measures in first_run_dict.items():
        if orig_col in orig_col_to_rewritten:
            rw_col = orig_col_to_rewritten[orig_col]
            summary_dict[rw_col].update(measures)
            print(f"DEBUG: Mapped {orig_col} -> {rw_col}, measures: {list(measures.keys())}")
        else:
            print(f"DEBUG: Skipping unmapped column: {orig_col}")
            
    print(f"DEBUG: summary_dict after mapping: {list(summary_dict.keys())}")
    for col, data in summary_dict.items():
        print(f"DEBUG: {col} has measures: {list(data.keys())}")

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
    
    print(f"DEBUG: Final summary_dict keys: {list(summary_dict.keys())}")
    for col, data in summary_dict.items():
        print(f"DEBUG: Final {col} keys: {list(data.keys())}")
    
    return summary_dict, errs


def polars_produce_summary_df(
    df: pl.DataFrame, series_stats: SDType,
    ordered_objs: PAObjs, df_name: str = 'test_df', debug: bool = False) -> Tuple[SDType, MutableMapping[str, str]]:
    """
    Polars-specific version of produce_summary_df that correctly handles column name mapping.
    
    The issue: polars results use original column names in JSON format like ["tripduration", "most_freq"]
    but the analysis pipeline expects rewritten names like "a", "b", "c", etc.
    """
    from .analysis_management import ColMeta, ErrDict, ColIdentifier, AObjs
    
    errs: ErrDict = {}
    summary_col_dict: SDType = {}
    cols: List[ColIdentifier] = []
    cols.extend(df.columns)
    
    # Create mapping from original to rewritten column names
    orig_to_rewritten = {}
    for orig_ser_name, rewritten_col_name in old_col_new_col(df):
        orig_to_rewritten[orig_ser_name] = rewritten_col_name
    
    print("seriestats 85")
    print(list(series_stats.keys()))
    
    for orig_ser_name, rewritten_col_name in old_col_new_col(df):
        # series_stats uses rewritten column names as keys, not original names
        base_summary_dict: ColMeta = series_stats.get(rewritten_col_name, {})
        print(f"DEBUG: Processing {orig_ser_name} -> {rewritten_col_name}")
        print(f"DEBUG: base_summary_dict type: {type(base_summary_dict)}")
        print(f"DEBUG: base_summary_dict value: {base_summary_dict}")
        
        # Handle case where series_stats contains error strings instead of dicts
        if isinstance(base_summary_dict, str):
            print(f"DEBUG: Found error string for {rewritten_col_name}: {base_summary_dict}")
            base_summary_dict = {}
        
        print(f"DEBUG: base_summary_dict keys: {list(base_summary_dict.keys())}")
        
        for a_kls in ordered_objs:
            try:
                print(f"DEBUG: Calling {a_kls.__name__}.computed_summary with keys: {list(base_summary_dict.keys())}")
                if a_kls.quiet or a_kls.quiet_warnings:
                    if debug is False:
                        warnings.filterwarnings('ignore')
                    summary_res = a_kls.computed_summary(base_summary_dict)
                    warnings.filterwarnings('default')
                else:
                    summary_res = a_kls.computed_summary(base_summary_dict)
                print(f"DEBUG: {a_kls.__name__} returned: {list(summary_res.keys())}")
                for k,v in summary_res.items():
                    base_summary_dict.update(summary_res)
            except Exception as e:
                print(f"DEBUG: Error in {a_kls.__name__}.computed_summary: {e}")
                print(f"DEBUG: Missing keys that {a_kls.__name__} expects:")
                if hasattr(a_kls, 'requires_summary'):
                    for req_key in a_kls.requires_summary:
                        if req_key not in base_summary_dict:
                            print(f"  - {req_key}")
                if not a_kls.quiet:
                    errs[(rewritten_col_name, "computed_summary")] = e, a_kls
                if debug:
                    traceback.print_exc()
                continue
        summary_col_dict[rewritten_col_name] = base_summary_dict
    return summary_col_dict, errs


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
        print("about to call polars_produce_summary_df")
        summary_dict, summary_errs = polars_produce_summary_df(
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
