import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    from buckaroo.marimo_utils import marimo_monkeypatch
    marimo_monkeypatch()
    #df = pd.read_parquet("~/code/imdb/principals-categoricals-category-constInt-split.parq")
    df = pd.read_parquet("~/code/imdb/principals-categoricals-category-constInt-split-downcast-dropother.parq")
    return df, marimo_monkeypatch, mo, pd


@app.cell
def _(df):
    df
    return


@app.cell
def _():
    #df['nconst'] = pd.to_numeric(df['nconst'], downcast="unsigned")
    #df['tconst'] = pd.to_numeric(df['tconst'], downcast="unsigned")
    #df['ordering'] = pd.to_numeric(df['ordering'], downcast="unsigned")
    return


@app.cell
def _():
    #df.to_parquet("~/code/imdb/principals-categoricals-category-constInt-split-downcast.parq")
    return


@app.cell
def _():
    #df.drop('job_other', inplace=True, axis=1)
    #df.drop('characters_other', inplace=True, axis=1)
    return


@app.cell
def _():
    #df.to_parquet("~/code/imdb/principals-categoricals-category-constInt-split-downcast-dropother.parq")
    return


@app.cell
def _(df):
    df[:5000]
    return


@app.cell
def _(df):
    df['job_other'].str.lower().value_counts()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
