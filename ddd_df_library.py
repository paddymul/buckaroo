import marimo

__generated_with = "0.13.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    return (pd,)


@app.cell
def _(pd):
    def multi_index_cols(rows=15):
        cols = pd.MultiIndex.from_tuples([('foo', 'a'), ('foo', 'b'),  ('bar', 'a'), ('bar', 'b'), ('bar', 'c')])
        return pd.DataFrame(
            [["asdf","foo_b", "bar_a", "bar_b", "bar_c"]] * rows,
            columns=cols)
    def get_tuple_cols(rows=15):
        multi_col_df = multi_index_cols(rows)
        multi_col_df.columns = multi_col_df.columns.to_flat_index()
        return multi_col_df
    get_tuple_cols()

    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
