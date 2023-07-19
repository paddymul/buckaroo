import graphlib
import unittest
import pandas as pd
import numpy as np
from collections import OrderedDict

class ColAnalysis(object):
    """
    Col Analysis runs on a single column
    """
    requires_raw = False
    requires_summary = [] # What summary stats does this analysis provide
    provides_summary = [] # mean/max/histogram
    provides_cleaning = None # or the name of the set of transforms this provides for column reordering
    provides_table_hints = None # display hints provided ex 'red_negative'

    @staticmethod
    def summary(sampled_ser, summary_ser):
        pass

    @staticmethod
    def column_order(sampled_ser, summary_ser):
        pass

    @staticmethod
    def cleaning(sampled_ser, summary_ser):
        #I want this to emit Operations for consumption by the UI and
        #possibly the transformed dataframe, not sure
        pass
    
    @staticmethod
    def table_hints(sampled_ser, summary_ser):
        pass

    @classmethod
    def cname(kls):
        #print(dir(kls))
        return kls.__qualname__
    


class NotProvidedException(Exception):
    pass

def check_solvable(a_objs):
    """
    checks taht all of the required  inputs are provided by another analysis object.
    """
    provided = []
    required = []
    for ao in a_objs:
        provided.extend(ao.provided_summary)
        required.extend(ao.requires_summary)
    all_provided = set(provided)
    all_required = set(required)
    if not all_required.issubset(all_provided):
        missing = all_required - all_provided
        raise NotProvidedException("Missing provided analysis for %r" % missing)

def remove_duplicates(lst):
    return list(OrderedDict.fromkeys(lst))

def clean_list(full_class_list):
    only_kls_lst = [kls for kls in full_class_list if not kls == None]
    #note I also want someway to detect that classes don't alternate
    # ['a', 'a', 'b', 'c', 'c'] # fine
    # ['a', 'a', 'b', 'a', 'c'] # something went wrong with the graph algo
    return remove_duplicates(only_kls_lst)


def order_analysis(a_objs):
    """order a set of col analysis objects such that the dag of their
    provided_summary and requires_summary is ordered for computation
    """


    graph = {}
    key_class_objs = {}
    for ao in a_objs:
        temp_provided = ao.provided_summary[0]
        first_mid_key = mid_key = ao.__name__ + "###" + temp_provided
        for k in ao.provided_summary[1:]:
            #print("k", k)
            next_mid_key = ao.__name__ + "###" + k
            graph[mid_key] = set([next_mid_key])
            key_class_objs[mid_key] = ao
            mid_key = next_mid_key
        graph[mid_key] = set(ao.requires_summary)
        key_class_objs[mid_key] = ao
        for j in ao.provided_summary:
            #print("j", j)
            graph[j] = set([first_mid_key])
    ts = graphlib.TopologicalSorter(graph)
    seq =  tuple(ts.static_order())
    #print("seq", seq)
    full_class_list = [key_class_objs.get(k, None) for k in seq]
    return clean_list(full_class_list)

def produce_summary_df(df, ordered_objs, df_name='test_df'):
    """
    takes a dataframe and a list of analyses that have been ordered by a graph sort,
    then it produces a summary dataframe
    """
    errs = {}
    summary_col_dict = {}
    for ser_name in df.columns:
        ser = df[ser_name]
        summary_ser = pd.Series({}, dtype='object')
        for a_kls in ordered_objs:
            try:
                res = a_kls.summary(ser, summary_ser, ser)
                for k,v in res.items():
                    summary_ser.loc[k] = v
            except Exception as e:
                print("summary_ser", summary_ser)
                errs[ser_name] = e, a_kls
                continue
        summary_col_dict[ser_name] = summary_ser
    if errs:
        for ser_name, err_kls in errs.items():
            err, kls = err_kls
            print("%r failed on %s with %r" % (kls, ser_name, err))
        print("Reproduce")
        print("from pluggable_analysis import test_ser")
        for ser_name, err_kls in errs.items():
            err, kls = err_kls
            print("%s.summary(test_ser.%s)" % (kls.__name__, ser_name))
    return pd.DataFrame(summary_col_dict)


class AnalsysisPipeline(object):

    def __init__(self, analysis_objects, unit_test_objs=True):
        self.unit_test_objs = unit_test_objs
        self.verify_analysis_objects(analysis_objects)

    def verify_analysis_objects(self, analysis_objects):
        self.ordered_a_objs = order_analysis(analysis_objects)
        check_solvable(self.ordered_a_objs)

        if self.unit_test_objs:
            self.unit_test()

    def unit_test(self):
        pass

    def produce_summary_dataframe(self, input_df):
        output_df = produce_summary_df(input_df, self.ordered_a_objs)
        return output_df

    def add_analysis(self, new_aobj):
        new_cname = new_aobj.cname()
        new_aobj_set = []
        for aobj in self.ordered_a_objs:
            if aobj.cname() == new_cname:
                continue
            new_aobj_set.append(aobj)
        new_aobj_set.append(new_aobj)
        self.verify_analysis_objects(new_aobj_set)

        
        
        
# feature to add
## if two Analysis Classes provide the same fact, flag a warning
# run the analysis that provides less facts last.  Odds are the user is tweaking a single fact


#produce_summary_df(test_df, [DistinctCount, Len, DistinctPer], 'test_df')

#how to find the variable name for the dataframe
#[k for k,v in globals().items() if v is test_df]

