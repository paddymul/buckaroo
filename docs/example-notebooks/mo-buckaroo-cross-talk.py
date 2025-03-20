import marimo

__generated_with = "0.11.14-dev6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


app._unparsable_cell(
    r"""
    mo.
    """,
    name="_"
)


@app.cell
async def _(mo):
    import pandas as pd
    import numpy as np
    import micropip

    await micropip.install("buckaroo")
    from buckaroo.buckaroo_widget import BuckarooInfiniteWidget, BuckarooWidget


    def BWOrig(df):
        return mo.ui.anywidget(BuckarooWidget(df))


    def BWI(df):
        return mo.ui.anywidget(BuckarooInfiniteWidget(df))
    return (
        BWI,
        BWOrig,
        BuckarooInfiniteWidget,
        BuckarooWidget,
        micropip,
        np,
        pd,
    )


@app.cell
def _(BWOrig, np, pd):
    ROWS = 13_0
    typed_df = pd.DataFrame(
        {
            "int_col": np.random.randint(1, 50, ROWS),
            "float_col": np.random.randint(1, 30, ROWS) / 0.7,
            "str_col": ["foobar"] * ROWS,
        }
    )
    widget1 = BWOrig(typed_df)
    widget1
    return ROWS, typed_df, widget1


@app.cell
def _(BWOrig, np, pd):
    ROWS2 = 34_0
    typed_df2 = pd.DataFrame(
        {
            "int_col2": np.random.randint(1, 50, ROWS2),
            "float_col2": np.random.randint(1, 30, ROWS2) / 0.7,
            "str_col2": ["foobar"] * ROWS2,
        }
    )
    widget2 = BWOrig(typed_df2)
    widget2
    return ROWS2, typed_df2, widget2


@app.cell
def _(widget2):
    widget2.widget.dataflow.raw_df.columns
    return


@app.cell
def _(widget1):
    widget1.widget.dataflow.raw_df.columns
    return


@app.cell
def _(widget1, widget2):
    len(widget1.widget._esm), len(widget2.widget._esm)
    return


@app.cell
def _(widget1, widget2):
    widget1.widget._esm == widget2.widget._esm
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
