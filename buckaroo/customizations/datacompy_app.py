import pandas as pd
import datacompy
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import ColAnalysis
from buckaroo import BuckarooWidget


def DatacompyBuckaroo(df1, df2):
    cmp = datacompy.Compare(
        df1, df2,
        join_columns='A',  # Column to join DataFrames on
        abs_tol=0,  # Absolute tolerance
        rel_tol=0)  # Relative tolerance
    
    def get_df_header(cmp):
        df_header = pd.DataFrame({        
            "DataFrame": [cmp.df1_name, cmp.df2_name],
            "Columns": [cmp.df1.shape[1], cmp.df2.shape[1]],
            "Rows": [cmp.df1.shape[0], cmp.df2.shape[0]]}) #, columns=[0, 1])
        return df_header.T
    
    def column_summary(cmp):
        df1_name = cmp.df1_name
        df2_name = cmp.df2_name
        col_df = pd.DataFrame({
            "Columns in common":[len(cmp.intersect_columns())],
            f"Columns in {df1_name} not in {df2_name}":[ cmp.df1_unq_columns().items],
            f"Columns in {df2_name} not in {df1_name}":[ cmp.df2_unq_columns().items]})
        return col_df.T
    
    def row_summary(cmp):
        # write pad arr function to pad array to number of join columns
        match_criteria = "index"
        if not cmp.on_index:
            match_criteria = ", ".join(cmp.join_columns)
            has_dupes = cmp._any_dupes
            df1_name = cmp.df1_name
            df2_name = cmp.df2_name
    
        row_df = pd.DataFrame({
            "Matched On": [match_criteria],
            "Any Duplicates on match values": [has_dupes],
            "Number of rows in common": cmp.intersect_rows.shape[0],
            f"Number of rows in {df1_name} but not in {df2_name}": cmp.df1_unq_rows.shape[0],
            f"Number of rows in {df2_name} but not in {df1_name}": cmp.df2_unq_rows.shape[0],
            "Number of rows with some compared columns unequal": [cmp.intersect_rows.shape[0] - cmp.count_matching_rows()],
            "Number of rows with all compared columns equal": [cmp.count_matching_rows()]
        })
        return row_df.T
    
    def column_matching(cmp):
        unequal_count = len([col for col in cmp.column_stats if col["unequal_cnt"] > 0])
        equal_count = len([col for col in cmp.column_stats if col["unequal_cnt"] == 0])
        total_unequal_count = sum(col["unequal_cnt"] for col in cmp.column_stats)
    
        col_df = pd.DataFrame({
            "Number of columns compared with some values unequal": [unequal_count],
            "Number of columns with all values equal": [equal_count],
            "Total number of values which compare unequal": [total_unequal_count]})
        return col_df.T
    
    def match_stats(cmp, sample_count=10):
        match_stats = []
        match_sample = []
        any_mismatch = False
        for column in cmp.column_stats:
            if not column["all_match"]:
                any_mismatch = True
                match_stats.append({
                    "Column": column["column"],
                    f"{cmp.df1_name} dtype": column["dtype1"],
                    f"{cmp.df2_name} dtype": column["dtype2"],
                    "# Unequal": column["unequal_cnt"],
                    "Max Diff": column["max_diff"],
                    "# Null Diff": column["null_diff"]})
            if column["unequal_cnt"] > 0:
                match_sample.append(
                    cmp.sample_mismatch(
                        column["column"], sample_count, for_display=True))
    
        df_match_stats = pd.DataFrame(match_stats)
        df_match_stats.sort_values("Column", inplace=True)
        return df_match_stats.T

    class DfHeader(ColAnalysis):
        @classmethod
        def post_process_df(kls, df):
            ab = get_df_header(cmp)
            print("ab", ab)
            return [ab, {}]
        post_processing_method = "Df Headers"


    class ColumnSummary(ColAnalysis):
        @classmethod
        def post_process_df(kls, df):
            col_summary_df = column_summary(cmp)
            print("col_summary", col_summary_df)
            return [col_summary_df, {}]
        post_processing_method = "Column Summary"

    class RowSummary(ColAnalysis):
        @classmethod
        def post_process_df(kls, df):
            return [row_summary(cmp), {}]
        post_processing_method = "Row Summary"

    class ColumnMatching(ColAnalysis):
        @classmethod
        def post_process_df(kls, df):
            return [column_matching(cmp), {}]
        post_processing_method = "Column Matching"

    class MatchStats(ColAnalysis):
        @classmethod
        def post_process_df(kls, df):
            return [match_stats(cmp), {}]
        post_processing_method = "Match Stats"

        
    datacompy_post_processing_klasses = [
        DfHeader, ColumnSummary, RowSummary, ColumnMatching, MatchStats]
    
    base_a_klasses = BuckarooWidget.analysis_klasses.copy()
    base_a_klasses.extend(datacompy_post_processing_klasses)
    class DatacompyBuckarooWidget(BuckarooWidget):
        analysis_klasses = base_a_klasses
    dcbw = DatacompyBuckarooWidget(pd.DataFrame({}, columns=[0,1]), debug=False)
    return dcbw
    
dcbw = DatacompyBuckaroo(df_a, df_b)
dcbw
