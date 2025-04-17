import marimo

__generated_with = "0.12.8"
app = marimo.App(width="medium")


@app.cell
def _():
    from buckaroo.jlisp.lisp_utils import s
    from buckaroo.jlisp.lispy import make_interpreter
    jl_eval, sc_eval = make_interpreter()
    return jl_eval, make_interpreter, s, sc_eval


@app.cell
def _():
    heuristic2 = {'t_str_bool':('greatest', 'and', ('gt', .7)), 
                  'regular_int_parse':('greatest', 'and', ('gt', .9)),
                  'strip_int_parse':('greatest', 'and', ('gt', .7)), 
                  't_us_dates':('only', ('gt', .6))}
    return (heuristic2,)


@app.cell
def _(s):
    l_rules = {
        ('col', 't_str_bool'):         [s('lambda'), [s('measure')], [s('>'), s('measure'), .7]],
        ('col', 'regular_int_parse'):  [s('lambda'), [s('measure')], [s('>'), s('measure'), .9]],
        ('col', 'strip_int_parse'):    [s('lambda'), [s('measure')], [s('>'), s('measure'), .7]],
        # ('only', ('gt', .6))}
        ('col', 't_us_dates'):         [s('lambda'), [s('measure')], [s('and'), [s('>'), s('measure'), .7], 100]]}
    return (l_rules,)


@app.cell
def _(s):
    # How I want it to look
    l_rules2 = {
        ('col', 't_str_bool'):         [s('greatest'), s('>'), s('measure'), .7],
        ('col', 'regular_int_parse'):  [s('greatest'), s('>'), s('measure'), .9],
        ('col', 'strip_int_parse'):    [s('greatest'), s('>'), s('measure'), .7],
        # ('only', ('gt', .6))}
        ('col', 't_us_dates'):         [s('only'), s('>'), s('measure'), .7]}

    #greatest and only are macros
    return (l_rules2,)


@app.cell
def _(mo):
    mo.md(
        r"""
        ```lisp
        (
        ('t_str_bool (greatest > measure .7))
        ('regular_int_parse (greatest > measure .9))
        ('strip_int_parse (greatest > measure .7))
        ('t_us_dates (only > measure .7)
         )

        ```
        """
    )
    return


@app.cell
def _(jl_eval, s):
    jl_eval([s('begin'), [s('define'), s('named_func'), [s('lambda'), [s('a')], [s('+'), s('a'), 3]]],
            [s('named_func'), 10]
            ])
    return


@app.cell
def _(jl_eval, s):
    jl_eval([s('begin'), s('df')], {'df':5}) == 5 # pass in a variable and return it
    jl_eval([s('begin'), [s('define'), s('df2'), 8], s('df2')], {'df':5}) == 8 # define a variable
    def dict_get(d, key, default=None):
        return d.get(key, default)
     #pass in a defined function from python
    jl_eval([s('dict_get'), s('fruits'), 'apple'], {'dict_get': dict_get, 'fruits':{'apple':9}}) == 9 
    jl_eval([s('dict_get'), s('fruits'), 'pear', 99], {'dict_get': dict_get, 'fruits':{'apple':9}}) == 99
    jl_eval([s('>'), 4, 9]) # comparison

    jl_eval([s('begin'), 
                [s('define'), s('named_func'), [s('lambda'), [s('a')], 
                                                    [s('+'), s('a'), 3]]],
                [s('named_func'), 10]
            ])  # define a lambda, assign it to a variable 'named_func', then call it with an argument of 10
    return (dict_get,)


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _(jl_eval, s):

    jl_eval(
        [s('begin'),
            [s("set!"), s("df"), 5],
            #[s('df')]
        ])
    #jl_eval([s('df')])
    #jl_eval([s('+'), 3, 8])
    return


@app.cell
def _():
    return


@app.cell
def _():
    import marimo as mo
    return (mo,)


if __name__ == "__main__":
    app.run()
