import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    return (pl,)


@app.cell
def _(pl):

    def get_categoricals(df):
        cat_columns = []
        for col in df.columns:
            if len(df[col].value_counts()) < 250:
                cat_columns.append(col)
        return cat_columns
    def scan_vc(fname, out_fname):
        small_df = pl.read_parquet(fname, n_rows=1_000_000)
        cat_columns = get_categoricals(small_df)
        select_args = []
        for k in small_df.columns:
            if k in cat_columns:
                select_args.append(pl.col(k).value_counts(sort=True).implode())
        #.select(pl.col(pl.String).value_counts(sort=True).implode())
        #pl.scan_parquet(fname).select(select_args).sink_parquet(out_fname)
        pl.scan_parquet(fname).select(select_args).collect().write_parquet(out_fname)
    
    #    scan_vc("~/JULY_FULL.parq", "~/JULY_FULL_vc.parq")

    return get_categoricals, scan_vc


@app.cell
def _(get_categoricals, pl):


    def to_categorical_parq(fname, out_fname):
        small_df = pl.read_parquet(fname, n_rows=1_000_000)
        cat_columns = get_categoricals(small_df)
        cast_args = {k:pl.Categorical for k in cat_columns}
        del small_df
        with pl.StringCache():
            pl.scan_parquet(fname).cast(cast_args).sink_parquet(out_fname)
    #to_categorical_parq("~/JULY_FULL.parq", "~/JULY_FULL_CAT.parq")

    #

    def get_enum_words(vc_df):
        #vc_df = pl.read_parquet("~/JULY_FULL_vc.parq")
        word_set = set()
        for col in vc_df.columns:
            _ser = vc_df[col].explode()
            _col_df = pl.DataFrame({'vc':vc_df[col].explode()}).unnest('vc') #.select(pl.all().exclude('count'))
            col_ser =_col_df[_col_df.columns[0]]
            word_set = word_set.union({*col_ser.to_list()})
            print("col", col, len(_col_df), len(word_set))
        return word_set

    def convert_to_enum(fname, out_fname, vc_df):
        word_set = get_enum_words(vc_df)
        word_enum = pl.Enum(list(word_set))
        enum_select = []
        for col in vc_df.columns:
            enum_select.append(pl.col(col).cast(word_enum))

        pl.scan_parquet(fname).select(enum_select).sink_parquet(out_fname)
    return (convert_to_enum,)


@app.cell
def _(convert_to_enum, pl, scan_vc):
    def long_running_function():
        scan_vc("~/JULY_FULL.parq", "~/JULY_FULL_vc.parq")
        _vc_df = pl.read_parquet("~/JULY_FULL_vc.parq")
        convert_to_enum("~/JULY_FULL.parq", "~/JULY_FULL_enum.parq", _vc_df)
    return


@app.cell
def _():
    cat_cols = [
        "Entity Type Code",
        "Replacement NPI",
        "Employer Identification Number (EIN)",
        "Provider Name Prefix Text",
        "Provider Name Suffix Text",
        "Provider Other Organization Name",
        "Provider Other Organization Name Type Code",
        "Provider Other Name Prefix Text",
        "Provider Other Name Suffix Text",
        "Provider Other Last Name Type Code",
        "Provider Business Mailing Address State Name",
        "Provider Business Mailing Address Country Code (If outside U.S.)",
        "Provider Business Practice Location Address State Name",
        "Provider Business Practice Location Address Country Code (If outside U.S.)",
        "NPI Deactivation Reason Code",
        "Provider Sex Code",
        "Provider License Number State Code_1",
        "Healthcare Provider Primary Taxonomy Switch_1",
        "Provider License Number State Code_2",
        "Healthcare Provider Primary Taxonomy Switch_2",
        "Provider License Number State Code_3",
        "Healthcare Provider Primary Taxonomy Switch_3",
        "Provider License Number State Code_4",
        "Healthcare Provider Primary Taxonomy Switch_4",
        "Provider License Number State Code_5",
        "Healthcare Provider Primary Taxonomy Switch_5",
        "Provider License Number State Code_6",
        "Healthcare Provider Primary Taxonomy Switch_6",
        "Provider License Number State Code_7",
        "Healthcare Provider Primary Taxonomy Switch_7",
        "Provider License Number State Code_8",
        "Healthcare Provider Primary Taxonomy Switch_8",
        "Provider License Number State Code_9",
        "Healthcare Provider Primary Taxonomy Switch_9",
        "Provider License Number State Code_10",
        "Healthcare Provider Primary Taxonomy Switch_10",
        "Provider License Number State Code_11",
        "Healthcare Provider Primary Taxonomy Switch_11",
        "Provider License Number State Code_12",
        "Healthcare Provider Primary Taxonomy Switch_12",
        "Healthcare Provider Taxonomy Code_13",
        "Provider License Number State Code_13",
        "Healthcare Provider Primary Taxonomy Switch_13",
        "Healthcare Provider Taxonomy Code_14",
        "Provider License Number State Code_14",
        "Healthcare Provider Primary Taxonomy Switch_14",
        "Healthcare Provider Taxonomy Code_15",
        "Provider License Number_15",
        "Provider License Number State Code_15",
        "Healthcare Provider Primary Taxonomy Switch_15",
        "Other Provider Identifier Type Code_1",
        "Other Provider Identifier State_1",
        "Other Provider Identifier Type Code_2",
        "Other Provider Identifier State_2",
        "Other Provider Identifier Type Code_3",
        "Other Provider Identifier State_3",
        "Other Provider Identifier Type Code_4",
        "Other Provider Identifier State_4",
        "Other Provider Identifier Type Code_5",
        "Other Provider Identifier State_5",
        "Other Provider Identifier Type Code_6",
        "Other Provider Identifier State_6",
        "Other Provider Identifier Type Code_7",
        "Other Provider Identifier State_7",
        "Other Provider Identifier Type Code_8",
        "Other Provider Identifier State_8",
        "Other Provider Identifier Type Code_9",
        "Other Provider Identifier State_9",
        "Other Provider Identifier Type Code_10",
        "Other Provider Identifier State_10",
        "Other Provider Identifier Type Code_11",
        "Other Provider Identifier State_11",
        "Other Provider Identifier Type Code_12",
        "Other Provider Identifier State_12",
        "Other Provider Identifier Type Code_13",
        "Other Provider Identifier State_13",
        "Other Provider Identifier Type Code_14",
        "Other Provider Identifier State_14",
        "Other Provider Identifier Type Code_15",
        "Other Provider Identifier State_15",
        "Other Provider Identifier Type Code_16",
        "Other Provider Identifier State_16",
        "Other Provider Identifier Type Code_17",
        "Other Provider Identifier State_17",
        "Other Provider Identifier Type Code_18",
        "Other Provider Identifier State_18",
        "Other Provider Identifier Type Code_19",
        "Other Provider Identifier State_19",
        "Other Provider Identifier Type Code_20",
        "Other Provider Identifier State_20",
        "Other Provider Identifier Issuer_20",
        "Other Provider Identifier Type Code_21",
        "Other Provider Identifier State_21",
        "Other Provider Identifier Issuer_21",
        "Other Provider Identifier Type Code_22",
        "Other Provider Identifier State_22",
        "Other Provider Identifier Issuer_22",
        "Other Provider Identifier_23",
        "Other Provider Identifier Type Code_23",
        "Other Provider Identifier State_23",
        "Other Provider Identifier Issuer_23",
        "Other Provider Identifier_24",
        "Other Provider Identifier Type Code_24",
        "Other Provider Identifier State_24",
        "Other Provider Identifier Issuer_24",
        "Other Provider Identifier_25",
        "Other Provider Identifier Type Code_25",
        "Other Provider Identifier State_25",
        "Other Provider Identifier Issuer_25",
        "Other Provider Identifier_26",
        "Other Provider Identifier Type Code_26",
        "Other Provider Identifier State_26",
        "Other Provider Identifier Issuer_26",
        "Other Provider Identifier_27",
        "Other Provider Identifier Type Code_27",
        "Other Provider Identifier State_27",
        "Other Provider Identifier Issuer_27",
        "Other Provider Identifier_28",
        "Other Provider Identifier Type Code_28",
        "Other Provider Identifier State_28",
        "Other Provider Identifier Issuer_28",
        "Other Provider Identifier_29",
        "Other Provider Identifier Type Code_29",
        "Other Provider Identifier State_29",
        "Other Provider Identifier Issuer_29",
        "Other Provider Identifier_30",
        "Other Provider Identifier Type Code_30",
        "Other Provider Identifier State_30",
        "Other Provider Identifier Issuer_30",
        "Other Provider Identifier_31",
        "Other Provider Identifier Type Code_31",
        "Other Provider Identifier State_31",
        "Other Provider Identifier Issuer_31",
        "Other Provider Identifier_32",
        "Other Provider Identifier Type Code_32",
        "Other Provider Identifier State_32",
        "Other Provider Identifier Issuer_32",
        "Other Provider Identifier_33",
        "Other Provider Identifier Type Code_33",
        "Other Provider Identifier State_33",
        "Other Provider Identifier Issuer_33",
        "Other Provider Identifier_34",
        "Other Provider Identifier Type Code_34",
        "Other Provider Identifier State_34",
        "Other Provider Identifier Issuer_34",
        "Other Provider Identifier_35",
        "Other Provider Identifier Type Code_35",
        "Other Provider Identifier State_35",
        "Other Provider Identifier Issuer_35",
        "Other Provider Identifier_36",
        "Other Provider Identifier Type Code_36",
        "Other Provider Identifier State_36",
        "Other Provider Identifier Issuer_36",
        "Other Provider Identifier_37",
        "Other Provider Identifier Type Code_37",
        "Other Provider Identifier State_37",
        "Other Provider Identifier Issuer_37",
        "Other Provider Identifier_38",
        "Other Provider Identifier Type Code_38",
        "Other Provider Identifier State_38",
        "Other Provider Identifier Issuer_38",
        "Other Provider Identifier_39",
        "Other Provider Identifier Type Code_39",
        "Other Provider Identifier State_39",
        "Other Provider Identifier Issuer_39",
        "Other Provider Identifier_40",
        "Other Provider Identifier Type Code_40",
        "Other Provider Identifier State_40",
        "Other Provider Identifier Issuer_40",
        "Other Provider Identifier_41",
        "Other Provider Identifier Type Code_41",
        "Other Provider Identifier State_41",
        "Other Provider Identifier Issuer_41",
        "Other Provider Identifier_42",
        "Other Provider Identifier Type Code_42",
        "Other Provider Identifier State_42",
        "Other Provider Identifier Issuer_42",
        "Other Provider Identifier_43",
        "Other Provider Identifier Type Code_43",
        "Other Provider Identifier State_43",
        "Other Provider Identifier Issuer_43",
        "Other Provider Identifier_44",
        "Other Provider Identifier Type Code_44",
        "Other Provider Identifier State_44",
        "Other Provider Identifier Issuer_44",
        "Other Provider Identifier_45",
        "Other Provider Identifier Type Code_45",
        "Other Provider Identifier State_45",
        "Other Provider Identifier Issuer_45",
        "Other Provider Identifier_46",
        "Other Provider Identifier Type Code_46",
        "Other Provider Identifier State_46",
        "Other Provider Identifier Issuer_46",
        "Other Provider Identifier_47",
        "Other Provider Identifier Type Code_47",
        "Other Provider Identifier State_47",
        "Other Provider Identifier Issuer_47",
        "Other Provider Identifier_48",
        "Other Provider Identifier Type Code_48",
        "Other Provider Identifier State_48",
        "Other Provider Identifier Issuer_48",
        "Other Provider Identifier_49",
        "Other Provider Identifier Type Code_49",
        "Other Provider Identifier State_49",
        "Other Provider Identifier Issuer_49",
        "Other Provider Identifier_50",
        "Other Provider Identifier Type Code_50",
        "Other Provider Identifier State_50",
        "Other Provider Identifier Issuer_50",
        "Is Sole Proprietor",
        "Is Organization Subpart",
        "Parent Organization TIN",
        "Authorized Official Name Prefix Text",
        "Authorized Official Name Suffix Text",
        "Healthcare Provider Taxonomy Group_1",
        "Healthcare Provider Taxonomy Group_2",
        "Healthcare Provider Taxonomy Group_3",
        "Healthcare Provider Taxonomy Group_4",
        "Healthcare Provider Taxonomy Group_5",
        "Healthcare Provider Taxonomy Group_6",
        "Healthcare Provider Taxonomy Group_7",
        "Healthcare Provider Taxonomy Group_8",
        "Healthcare Provider Taxonomy Group_9",
        "Healthcare Provider Taxonomy Group_10",
        "Healthcare Provider Taxonomy Group_11",
        "Healthcare Provider Taxonomy Group_12",
        "Healthcare Provider Taxonomy Group_13",
        "Healthcare Provider Taxonomy Group_14",
        "Healthcare Provider Taxonomy Group_15"
    ]
    return


if __name__ == "__main__":
    app.run()
