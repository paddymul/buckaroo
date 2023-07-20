from buckaroo.pluggable_analysis_framework import (
    ColAnalysis, order_analysis, check_solvable, NotProvidedException,
    produce_summary_df)
FAST_SUMMARY_WHEN_GREATER = 1_000_000


class AnalsysisPipeline(object):
    """
    manage the ordering of a set of col_analysis objects
    allow for computing summary_stats (and other oberservation sets) based on col_analysis objects
    allow col_anlysis objects to be added
    """
    def __init__(self, analysis_objects, unit_test_objs=True):
        self.unit_test_objs = unit_test_objs
        self.verify_analysis_objects(analysis_objects)

    def verify_analysis_objects(self, analysis_objects):
        self.ordered_a_objs = order_analysis(analysis_objects)
        check_solvable(self.ordered_a_objs)

        if self.unit_test_objs:
            self.unit_test()

    def unit_test(self):
        """test a single, or each col_analysis object with a set of commonly difficult series.
        not implemented yet.

        This helps interactive development by doing a smoke test on
        each new iteration of summary stats function

        """
        pass

    def produce_summary_df(self, input_df):
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

class DfStats(object):
    '''
    DfStats exists to handle inteligent downampling and applying the ColAnalysis functions
    '''

    def __init__(self, df, col_analysis_objs):
        self.df = self.get_operating_df(df, force_full_eval=False)
        self.col_order = self.df.columns
        self.ap = AnalsysisPipeline(col_analysis_objs)
        self.sdf = self.ap.produce_summary_df(self.df)

    def get_operating_df(self, df, force_full_eval):
        rows = len(df)
        cols = len(df.columns)
        item_count = rows * cols

        if item_count > FAST_SUMMARY_WHEN_GREATER:
            return df.sample(np.min([50_000, len(df)]))
        else:
            return df
