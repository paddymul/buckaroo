.. _using:

Data Flow through Buckaroo
==========================


Buckaroo is extensible.  The architecture of Buckaroo is crafted to allow specific points of composable extensibility in an opinionated manner.  It was designed this way based on experience from writing many adhoc analysis pipelines.  Previous "simpler" attempts at extensibility ran into bugs that couldn't be cleanly accomodated. The following will be addressed below:

Buckaroo aims to allow highly opionated configurations to be toggled by users.  With buckaroo, you can add a cleaning_method of "interpret int as milliseconds from unix epoch", and it will look at a column of ints, and decide that values map to datetimes in the past year (as opposed to centered around 1970) and we should treat this column as a datetime.  That is a highly opinionated view of your data, the cost for that highly opinonated view is less when multiple opinions can be quickly cycled through.

This approach is different than most tools which aim to be a generic tool that is customizable with bespoke configuration.  It would be a bad thing if a generic table tool displayed integers as dates because it assumes that those integers are milliseconds from the unix epoch.  Normally this would require custom code to be written and called based on manual inspection of the data.

This document describes the multiple ways of extending bucakroo to add your own toggable opinons.






#. understand the dataflow through Buckaroo
#. quick start to extending buckaroo
#. description of extension points


Customization points of Buckaroo
--------------------------------


#. Sample_method
   Used to specify conditions for downsampling dataframe and method of sampling.  Example alternatives include sampling in chunks,  only showing first and last row, random sampling, and limiting number of columns.  Returns  sampled df
#. Cleaning_method
   recieves sampled_dataframe Used to control how dataframes are cleaned before summary stats are run.  Examples include special parsing rules for unique date formats, removing strings from primarily numeric columns.  Returns cleaned_df and cleaned_summary_dict
#. Post_processing_method
   recieves entire cleaned dataframe. Used to perform multi-column operations, like adding a running_diff column, or combining a latitude and longitude column into a single lat/long column.  returns processed_df and processed_summary_dict
#. Analysis_klasses
   recieves individual columns from processed_df.  Individual column level analysis klasses used to fill out summary_stats.  examples include mean, median, min, max, and complex results like histograms.  Each class returns a summary_dict about a single column
#. style-method
   recieves col_name, col_summary_dict, default_config.  Takes a column_summary_dict and returns the column_config for that column.  Examples include formatting a datetime as time only if the min/max are within a single day, conditionally turning on tooltips and color_maps based on other info in summary_dict




ignore
'    make_getter (`operation_result`, None, ``cleaned_sd``  ``generated_code`` )
'   make_getter  (`processed_result`, ``processed_df``,  ``processed_sd`` )
   
Full Flow
---------
Use the following glyphs to understand the variables

#. ``instantiation_``        are defined at class instantiation time, or through python
#. `dependent_`              are the result of a previous step, the data_flow variable that is watched
#. `user specified`_         are specified in the UI, and can be changed interactively
#. **named_tuple_variable**  Some results return as a tuple, the tuple is what is watched, the sub parts of the tuple can be referenced later

Starting with ``raw_df`` data flows through buckaroo as follows.  If one of the values on the right side of equals changes, all steps below that are executed

The final result of `widget` is what is displayed to the user.

#. ``sampled_df``                                                   = ``raw_df``, `sample_method`_
#. ``cleaned``   = **cleaned** (**_df**, **_sd**, **generated_code**) = `sampled_df`, `cleaning_method`_, `existing_operations`_
#. ``processed`` = **processed** (**_df**, **_sd**)                 = `cleaned_.df`, `post_processing_method`_
#. ``summary_sd``                                                   = `processed_result.df`, ``analysis_klasses``
#. ``merged_sd``                                                    = ``cleaned_sd``, `summary_sd`, ``processed_sd``
#. ``widget``                                                       = ``processed_df``, `merged_sd`, `style_method`_, ``generated_code``


+----------------+------------------------------------------------------------------+
| Destination    |                               args                               |
+================+==================================================================+
| ``sampled_df`` | ``raw_df``, `sample_method`                                      |
+----------------+------------------------------------------------------------------+
| ``cleaned``    |     `sampled_df`, `cleaning_method`_, `existing_operations`_     |
+----------------+------------------------------------------------------------------+
|                | cleaned_df, cleaned_sd, generated_code                           |
+----------------+------------------------------------------------------------------+
| ``processed``  | `cleaned_.df`, `post_processing_method`_                         |
+----------------+------------------------------------------------------------------+
|                | processed_df, processed_sd                                       |
+----------------+------------------------------------------------------------------+
| ``summary_sd`` | `processed_result.df`, ``analysis_klasses``                      |
+----------------+------------------------------------------------------------------+
| ``merged_sd``  | ``cleaned_sd``, `summary_sd`, ``processed_sd``                   |
+----------------+------------------------------------------------------------------+
| ``widget``     | ``processed_df``, `merged_sd`, `style_method`_, ``cleaned_code`` |
|                |                                                                  |
+----------------+------------------------------------------------------------------+



Rewritten so each step only depends on a single generated property (but possibly two user props)
getters are specced in args surrounded in quotes

The getters are important because they get a previously created value... but they don't set up a listener.
without getters, unneeded recomps are triggered


existing_operations is an interint one.  It can be either user entered low_code ops, or the previous cleaning_operations.  merged_operations is responsible for first stripping all cleaning_operations from "existing_operations", then adding in the new "cleaning_operations".  This preserves any user netered operations


Quick Start to extending Buckaroo
---------------------------------

In this exercise we are going add a custom coloring method to Buckaroo.  We will take an OHLCV dataframecolor and Volume based on the change from the previous day.

First we need to craft the column config that will enable this conditonal coloring.

We want to use `ColorFromColumn`, we want the config for the volume column to look like

.. code-block:: python
    
    volume_config_override = {
        'color_map_config' : {
	    'color_rule': 'color_from_column',
            'col_name': 'Volume_colors'}}


Using this in Buckaroo will look like this
 
.. code-block:: python

    df = get_ohlcv("IBM")
    df['Volume_colors'] = 'red'
    BuckarooWidget(df, override_column_config={'Volume': volume_config_override})

This is a nice start.  But now our analysis depends on remembering and typing specific config lines each time we want this display.


Buckaroo provides built in ways of handling this.

First we want to use a `post_processing_function` to add the `volume_colors` column all of the time.  And to make it condtional on change.  we need to use `post_processing_function` because we specifically need to operate on the whole dataframe, not just a single column.


.. code-block:: python

    def volume_post(df):
        if 'Volume' not in df.columns:
	    return [df, {}]
	df['Volume_colors'] = 'red'  # replace with actual red/green based on diff
	extra_summary_dict = {
            'Volume' : {
	        'column_config_override': {
	            'color_map_config' :
		        {'color_rule': 'color_from_column',
			 'col_name': 'Volume_colors'}}},
            'Volume_colors' : {
	        'column_config_override': {
		    'displayer': 'hidden'}}}
	return [df, extra_summary_dict]
    
     class OHLVCBuckarooWidget(BuckarooWidget):
         post_processing_function=volume_post
    OHLVCBuckarooWidget(get_ohlcv("IBM"))


Now when you instantiate `OHLVCBuckarooWidget` there will be a UI toggable function of `volume_post` so you can turn on and turn off this feature interactively.  `OHLVCBuckarooWidget` has your own opinions baked in, that the user can turn on or off.

What if we want to switch between red/green colors map and a color map based on size of diff to previous day?  In this case we want to add two "style_methods" which are togglable in the UI.  style_method takes a summary_dict and returns the column config.


.. code-block:: python

    def volume_post(df):
        if 'Volume' not in df.columns:
	    return [df, {}]
	df['Volume_colors'] = 'red'  # replace with actual red/green based on diff
	df['Volume_diff'] = df['Volume'].diff()
	extra_summary_dict = {
            'Volume_colors' : { 'column_config_override': { 'displayer': 'hidden'}},
            'Volume_diff' : { 'column_config_override': { 'displayer': 'hidden'}}}
	return [df, extra_summary_dict]

     def volume_style_red_green(col_name, col_summary_dict, default_config):
         if col_name == 'Volume':
	     return {'override': {
	            'color_map_config' : {'color_rule': 'color_from_column', 'col_name': 'Volume_colors'}}}
	 return {}

     def volume_style_color_map(col_name, col_summary_dict, default_config):
         if col_name == 'Volume':
	     return {'override': {
	            'color_map_config' : {'color_rule': 'color_map', 'map_name': 'BLUE_TO_YELLOW',
		                          'val_column': 'Volume_diff'}}}
	 return {}
	 
     class OHLVCBuckarooWidget(BuckarooWidget):
         post_processing_function=volume_post
	 style_methods=[volume_style_red_green, volume_style_color_map]
    OHLVCBuckarooWidget(get_ohlcv("IBM"))


With this implementation, the frontend can cycle through three style_methods `volume_style_red_green`, `volume_style_color_map` and `default`



   



