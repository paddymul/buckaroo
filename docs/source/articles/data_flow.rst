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
