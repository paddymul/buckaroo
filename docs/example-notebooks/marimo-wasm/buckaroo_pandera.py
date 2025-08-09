import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        r"""
    # Demonstrating Buckaroo with Pandera

    [Pandera](https://github.com/unionai-oss/pandera) is a library to write schemas for data validation in DataFrames.
    [Buckaroo](https://github.com/paddymul/buckaroo) is a library to better display DataFrames in notebook environments.

    This demonstrates the new `BuckarooPandera` widget that let's you visualy pick out where errors occur in a DataFrame.
    """
    )
    return


@app.cell
async def _():
    # Initialization code that runs before all other cells
    import marimo as mo
    import numpy as np
    import sys

    if "pyodide" in sys.modules:  # make sure we're running in pyodide/WASM
        import micropip

        await micropip.install("pandera")

        await micropip.install("buckaroo")
        await micropip.install("pyarrow")

    import pandas as pd
    import pandera.pandas as pa
    from pandera import Column, Check
    import buckaroo  # to get buckaroo as the default dataframe display
    from buckaroo.contrib.buckaroo_pandera import BuckarooPandera
    return BuckarooPandera, Check, Column, mo, pa, pd


@app.cell
def _(pd):
    fruits = pd.DataFrame({"name": ["apple", "banana", "apple", "orange"], "store": ["Aldi", "Walmart", "Walmart", "Aldi"], "price": [-3, 1, 2, 4]})
    fruits
    return (fruits,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## A simple example
    Here we call `BuckarooPandera(fruits_df, schema)`
    and we see one cell highlighted because it is failing a check.
    When you hover over the highlighted cell, you will see a tooltip with the error message explaining why the check failed.
    """
    )
    return


@app.cell
def _(BuckarooPandera, Check, Column, fruits, pa):
    available_fruits = ["apple", "banana", "orange"]
    nearby_stores = ["Aldi", "Walmart"]

    schema = pa.DataFrameSchema({
        "name": Column(str, Check.isin(available_fruits)),
        "store": Column(str, Check.isin(nearby_stores)),
        "price": Column(int, Check.greater_than(0))})
    BuckarooPandera(fruits, schema)
    return (schema,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Let's look at a dataframe with no errors""")
    return


@app.cell
def _(BuckarooPandera, pd, schema):
    fruits2 = pd.DataFrame({
        "name": ["apple", "banana", "apple", "orange"], 
        "store": ["Aldi", "Walmart", "Walmart", "Aldi"], 
        "price": [2, 1, 3, 2]})
    BuckarooPandera(fruits2, schema)
    return


@app.cell
def _(Check, Column, pa, pd):
    # Schema adapted from https://www.kdnuggets.com/clean-and-validate-your-data-using-pandera
    def is_even(val):
        return val % 2 == 1


    schema2 = pa.DataFrameSchema(
        {
            "customer_id": Column(
                dtype="int64",  # Use int64 for consistency
                checks=[Check(lambda x: x > 0, element_wise=True), Check(is_even, element_wise=True), Check.isin(range(-50, 1000)), Check.isin(range(0, 1000))],  # IDs must be positive  # IDs between 1 and 999
                nullable=False,
            ),
            "name": Column(dtype="string", checks=[Check.str_length(min_value=1), Check(lambda x: x.strip() != "", element_wise=True)], nullable=False),  # Names cannot be empty
            "age": Column(
                dtype="int64",
                checks=[
                    Check.greater_than(0),  # Age must be positive
                    Check.less_than_or_equal_to(120),
                ],  # Age must be reasonable
                nullable=False,
            ),
            "email": Column(dtype="string", checks=[Check.str_matches(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")], nullable=False),
        }
    )

    kd_df = pd.DataFrame(
        {
            "customer_id": pd.Series([pd.NA, -20, 3, 4, -5, 2000, 2001, 9], dtype="Int64"),  # "invalid" is not an integer
            "name": ["Maryam", "Jane", "", "Alice", "Bobby", "k", "v", "normal"],  # Empty name
            "age": [25, -5, 30, 45, 35, 150, 7, 25],  # Negative age is invalid
            "email": ["mrym@gmail.com", "jane.s@yahoo.com", "invalid_email", "alice@google.com", None, "asdasdf", None, "good@email.com"],
        }
    )
    return kd_df, schema2


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## A more complex example

    This shows multiple errors in the same dataframe.
    At the top we see column level error reports (email and name are supposed to be dtype='string', but they are object instead)

    We also see multiple colors for errors on cells.  Every combination of failing checks gets a different color.  This lets you spot different patterns in failing checks.
    """
    )
    return


@app.cell
def _(BuckarooPandera, kd_df, schema2):
    BuckarooPandera(kd_df, schema2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # How Buckaroo Pandera works
    Take a look at [buckaroo_pandera.py](https://github.com/paddymul/buckaroo/blob/main/buckaroo/contrib/buckaroo_pandera.py) in the github repo.
    """
    )
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
