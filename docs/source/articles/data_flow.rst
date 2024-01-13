.. _using:

Data Flow through Buckaroo
==========================

Data flow through Buckaroo is complex and nuanced.

Basic Flow
----------

#. ``raw_df``
#. ``operating_df``               = `raw_df`, sample-method_
#. ``cleaning_operations``        = `operating_df`, cleaning-method_
#. ``cleaned_df``, ``cleaned_sd`` = `operating_df`, `cleaning_operations`
#. ``summary_sd``                 = `cleaned_df` ``analysis_klasses``
#. ``merged_sd``                  = `cleaned_sd`, `summary_sd`
#. ``column_config``              = `merged_sd` style-method_
#. ``final_column_config``        = `column_config`, ``column_config_override``
#. ``widget``                     = `cleaned_df`, `merged_sd`, `final_column_config`


MVP Release
-----------

#. ``raw_df``
#. ``operating_df``               = `raw_df`, sample-method_
#. ``cleaned_df``                 = `operating_df`
#. ``summary_sd``                 = `cleaned_df` ``analysis_klasses``
#. ``merged_sd``                  = `{}`, `summary_sd`
#. ``column_config``              = `merged_sd` style-method_
#. ``final_column_config``        = `column_config`, ``column_config_override``
#. ``widget``                     = `cleaned_df`, `merged_sd`, `final_column_config`













   
Full Flow
---------
``instantiation_`` are defined at class instantiation time, or through python
`dependent_`       are the result of a previous step
user-specified_    are specified in the UI, and can be changed interactively

#. ``operating_df``         <> ``raw_df``, sample-method_
#. ``cleaning_operations``  = `operating_df`, cleaning-method_
#. ``merged_operations``    = `cleaning_operations`, existing-operations_
#. ``operation_result``     = `operating_df`, `merged_operations`
#. ``transformed_df``       = `operation_result`
#. ``cleaned_sd``           = `operation_result`
#. ``generated_code``       = `operation_result`
#. ``processed_result``     = `transformed_df`, post-processing-method_
#. ``processed_df``         = `processed_result`
#  ``processed_sd``         = `processed_result`
#. ``summary_sd``           = `processed_df` ``analysis_klasses``
#. ``merged_sd``            = `cleaned_sd`, `summary_sd`, `processed_sd`
#. ``column_config``        = `merged_sd` style-method_
#. ``merged_column_config`` = `column_config`, ``column_config_override``
#. ``widget``               = `processed_df`, `merged_sd`, `merged_column_config`, `generated_code`
   

existing_operations is an interint one.  It can be either user entered low_code ops, or the previous cleaning_operations.  merged_operations is responsible for first stripping all cleaning_operations from "existing_operations", then adding in the new "cleaning_operations".  This preserves any user netered operations


----
Rewritten so result tuples are referenced, not individual variables

#. ``operating_df``         <> ``raw_df``, sample-method_
#. ``cleaning_operations``  = `operating_df`, cleaning-method_
#. ``merged_operations``    = `cleaning_operations`, existing-operations_
#. ``operation_result``     = `operating_df`, `merged_operations`
   ( ``transformed_df``  ``cleaned_sd``  ``generated_code`` )
#. ``processed_result``     = `operation_result`df, post-processing-method_
   ( ``processed_df``   ``processed_sd`` )
#. ``summary_sd``           = `processed_result`df, ``analysis_klasses``
#. ``merged_sd``            = `cleaned_sd`, `summary_sd`, `processed_result`sd
#. ``column_config``        = `merged_sd` style-method_
#. ``merged_column_config`` = `column_config`, ``column_config_override``
#. ``widget``               = `processed_result`df, `merged_sd`, `merged_column_config`, operation_result`generated_code`


----
Rewritten so with getters for the result tuples.


#. ``operating_df``         <> ``raw_df``, sample-method_
#. ``cleaning_operations``  = `operating_df`, cleaning-method_
#. ``merged_operations``    = `cleaning_operations`, existing-operations_
#. ``operation_result``     = `operating_df`, `merged_operations`
.   make_getter (`operation_result`, None, ``cleaned_sd``  ``generated_code`` )
#. ``processed_result``     = `operation_result.df`, post-processing-method_
.   make_getter  (`processed_result`, ``processed_df``,  ``processed_sd`` )
#. ``summary_sd``           = `processed_result.df`, ``analysis_klasses``
#. ``merged_sd``            = 'cleaned_sd', `summary_sd`, 'processed_sd'
#. ``column_config``        = `merged_sd` style-method_
#. ``merged_column_config`` = `column_config`, ``column_config_override``
#. ``widget``               = 'processed_df', `merged_sd`, `merged_column_config`, 'generated_code'

getters are specced in args surrounded in quotes

The getters are important because they get a previously created value... but they don't set up a listener.
without getters, unneeded recomps are triggered


----
Rewritten so each step only depends on a single generated property (but possibly two user props)


#. ``operating_df``         = ``raw_df``, sample-method_
#. ``operation_result``     = `operating_df`, cleaning-method_, existing-operations_ 
.   make_getter (`operation_result`, None, ``cleaned_sd``  ``generated_code`` )
#. ``processed_result``     = `operation_result.df`, post-processing-method_
.   make_getter  (`processed_result`, ``processed_df``,  ``processed_sd`` )
#. ``summary_sd``           = `processed_result.df`, ``analysis_klasses``
#. ``merged_sd``            = 'cleaned_sd', `summary_sd`, 'processed_sd'
#. ``widget``               = 'processed_df', `merged_sd`, style-method_, 'generated_code'

getters are specced in args surrounded in quotes

The getters are important because they get a previously created value... but they don't set up a listener.
without getters, unneeded recomps are triggered




----

Buckaroo is extensible.  The architecture of Buckaroo is crafted to allow specific points of composable extensibility in an opinionated manner.  It was designe dthis way based on experience from writing many adhoc anlsysis pipelines.  Previous "simpler" attempts at extensibility ran into bugs that couldn't be cleanly accomodated.

Quick Start to extending buckaroo

In this exercise we are going add a custom coloring method to Buckaroo.  We will take an OHLCV dataframecolor and Volume based on the change from the previous day.

First we need to craft the column config that will enable this conditonal coloring.

We want to use `ColorFromColumn`, we want the config for the volume column to look like
.. code-block:: python

    volume_config_override = {
        'color_map_config' : {'color_rule': 'color_from_column', 'col_name': 'Volume_colors'}}


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
	            'color_map_config' : {'color_rule': 'color_from_column', 'col_name': 'Volume_colors'}}},
            'Volume_colors' : {
	        'column_config_override': { 'displayer': 'hidden'}}}
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


   

Rewritten so each step only depends on a single generated property (but possibly two user props)


#. ``sampled_df``         = ``raw_df``, sample-method_
#. ``operation_result``     = `sampled_df`, cleaning-method_, existing-operations_ 
.   make_getter (`operation_result`, None, ``cleaned_sd``  ``generated_code`` )
#. ``processed_result``     = `operation_result.df`, post-processing-method_
.   make_getter  (`processed_result`, ``processed_df``,  ``processed_sd`` )
#. ``summary_sd``           = `processed_result.df`, ``analysis_klasses``
#. ``merged_sd``            = 'cleaned_sd', `summary_sd`, 'processed_sd'
#. ``widget``               = 'processed_df', `merged_sd`, style-method_, 'generated_code'

getters are specced in args surrounded in quotes

The getters are important because they get a previously created value... but they don't set up a listener.
without getters, unneeded recomps are triggered



