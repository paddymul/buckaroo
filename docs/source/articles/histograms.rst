.. _using:

==========
Histograms
==========

Buckaroo uses histograms to convey the general shape of a colum in the minimum amount of screen real estate.  Like the rest of buckaroo, this is an opionated feature.





Interpreting buckaroo histograms
================================

Histograms in buckaroo are setup to give you a rough understanding of the distribution of values in a column at a glance.  This can tell you important things like "is this an ID column?" "is this a categorical column".  The following pictures give some context.


Buckaroo histograms by example
==============================


Common patterns
---------------

.. image:: ../_static/histograms-common.png
  :alt: Most common histograms
This picture shows 5 common column types.


* ``normal`` shows a numerical column with random (unordered) values from the standard distribution
* ``exponential`` shows a numerical column with random unorderd values from the exponential distribution
* ``increasing`` shows all numbers from 1 to 2000 ordered.
* ``one`` shows a column where every value is "1".  This is displayed in pink with a pattern because the histogram treats it as a categorical histogram even though it is a numerical column
* ``all_unique_cat`` shows the histogram for a string column where each value is different.  This is a categorical histogram


Categorical patterns
--------------------
	
Buckaroo has special colors and patterns for categorical type columns.  Categoricals are always displayed in decreasing order with the most frequent value on the left.  There are other special columns.  Unique and longtail are stacked.  Longtail is the sum of occurences of every value that is not unique, and is not one of the 7 most frequent categories.  Unique is the bar for values that occur only once.


.. image:: ../_static/histograms-categorical-1.png
  :alt: Most common histograms


Numeric columns with less than 5 values are treated as categoricals.  The thinking was that a limited number of values in a numeric column probably represented some type of flag field, and not a true measurement.

* ``all_NA`` has only NA/NaN values.  The red cross hatch takes up the entire histogram area
* ``half_NA`` has half NA values and the other half is filled with ``1``.
* ``longtail`` has 80% longtail values and 20% NA
* ``longtail_unique`` has half longtail values and half unique values.  Note that the bars are stacked


Numeric patterns
----------------


Numeric histograms work mostly as expected. One thing to note, there is a separate bar for the 1st and last percentile of values.  This filters out extreme values and gives much more resolution to the middle 98% of data. With such a small area, this seemed like the best approach.


.. image:: ../_static/histograms-numeric.png
  :alt: Most common histograms

* ``bimodal`` shows a bimodal distribution
* ``Exp`` shows an exponential distribution
* ``geometric`` shows a geometric distribution.  Note that this is very difficult to decipher from an exponential distribution, probably do to outlier filters and limited resolution.
* 





Simple histograms for numeric columns
=====================================

Histograms traditionally show the distribution of values in a column allowing different distributions to be identified (normal distribution, bimodal, random, skew).  This works well for accurate data without outliers.

There are a couple types of outliers that mess up normal histogrrams.

Traditional histograms make no provision for NaNs.  There are two ways we could deal with NaN's treating them as another bar, or as an independent bar.  We chose a separate bar because NaNs are a property of the entire dataset and the histogram is a function of the relevant values.  NaNs are displayed in a different color and pattern.

Sentinel values.  Columns frquently have sentinel values mixed in to convey missing data or some special condition.  After dropping NaNs, we then look at the value counts, here is one explanation of a sampling

imagine a dataset inserts 0 for NaNs, without 0's the range of numbers goes from 55 to 235, 0's account for 10% of observations.  0 is obviosuly a sentinel here and should be plotted as a categorical.  If you disagree you can write your own histogram implementation and plug it in with the pluggable analysis framework.

Extreme values.  Buckaroo limits the extents of the set where the histogram is computed so that of the 10 bins, no single bin represents more than 50% of samples, limited to the quantile range from (0.1 to 0.9).  The reasoning is that the extreme values represent errant values if they are so far off that they mess up the range of the rest of the histogram.  I haven't decided how to convey which quantile range was chosen.


Categorical Histograms for everything else
==========================================

Histograms are generally considered for numeric columns. Most datasets have many categorical or non numeric values, how can we get a quick overview of them?

Well we already know how to plot NaNs, there are three other sentinel values that matter False, True, and "0".

Remaining categoricals are plotted as a long tail plot, most frequent on the left with decreasing frequency to the right.  The top 7 most frequent values are plotted, with a final bar of "long tail" consisting of the sum of all the remaining values"



Objections to this approach
===========================

This is not a traditional histogram and should not be read as such.  It is the best way to show the most insight about frequency of values in a column that we could come up with.


Other research
==============

https://edwinth.github.io/blog/outlier-bin/

https://stackoverflow.com/questions/11882393/matplotlib-disregard-outliers-when-plotting
references

        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.



	
