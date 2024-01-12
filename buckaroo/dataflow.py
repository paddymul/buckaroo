

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

    @data_observe('operating_df', 'cleaning_method', 'existing_operations')
    def _operation_result(self, operating_df, cleaning_method, existing_operations)
        cleaning_operations = get_cleaning_operations(operating_df, cleaning_method)
        cleaning_sd = get_cleaning_sd(operating_df, cleaning_method)
        merged_operations = merge_ops(existing_operations, cleaning_operations)
        cleaned_df = run_df_interpreter(operating_df, merged_operations)
        generated_code = run_code_generator(merged_operations)
        #there is a cycle with exisitng operations and merged_operations
        return [cleaned_df, cleaning_sd, generated_code, merged_operations]

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

    @data_observe('summary_sd', __cleaned_sd,  __processed_sd)
    def _merged_sd(self, cleaned_sd, summary_sd, processed_sd):
        return merge_sds(cleaned_sd, summary_sd, processed_sd)

    def get_column_config(self, sd, style_method):
        base_column_config = style_method(sd)
        return merge_column_config(base_column_config, self.column_config_override)

    @data_observe('merged_sd', __processed_df, __generated_code,  'style_method')
    def _widget_config(self, processed_df, merged_sd, style_method, generated_code):
        column_config = self.get_column_config(merged_sd, style_method)
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
    
    def constructed_decorator(wrapped_func):
        target_name = wrapped_func.__name__[1:] #strip the leading underscore off the function name

        trigger_watch_trait = watch_traits[0]
        
        if "[0]" in trigger_watch_trait:
            target_name = target_name.replace("[0]", "")
            
        def decorated_function(self, *args):

            change['new']
            pass
        return decorated_function
    return constructed_decorator

