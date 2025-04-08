import marimo

__generated_with = "0.12.2"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        """
        We deal with data cleaning all the time as data scientists.  Most of it is repetitive doing the same thing over and over again

        Buckaroo proposes some heuristic based cleaning techniques that can be toggled through
        """
    )
    return


@app.cell
def _():
    #imagine a dataframe as follows
    import marimo as mo
    import pandas as pd
    import re
    dirty_df = pd.DataFrame({'probably_int': [10, 'a', 20, 30, "3,000"],
                             'mostly_us_dates': ["07/17/1982", "17/7/1983", "12/03/1991", "12/28/1996", "4/15/2024"],
                             'probably_bool': [True, "True", "Yes", "No", "False"]
                            })
    dirty_df
    return dirty_df, mo, pd, re


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(
        """
        From a quick eyeball we can tell the cleaned types from each column.  To clean this though, in regular pandas we have to manually scan each column, and then type from memory, stack overflow or LLM the correct transformation for each column.  The transforms are fairly limited and the heuristics are pretty obvious, but we do the same rote work.

        More importantly, in this case the transforms are obvious.  What about actual large datasets.  Or datasets where the edge cases aren't visible via `df.head()`
        """
    )
    return


@app.cell
def heuristic():
    def heuristic(f):
        """No Op for now"""
        return f
    return (heuristic,)


@app.cell
def _(heuristic, pd, re):
    # Here is what I would like configuring a heuristic system to look like
    digits_and_period = re.compile(r'[^\d\.]')

    @heuristic
    def measure_int_parse(ser):
        null_count =  (~ ser.apply(pd.to_numeric, errors='coerce').isnull()).sum()
        return {'int_parse_fraction': null_count / len(ser)}

    @heuristic
    def measure_strip_int_parse(ser):
        stripped = ser.str.replace(digits_and_period, "", regex=True)
        int_parsable = ser.astype(str).str.isdigit() #don't like the string conversion here, should still be vectorized
        parsable = (int_parsable | (stripped != ""))
        return {'strip_int_parse_fraction': parsable.sum() / len(ser)}

    TRUE_SYNONYMS = ["true", "yes", "on", "1"]
    FALSE_SYNONYMS = ["false", "no", "off", "0"]
    BOOL_SYNONYMS = TRUE_SYNONYMS + FALSE_SYNONYMS

    @heuristic
    def str_bool(ser):
        #dirty_df['probably_bool'].str.lower().isin(BOOL_SYNONYMS)
        matches = ser.str.lower().isin(BOOL_SYNONYMS)
        return {'str_bool_fraction': matches.sum() / len(ser)}
    
    measures = [measure_int_parse, measure_strip_int_parse, str_bool]
    return (
        BOOL_SYNONYMS,
        FALSE_SYNONYMS,
        TRUE_SYNONYMS,
        digits_and_period,
        measure_int_parse,
        measure_strip_int_parse,
        measures,
        str_bool,
    )


@app.cell
def _(dirty_df, measures, pd):
    pd.DataFrame({k: {m.__name__: list(m(dirty_df[k]).values())[0]  for m in measures}  for k in dirty_df.columns})
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
