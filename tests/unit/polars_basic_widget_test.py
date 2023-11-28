import polars as pl

from buckaroo import polars_buckaroo

def test_basic_instantiation():
    polars_buckaroo.PolarsBuckarooWidget(
        pl.DataFrame({'a':[1,2,3]}), auto_clean=False)
