from traitlets import Unicode, Any, observe
from ipywidgets import DOMWidget


def get_cleaning_operations():
    pass

def get_cleaning_sd():
    pass

def merge_ops():
    pass

def run_df_interpreter():
    pass

def run_code_generator():
    pass

def make_getter():
    pass

def merge_sds():
    pass

def merge_column_config():
    pass


class DataFlow(DOMWidget):


    sample_method = Unicode('default')
    operating_df = Any('')

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

    @observe('raw_df', 'sample_method')
    def _operating_df(self, change):
        self.operating_df = self.compute_operating_df(self.raw_df, self.sample_method)

    @observe('cleaning_method', 'existing_operations')
    def _operation_result(self, change):
        cleaning_operations = get_cleaning_operations(self.operating_df, self.cleaning_method)
        cleaning_sd = get_cleaning_sd(self.operating_df, self.cleaning_method)
        merged_operations = merge_ops(self.existing_operations, cleaning_operations)
        cleaned_df = run_df_interpreter(self.operating_df, self.merged_operations)
        generated_code = run_code_generator(self.merged_operations)
        self.operation_result = [cleaned_df, cleaning_sd, generated_code, merged_operations]

    @observe('operation_result', 'post_processing_method')
    def _processed_result(self, change):
        #for now this is a no-op because I don't have a post_processing_function or mechanism
        self.processed_result = [self.operation_result[0], {}]

    @observe('processed_result', 'analysis_klasses')
    def _summary_sd(self, change):
        #processed_df = self.processed_result[0]
        #analysis_klasses
        #call dfstats stuff here
        self.summary_sd = {}

    @observe('summary_sd')
    def _merged_sd(self, change):
        #slightly inconsitent that processed_sd gets priority over
        #summary_sd, given that processed_df is computed first. My
        #thinking was that processed_sd has greater total knowledge
        #and should supersede summary_sd.
        cleaned_sd = self.operation_result[1]
        processed_sd = self.processed_result[1]
        self.merged_sd = merge_sds(cleaned_sd, self.summary_sd, processed_sd)

    def get_column_config(self, sd, style_method):
        base_column_config = style_method(sd)
        return merge_column_config(base_column_config, self.column_config_override)

    @observe('merged_sd', 'style_method')
    def _widget_config(self, change):
        # generated_code = operation_result[2]
        # processed_df = processed_result[0]
        column_config = self.get_column_config(self.merged_sd, self.style_method)
        return [column_config]
