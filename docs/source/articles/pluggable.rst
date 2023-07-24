.. _using:

============================
Pluggable analysis framework
============================

The pluggable analysis framework is built to allow the different bits of analysis done by buckaroo to be mixed and matched as configuration, without requiring editting the core of buckaroo.  Pieces of analysis can build on each other, and errors are flagged intelligently.


Analysis In Action
==================

The most obvious piece of analysis is adding a new measure/fact to summary stats.

A monolithic summary_stats would look like this

.. code-block:: python

def summarize_string(ser):
    l = len(ser)
    val_counts = ser.value_counts()
    distinct_count= len(val_counts)

    return dict(
        dtype=ser.dtype,
        length=l,
        min='',
        distinct_count= distinct_count,
        distinct_percent = distinct_count/l)

def summarize_df(df):
    summary_df = pd.DataFrame({col:summarize_string(df[col]) for col in df})
    return summary_df


If you wanted to enhance that simple summary_stat by adding nan_count and nan_percent, you would have to rewrite the entire function and get buckaroo to use your new function.  Instead, imagine that the existing ``sumarize_string`` was already built into Buckaroo and you wanted to add to it. Here's what the code looks like.


.. code-block:: python

bw = BuckarooWidget(df)
@bw.add_analysis
class NanStats(ColAnalysis):
    provided_summary = [
        'nan_count', 'nan_percent']
    requires_summary = ['length']

    @staticmethod
    def summary(sampled_ser, summary_ser, ser):
        l = summary_ser.loc['min']
        nan_count = l - len(ser.dropna())
        return dict(
	    nan_count = nan_count,
            nan_percent = nan_count/l)
bw  #render the buckaroo widget


Now buckaroo will be displayed with the new summary stats of 'nan_count' and 'nan_percent'.  Buckaroo knows that ``NanStats`` must be called after the ``ColAnalysis`` object that provides ``length`` and that ordering is handled for you automatically (via a DAG).

You can then iteratively and interactively update your analysis in the jupyter notebook focussing on the core of your business logic without worrying about how to structure your code.  When ``add_analysis`` is called, a set of simple unit tests are run that catch common errors with weird datashapes.  This means you can focus on coding and not worry about all the edge cases.

