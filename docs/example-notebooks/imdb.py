import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


app._unparsable_cell(
    r"""
    import marimo as mo
    import pandas as pd
    from buckaroo.marimo_utils import marimo_monkeypatch
    marimo_monkeypatch()
    \"~/code/imdb/principals-categoricals-category-constInt-split.parq\")
    """,
    name="_"
)


@app.cell
def _():
    #title_df = pd.read_csv("~/Downloads/title.episode.tsv", delimiter="\t")
    return


@app.cell
def _():
    #principals_df = pd.read_csv("~/Downloads/title.principals.tsv", delimiter="\t")
    #principals_df = pd.read_csv("./principals-5000.tsv", delimiter="\t", on_bad_lines="warn")
    #principals_df = pd.read_csv(, delim_whitespace="\t", on_bad_lines="warn")
    #principals_df.to_parquet("~/code/imdb/principals-0-20M.parq")
    return


@app.cell
def _():
    #principals_df = pd.read_parquet("~/code/imdb/principals-0-20M.parq")
    return


@app.cell
def _():
    #principals_df.convert_dtypes().to_parquet("~/code/imdb/principals-optimized-dtypes.parq")
    return


@app.cell
def _(principals_df):
    principals_df['job'].value_counts()
    return


@app.cell
def _():
    #75_167_741 "/n rows"
    return


@app.cell
def _(principals_df):
    principals_df['characters'].value_counts()
    return


@app.cell
def _(principals_df):
    len(principals_df['category'].value_counts())
    return


@app.cell
def _(principals_df):
    len(principals_df['characters'].value_counts())
    return


@app.cell
def _():
    #principals_df['category'] = principals_df['category'].astype('category')
    #principals_df['job'] = principals_df['job'].astype('category')
    #principals_df.to_parquet("~/code/imdb/principals-categoricals-category.parq")
    return


@app.cell
def _():
    #principals_df['tconst'] = principals_df['tconst'].str.slice(2).astype('Int64')
    #principals_df.to_parquet("~/code/imdb/principals-categoricals-category-tconstInt.parq")
    return


@app.cell
def _():
    #principals_df['nconst'] = principals_df['nconst'].str.slice(2).astype('Int64')
    #principals_df.to_parquet("~/code/imdb/principals-categoricals-category-constInt.parq")
    return


@app.cell
def _():
    #principals_df['category'] = principals_df['category'].astype('category')
    #principals_df['job'] = principals_df['job'].astype('category')
    #principals_df.to_parquet("~/code/imdb/principals-categoricals.parq")
    return


@app.cell
def _():
    #small_df = principals_df.sample(500_000)
    #small_df
    return


@app.cell
def _():
    #small_df.to_parquet("~/code/imdb/principals-500k.parq")
    return


@app.cell
def _(pd):
    small_df = pd.read_parquet("~/code/imdb/principals-500k.parq")
    small_df
    return (small_df,)


@app.cell
def _(pd, small_df):
    small_df['job'] = small_df['job'].astype('string').replace('\\N', pd.NA)
    small_df['characters'] = small_df['characters'].astype('string').replace('\\N', pd.NA)
    return


@app.cell
def _():
    #small_df.to_parquet("~/code/imdb/principals-500k-non.parq")
    return


@app.cell
def _(np, pd):
    def to_top_categorical(df, col):
        ser = df[col]
        is_cat_ser = ser.isin(ser.value_counts()[:120].index.values)
        cat_ser = np.where(is_cat_ser, ser, None)

        #final_cat_ser = cat_ser.astype('category')
        regular_ser = np.where(~is_cat_ser, ser, None) #.astype('string')
        df.drop(col, axis=1, inplace=True)
        df[col+"_categorical"] = cat_ser
        df[col+"_other"] = regular_ser
        df[col+"_categorical"] =  df[col+"_categorical"].astype('category').replace('\\N', pd.NA)
        df[col+"_other"] = df[col+"_other"].astype('string').replace('\\N', pd.NA)
    return (to_top_categorical,)


@app.cell
def _(pd, to_top_categorical):
    small_df2 = pd.read_parquet("~/code/imdb/principals-500k-non.parq")
    to_top_categorical(small_df2, 'characters')
    to_top_categorical(small_df2, 'job')

    small_df2
    small_df2.to_parquet("~/code/imdb/principals-500k-split-categorical.parq")
    return (small_df2,)


@app.cell
def _(df2, to_top_categorical):
    #df2 = pd.read_parquet("~/code/imdb/principals-categoricals-category-constInt.parq")
    to_top_categorical(df2, 'characters')
    to_top_categorical(df2, 'job')
    #1md25s
    df2.to_parquet("~/code/imdb/principals-categoricals-category-constInt-split.parq")
    return


@app.cell
def _(small_df):
    small_df['job'].value_counts()[:120].sum()
    return


@app.cell
def _(small_df):
    (~small_df['job'].isna()).sum()
    return


@app.cell
def _():
    89348
    return


@app.cell
def _(small_df):
    small_df['job_cat']
    return


@app.cell
def _():
    #df['hasimage'] = np.where(df['photos']!= '[]', True, False)
    return


@app.cell
def _(small_df):
    small_df['job'].value_counts()[:120].index.values
    return


@app.cell
def _(small_df):
    import numpy as np
    small_df['job_is_categorical'] = small_df['job'].isin(small_df['job'].value_counts()[:120].index.values)
    return (np,)


@app.cell
def _(small_df):
    small_df
    return


@app.cell
def _(np, small_df):
    #df['col3'] = np.where(condition, df['col2'], None)
    small_df['job_categorical'] = np.where(small_df['job_is_categorical'], small_df['job'], None)
    return


@app.cell
def _(small_df):
    small_df['job_categorical'] = small_df['job_categorical'].astype('category')
    return


@app.cell
def _(np, small_df):
    small_df['job_regular'] = np.where(~small_df['job_is_categorical'], small_df['job'], None)
    return


@app.cell
def _(small_df):
    small_df['foo'] = 5
    return


@app.cell
def _(small_df):
    small_df.drop('foo', axis=1)
    return


@app.cell
def _(small_df):
    small_df
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
