import marimo

__generated_with = "0.12.2"
app = marimo.App(width="medium")


@app.cell
def _(mo):
    mo.md(
        """
        We deal with data cleaning all the time as data scientists.  Most of it is repetitive doing the same thing over and over again

        Buckaroo proposes some frac based cleaning techniques that can be toggled through
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
                             'mostly_us_dates': ["07/17/1982", "17/7/1983", "12/14/1991", "12/28/1996", "4/15/2024"],
                             'probably_bool': [True, "True", False, "No", "False"]
                            })
    dirty_df
    return dirty_df, mo, pd, re


@app.cell
def _(mo):
    mo.md(
        """
        From a quick eyeball we can tell the cleaned types from each column.  To clean this though, in regular pandas we have to manually scan each column, and then type from memory, stack overflow or LLM the correct transformation for each column.  The transforms are fairly limited and the fracs are pretty obvious, but we do the same rote work.

        More importantly, in this case the transforms are obvious.  What about actual large datasets.  Or datasets where the edge cases aren't visible via `df.head()`
        """
    )
    return


@app.cell
def _():
    return


@app.cell
def frac():
    def frac(f):
        """No Op for now.  This denotes that the function produces a 0-1 rating for a series that's passed in"""
        return f
    return (frac,)


@app.cell
def _(frac, pd, re):
    # Here is what I would like configuring a frac system to look like
    digits_and_period = re.compile(r'[^\d\.]')

    @frac
    def measure_int_parse(ser):
        null_count =  (~ ser.apply(pd.to_numeric, errors='coerce').isnull()).sum()
        return {'int_parse_fraction': null_count / len(ser)}

    @frac
    def measure_strip_int_parse(ser):
        stripped = ser.str.replace(digits_and_period, "", regex=True)
        int_parsable = ser.astype(str).str.isdigit() #don't like the string conversion here, should still be vectorized
        parsable = (int_parsable | (stripped != ""))
        return {'strip_int_parse_fraction': parsable.sum() / len(ser)}

    TRUE_SYNONYMS = ["true", "yes", "on", "1"]
    FALSE_SYNONYMS = ["false", "no", "off", "0"]
    BOOL_SYNONYMS = TRUE_SYNONYMS + FALSE_SYNONYMS

    @frac
    def str_bool(ser):
        #dirty_df['probably_bool'].str.lower().isin(BOOL_SYNONYMS)
        matches = ser.str.lower().isin(BOOL_SYNONYMS)
        return {'str_bool_fraction': matches.sum() / len(ser)}

    frac_measures = [measure_int_parse, measure_strip_int_parse, str_bool]
    return (
        BOOL_SYNONYMS,
        FALSE_SYNONYMS,
        TRUE_SYNONYMS,
        digits_and_period,
        frac_measures,
        measure_int_parse,
        measure_strip_int_parse,
        str_bool,
    )


@app.cell
def _(dirty_df, frac_measures, pd):
    pd.DataFrame({k: {m.__name__: list(m(dirty_df[k]).values())[0]  for m in frac_measures}  for k in dirty_df.columns})
    return


@app.cell
def _(mo):
    mo.md(
        """
        Ok, this is looking pretty good.  We have 3 fracs, applied to 3 columns (but they are only made for two of the columns),  and we can see how frequently they get the right answer.

        Let's add more fracs
        """
    )
    return


@app.cell
def _(dirty_df, frac, frac_measures, pd):
    @frac
    def us_dates(ser):
        parsed_dates = pd.to_datetime(ser, errors='coerce', format="%m/%d/%Y")
        return {'us_date_fraction': (~ parsed_dates.isna()).sum() / len(ser)}

    @frac
    def euro_dates(ser):
        parsed_dates = pd.to_datetime(ser, errors='coerce', format="%d/%m/%Y")
        return {'us_date_fraction': (~ parsed_dates.isna()).sum() / len(ser)}
    more_fracs = frac_measures + [us_dates, euro_dates]
    pd.DataFrame({k: {m.__name__: list(m(dirty_df[k]).values())[0]  for m in more_fracs}  for k in dirty_df.columns})
    return euro_dates, more_fracs, us_dates


@app.cell
def _(mo):
    mo.md(
        """
        Things get interesting here.  Every row from mostly_us_dates parses as a number, even though the best date parsing only gets 0.8.  But we know that these are dates from looking at the data.  How should we resolve this?

        That's an open question.
        Either way, let's start writing some transform functions.
        """
    )
    return


@app.cell
def transform():
    def transform(frac):
        """Pair a transform function that actually cleans a series with the frac. used as a decorator """
        def dec(f):
            return f
        return dec
    return (transform,)


@app.cell
def _(digits_and_period, pd):
    _ser = pd.Series([10, 'a', 20, 30, "3,000"])
    _reg_parse = _ser.apply(pd.to_numeric, errors='coerce')
    _strip_parse = _ser.str.replace(digits_and_period, "", regex=True).apply(pd.to_numeric, errors='coerce')
    _combined = _reg_parse.fillna(_strip_parse)
    pd.DataFrame({'_ser':_ser, 'combined': _combined, '_reg_parse':_reg_parse, '_strip_parse':_strip_parse})
    return


@app.cell
def _(
    FALSE_SYNONYMS,
    TRUE_SYNONYMS,
    digits_and_period,
    measure_int_parse,
    measure_strip_int_parse,
    pd,
    reg_parse,
    str_bool,
    transform,
):
    @transform(measure_int_parse)
    def regular_int_parse(ser):
        return ser.apply(pd.to_numeric, errors='coerce')

    @transform(measure_strip_int_parse)
    def strip_int_parse(ser):
        _reg_parse = ser.apply(pd.to_numeric, errors='coerce')
        _strip_parse = ser.str.replace(digits_and_period, "", regex=True).apply(pd.to_numeric, errors='coerce')
        _combined = reg_parse.fillna(_strip_parse)
        return _combined

    @transform(str_bool)
    def t_str_bool(_ser):
        _int_sanitize = _ser.replace(1, True).replace(0, False) 
        _real_bools = _int_sanitize.isin([True, False])
        _boolean_ser = _int_sanitize.where(_real_bools, pd.NA).astype('boolean')    
        _trues = _ser.str.lower().isin(TRUE_SYNONYMS).replace(False, pd.NA).astype('boolean')
        _falses =  ~ (_ser.str.lower().isin(FALSE_SYNONYMS).replace(False, pd.NA)).astype('boolean')
        _combined = _boolean_ser.fillna(_trues).fillna(_falses)    
        return _combined
    # t_str_bool(pd.Series(["asdf", True, "True", "1", 0, None, 1]))
    return regular_int_parse, strip_int_parse, t_str_bool


@app.cell
def _(mo):
    mo.md(
        """
        Side note.  These functions are tricky to write.  So many edge cases.
        I see why I and most people punt on writing this stuff.  It's tricky and shouldn't have to be repeated.  The `t_str_bool` was one of the ahrdest to write.  Look at the commented out mini test case

        """
    )
    return


@app.cell
def _(mo):
    mo.md(
        """
        Now to write the syntax for the heuristic class.

        The idea is that when each matching frac is the heighest percentage, apply that transform function to that column

        Writing `transforms` and `fracs` is tricky and will be done infrquently.  Writing heuristic sets will be done regularly, and lets you toggle through different views
        """
    )
    return


@app.cell
def _(regular_int_parse, strip_int_parse, t_str_bool):
    heuristic = {t_str_bool:.7, regular_int_parse:.9, strip_int_parse:.7}
    return (heuristic,)


@app.cell(hide_code=True)
def _():
    #Also, our nested dictionary comprehension to dataframe is cute, but watch what happens when we have an error measure
    #error_measures = measures + [lambda x: 1/0] + [us_dates]
    #pd.DataFrame({k: {m.__name__: list(m(dirty_df[k]).values())[0]  for m in error_measures}  for k in dirty_df.columns})
    # what column threw the error. what happened to the rest of the code?
    return


if __name__ == "__main__":
    app.run()
