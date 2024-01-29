import polars as pl

from buckaroo import polars_buckaroo

def test_basic_instantiation():
    polars_buckaroo.PolarsBuckarooWidget(
        pl.DataFrame({'a':[1,2,3]}), )

def test_sdf_hints():
    pbw = polars_buckaroo.PolarsBuckarooWidget(
        pl.DataFrame({'a':[1,2,3]}), debug=True)
    assert pbw.merged_sd['a']['type'] == 'integer'

'''
FIXME:test a large dataframe that forces sampling
'''
