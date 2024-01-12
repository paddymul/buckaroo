

class DataFlow(DOMWidget):


    sample_method = Unicode('default')
    operating_df = Any(module_version)

    cleaning_method = Unicode('')
    cleaning_operations = Any()

    existing_operations = Any()
    merged_operations = Any()

    cleaned_df = Any()
    cleaned_sd = Any()
    
    lowcode_operations = Any()

    transformed_df = Any()

    summary_sd = Any()

    merged_sd = Any()

    style_method = Unicode('')
    column_config = Any()

    merged_column_config = Any()

    widget_args_tuple = Any()


    
    @data_observe('raw_df', 'sample_method')
    def _operating_df(self, raw_df, sample_method):
        return raw_df

    @data_observe('operating_df', 'cleaning_method')
    def _cleaning_operations(self, operating_df, cleaning_method):
        return operating_df

    @data_observe('cleaning_operations',' existing-operations')
    def _merged_operations(self, cleaning_operations, existing_operations):
        return cleaning_operations
    
    @data_observe('operating_df', 'merged_operations')
    def _operation_result(self, operating_df, merged_operations):
        return [operating_df, {}, ""]

    __cleaned_sd = make_getter(operation_result, 1)
    __generated_code = make_getter(operation_result, 2)

    @data_observe('operation_result[0]', 'post_processing_method')
    def _processed_result(self, transformed_df, post_processing_method):
        return [transformed_df, {}]

    __processed_df = make_getter(processed_result, 0)
    __processed_sd = make_getter(processed_result, 1)
    
    @data_observe('processed_result[0]', 'analysis_klasses')
    def _summary_sd(self, processed_df, analysis_klasses):
        return {}

    @data_observe(__cleaned_sd, 'summary_sd', __processed_sd)
    def _merged_sd(self, cleaned_sd, summary_sd, processed_sd):
        return {}

    @data_observe('merged_sd', 'style_method')
    def _column_config(self, merged_sd, style_method):
        return []

    @data_observe('column_config', 'column_config_override')
    def _merged_column_config(self, column_config, column_config_override):
        return []

    @data_observe(__processed_df, 'merged_sd', 'merged_column_config', __generated_code)
    def _widget_config(self, column_config, column_config_override):
        return []
    
def data_observer( *watch_traits):
    """wire up observers such that if any of watch traits change, call
    the listener and set the destination Provide protections such that
    intial state loops are prevented

    destination_result is determined from the decorated function_name
    so def _generated_code(self, operation_result)
    will set the property of "generated_code" note the leading
    underscore, this is necessary so the function name doesn't colide
    with the property name

    __getters are used when a function returns multiple values, and
    only one of the values shoudl trigger further listeners


    each function should only depend on a single data_flow observable.  other dataflow results can be accessed via properties
    
    
    """
    pass


"""
Data observe is responsible for the following



"""

    
    
