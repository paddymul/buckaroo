import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import buckaroo
    return buckaroo, pd


@app.cell
def _(pd):
    big_df = pd.read_parquet("~/code/buckaroo_data/npi_150k_100col.parq")

    big_df
    return (big_df,)


@app.cell
def _(big_df, buckaroo, pd):
    def na_outliers_only(df):
        """
            If a column has 99% NA, for that column filter to only rows that aren't NA,  Union with non na rows of other columns
        """
        mostly_na_columns = []
        for col in df.columns:
            ser = df[col]
            if (df[col].notna().sum() / len(df)) < 0.01:
                mostly_na_columns.append(col)
        all_na_outliers = ~df.all(axis=1) # start with an entirely false series
        for col in mostly_na_columns:
            all_na_outliers |= df[col].notna()
        return df[all_na_outliers]
    bw = buckaroo.BuckarooInfiniteWidget(big_df.convert_dtypes().replace('', pd.NA))
    bw.add_processing(na_outliers_only)
    bw
    return (bw,)


@app.cell
def _(bw):
    bw.dataflow.processed_df.to_csv("./for_my_cousin.csv")
    return


@app.cell
def _():
    #big_df = pd.read_parquet("~/JULY_FULL_enum.parq")[:150_000]
    #big_df = big_df[big_df.columns[:100]]
    #big_df.to_parquet("~/code/buckaroo_data/npi_150k_100col.enum.parq")

    #big_df = pd.read_parquet("~/code/buckaroo_data/npi_150k_100col.enum.parq")
    return


if __name__ == "__main__":
    app.run()
