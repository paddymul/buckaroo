import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    import buckaroo
    return (pl,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # Dealing with entire large dataframes

    This blog walks through some techniques for dealing with a large dataframe when you need to look at the entire thing.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
    # digging in
    `get_categoricals`  
    d
    """
    )
    return


@app.cell
def _(pl):
    def get_lazy_df(fname):
        if fname.endswith("csv"):
            return pl.scan_csv(fname)
        else:
            return pl.scan_parquet(fname)

    def get_categoricals(df, n_vals=250):
        cat_columns = []
        for col in df.columns:
            if len(df[col].value_counts()) < n_vals:
                cat_columns.append(col)
        return cat_columns

    def scan_vc(fname, out_fname, n_rows=500_000):
        small_df = get_lazy_df(fname)[:n_rows].collect()
        #small_df = pl.read_parquet(fname, n_rows=n_rows)
        cat_columns = get_categoricals(small_df)
        print("finished get_categoricals this many columns", len(cat_columns))
        select_args = []
        for k in small_df.columns:
            if k in cat_columns:
                select_args.append(pl.col(k).value_counts(sort=True).implode())
        #lazy_df = pl.scan_csv(fname) if fname.endswith("csv") else pl.scan_parquet(fname)
        get_lazy_df(fname).select(select_args).sink_parquet(out_fname)
    #scan_vc("~/JULY_FULL.parq", "~/JULY_FULL_vc2.parq")
    #this took 57 seconds on my MBA M1
    return get_categoricals, scan_vc


@app.cell
def _():
    #scan_vc("~/NPPES_Data_Dissemination_July_2025/npidata_pfile_20050523-20250713.csv", "~/JULY_FULL_vc2.parq")
    #1m24s on my laptop
    return


@app.cell
def _(pl):
    vc_df = pl.read_parquet("~/JULY_FULL_vc2.parq")
    vc_df
    return (vc_df,)


@app.cell
def _(pl, vc_df):
    vc_df.select([pl.all().explode().len()]).transpose(include_header=True).sort('column_0')
    return


@app.cell
def _(get_categoricals, pl):


    def to_categorical_parq(fname, out_fname):
        small_df = pl.read_parquet(fname, n_rows=1_000_000)
        cat_columns = get_categoricals(small_df)
        cast_args = {k:pl.Categorical for k in cat_columns}
        del small_df
        with pl.StringCache():
            pl.scan_parquet(fname).cast(cast_args).sink_parquet(out_fname)

    def get_enum_words(vc_df):
        word_set = set()
        for col in vc_df.columns:
            _ser = vc_df[col].explode()
            _col_df = pl.DataFrame({'vc':vc_df[col].explode()}).unnest('vc')
            col_ser =_col_df[_col_df.columns[0]]
            word_set = word_set.union({*col_ser.to_list()})
            print("col", col, len(_col_df), len(word_set))
        return word_set

    def convert_to_enum(fname, out_fname, vc_df):
        word_set = get_enum_words(vc_df)
        print("got word_set")
        word_enum = pl.Enum(list(word_set))
        enum_select = []
        for col in vc_df.columns:
            enum_select.append(pl.col(col).cast(word_enum))
        pl.scan_parquet(fname).select(enum_select).sink_parquet(out_fname)
    return (convert_to_enum,)


@app.cell
def _():
    #takes 33 seconds on my machine
    #convert_to_enum("~/JULY_FULL.parq", "~/JULY_FULL_enum2.parq", vc_df)
    return


@app.cell
def _(pl):
    def convert_to_enum3(fname, out_fname, vc_df):
        enum_select = []
        for col in vc_df.columns:
            enum_select.append(pl.col(col))
        pl.scan_parquet(fname).select(enum_select).sink_parquet(out_fname)
    #22 seconds on my machine
    #convert_to_enum3("~/JULY_FULL.parq", "~/JULY_FULL_enum3.parq", vc_df)
    return


@app.cell
def _(pl):
    _ROWS=5
    _COLS=5
    _df = pl.read_parquet("~/JULY_FULL_enum2.parq", n_rows=_ROWS)
    _df[_df.columns[:_COLS]]
    return


@app.cell
def _(pl):
    pl.read_parquet("~/JULY_FULL_enum3.parq", n_rows=5000)
    return


@app.cell
def _():
    import fastparquet

    return (fastparquet,)


@app.cell
def _(fastparquet):
    pf2 = fastparquet.ParquetFile("/Users/paddy/JULY_FULL_enum2.parq")
    pf2.schema.schema_elements_by_name["Provider License Number State Code_7"]
    return


@app.cell
def _(fastparquet):
    pf3 = fastparquet.ParquetFile("/Users/paddy/JULY_FULL_enum3.parq")
    pf3.schema.schema_elements_by_name["Provider License Number State Code_7"]
    return


@app.cell
def _(convert_to_enum, pl, scan_vc):
    def long_running_function():
        scan_vc("~/JULY_FULL.parq", "~/JULY_FULL_vc.parq")
        _vc_df = pl.read_parquet("~/JULY_FULL_vc.parq")
        convert_to_enum("~/JULY_FULL.parq", "~/JULY_FULL_enum.parq", _vc_df)
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
