.. _using:

============================
Pluggable analysis framework
============================


The pluggable analysis framework is built to make it easy to add custom analysis to table applications built with Buckaroo.  It powers summary stats and styling for buckaroo.

Why
---
when writing analysis code, I frequently wrote code that iterated over columns and built a resulting summary dataframe.  This is initially simple.  First you write transformations inline, then you probably iterate over functions that operate on each column.  Eventually this type of code becomes difficult to maintain.  A single error is hard to track down because it will be in the middle of nested for loops.  For pandas in particular you face the problem of either repeating expenesive analyses over and over (value counts) or depending on state in an adhoc way.  Your simple functions become complex and dependent on order of execution.


How
---

The pluggable analysis framework improves these problems by
1. Writing analysis into classes that extend `ColAnalysis`
2. Requiring each analysis class to recieve previously computed values, specify which keys it depends on, and specify keys it provides along with defaults
3. Ordering analysis classes into a DAG so users don't have to manually order dependent classes.  If the DAG contains cycles or the required keys aren't provided, an error is thrown before execution with a more understandable message.
4. If an error occurs during excution, sensible error messages are displayed along with explicit steps to reproduce.  No more navigating through nested for loop stack traces and wondering what the state passed into functions was.

There are 3 main areas that the pluggable analysis framework is responsible for powering
1. Summary stats.  A dictionary of measures about each column.  These can be independently computed on a per column basis.
2. Column styling.  This is a function that takes the "required" measures about an individual column and returns a column_config.  Once again this can be computed indepently per column.  Styling also can generally be agnostic to pandas vs polars, as long as the other analysis classes provide similar measures
3. Transform functions.  Transform functions operate on the entire dataframe, and return extra summary_stats.  This is the only place you can operate on related columns.

Methods to override
===================

* Pandas / Polars specific methods to produce raw facts (covered separately)
* ``style_column``  return a column_config given column_metadata
* ``post_process_df``  modify the entire dataframe

Properties to override
======================

* ``post_processing_method``  name of the post_processing function for display in the UI
* ``pinned_rows``   Ordered list of pinned_row configs that will be show before any main data
* ``df_display_name``  Name of the display view that is visible in the UI
* ``data_key``         Which key to read the non_pinned rows from, use "main" or "empty"

Shared Summary stats properties
===============================

* ``requires_summary``    a list of keys that must be provided for this analysis to compute
* ``provides_defaults``   a dictionary from measure_key to measure of defaults that this analysis provides
* ``computed_summary``   passed the dictionary of measures, returns extra measures computed off of these, will include any measures computed by series_summary
   
Pandas specific methods
=======================
1. ``series_summary``  Passed the series and sampled series, returns a dictionary of measures
The `extending-pandas <https://github.com/paddymul/buckaroo/blob/main/example-notebooks/Extending-pandas.ipynb>`_ notebook shows all of these methods being used

Polars specific methods
=======================
1. ``select_clauses``  A list of polars expressions to be called on the dataframe.  Try to use this as much as possible, select queries are optimized heavily by polars.
2. ``column_ops``  a dictionary from measure_key to  tuple of polars selector, and a function to apply to the polars series object of each matching series.  There are some polars operations that only can be called on series and not executed as a select query.

The `extending-polars <https://github.com/paddymul/buckaroo/blob/main/example-notebooks/Extending.ipynb>`_ notebook shows all of these methods being used



Future Improvements
===================

1. Future releases of Buckaroo should include pydantic for better typing of summary stats methods
2. Better error messages.  The error messages in pluggable analysis framework seek to give you a one line reproduction fo the error found.  through some refactorings, the method names have changed.
