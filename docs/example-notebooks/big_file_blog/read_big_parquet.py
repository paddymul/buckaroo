import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import polars as pl
    #12 seconds to read from parquet
    #df = pl.read_parquet("~/JULY_FULL.parq")
    #filtered_df = pl.scan_parquet("~/JULY_FULL.parq").filter(pl.any_horizontal(pl.col(pl.String).str.contains('UNAV'))).collect()
    #df
    return (pl,)


@app.cell
def _():
    #on the full df this took 26 seconds
    #df.filter(pl.any_horizontal(pl.col(pl.String).str.contains('UNAV')))
    return


@app.cell
def _(pl):
    df_orig = pl.read_parquet("~/JULY_FULL.parq", n_rows=20_000)
    df_orig
    return (df_orig,)


@app.cell
def _(df):
    df.columns[3]
    return


@app.cell
def _(df):
    df.columns[50],df.columns[51]
    return


@app.cell
def _(df, pl):
    df.select(pl.col("Healthcare Provider Primary Taxonomy Switch_1").value_counts(sort=True).implode())
    #  "Healthcare Provider Taxonomy Code_2"
    #])
    return


@app.cell
def _(pl):
    _vc_df = pl.read_parquet("~/JULY_FULL_vc.parq")
    _col = _vc_df.columns[0]
    print("col", _col)
    _vc_df[_col].explode()
    pl.DataFrame({'vc': _vc_df[_vc_df.columns[0]].explode()}).unnest('vc').select(pl.all().exclude('count'))
    return


@app.cell
def _(pl):
    vc_df = pl.read_parquet("~/JULY_FULL_vc.parq")
    word_set = set()
    for col in vc_df.columns:
        print(col)
        _ser = vc_df[col].explode()
        #print("ser", ser[0])
        _col_df = pl.DataFrame({'vc':vc_df[col].explode()}).unnest('vc') #.select(pl.all().exclude('count'))
        #print("col", len(col_df))
        col_ser =_col_df[_col_df.columns[0]]
        word_set = word_set.union({*col_ser.to_list()})
        print("col", col, len(_col_df), len(word_set))


    return vc_df, word_set


@app.cell
def _(pl, word_set):
    word_enum = pl.Enum(list(word_set))
    return (word_enum,)


@app.cell
def _(vc_df):
    vc_col1 = vc_df.columns[0]
    vc_col1
    return (vc_col1,)


@app.cell
def _(df_orig, pl, vc_col1, word_enum):
    df_orig.select(pl.col(vc_col1).cast(word_enum))
    return


@app.cell
def _(df_orig, pl, vc_col1):
    f_ser_1 = df_orig.select(pl.col(vc_col1))
    #f_ser_1 = df_orig[vc_col1]
    #f_ser_1.toa
    #f_ser_1.cast(word_enum)
    return


@app.cell
def _(word_set):
    len(word_set)
    return


@app.cell
def _(pl):
    help(pl.Enum)
    return


app._unparsable_cell(
    r"""
        {*col_ser.to_list()}
    """,
    name="_"
)


@app.cell
def _():
    a = {3,4,4}
    a
    return (a,)


@app.cell
def _(a):
    a.up
    return


@app.cell
def _(pl):
    df = pl.read_parquet("~/JULY_FULL_CAT.parq", n_rows=1_000_000)
    df
    return (df,)


@app.cell
def _(df):
    ab = df[df.columns[3]]
    ab
    return (ab,)


@app.cell
def _(ab):
    ab.value_counts()
    return


@app.cell
def _(pl):
    cat_cols = ['a','b']
    cast_args = {k:pl.Categorical for k in cat_cols}
    cast_args
    return


@app.cell
def _(df, pl):

    # This takes 34 seconds:
    with pl.StringCache():
        df2 = df.cast({df.columns[3]: pl.Categorical})
    df2
    return


@app.cell
def _(df):
    def to_categoricals(df):
        cat_columns = []
        for col in df.columns:
            if len(df[col].value_counts()) < 250:
                cat_columns.append(col)
        return cat_columns
    to_categoricals(df)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
