from traitlets import Unicode, Any, observe
from ipywidgets import DOMWidget


    

def get_cleaning_sd(df, cleaning_method):
    return {}

SENTINEL_DF_1 = 9
SENTINEL_DF_2 = 80
SENTINEL_DF_3 = 90
SENTINEL_DF_4 = 90


def merge_ops(existing_ops, cleaning_ops):
    """ strip cleaning_ops from existing_ops, reinsert cleaning_ops at the beginning """
    a = existing_ops.copy()
    a.extend(cleaning_ops)
    return a

def get_cleaning_operations(df, cleaning_method):
    if cleaning_method == "one op":
        return [""]
    if cleaning_method == "two op":
        return ["", ""]
    return []

def run_df_interpreter(df, ops):
    if len(ops) == 1:
        return SENTINEL_DF_1
    if len(ops) == 2:
        return SENTINEL_DF_2
    return df

def run_code_generator(ops):
    if len(ops) == 1:
        return "codegen 1"
    if len(ops) == 2:
        return "codegen 2"
    return ""


def merge_column(base, new):
    ret = base.copy()
    ret.update(new)

    base_override = base.get('column_config_override', {}).copy()
    new_override = new.get('column_config_override', {}).copy()
    base_override.update(new_override)

    if len(base_override) > 0:
        ret['column_config_override'] = base_override
    return ret

        

def merge_sds(*sds):
    """merge sds with later args taking precedence

    sub-merging of "overide_config"??
    """
    base_sd = {}
    for sd in sds:
        for column in sd.keys():
            base_sd[column] = merge_column(base_sd.get(column, {}), sd[column])
    return base_sd

SENTINEL_COLUMN_CONFIG_1 = "ASDF"
SENTINEL_COLUMN_CONFIG_2 = "FOO-BAR"


def get_summary_sd(df, analysis_klasses):
    if analysis_klasses == "foo":
        return {'foo':8}
    if analysis_klasses == "bar":
        return {'bar':10}
    return {}


def style_columns(style_method:str, sd):
    if style_method == "foo":
        return sentinel_column_config_2
    else:
        return SENTINEL_COLUMN_CONFIG_1

def merge_column_config(*column_configs):
    pass

def compute_sampled_df(raw_df, sample_method):
    if sample_method == "first":
        return raw_df[:1]
    return raw_df

class DataFlow(DOMWidget):

    def __init__(self, raw_df):
        self.summary_sd = {}
        self.existing_operations = []
        self.raw_df = raw_df

    
    raw_df = Any('')
    sample_method = Unicode('default')
    sampled_df = Any('')

    cleaning_method = Unicode('')
    cleaning_operations = Any()

    existing_operations = Any([])
    merged_operations = Any()


    cleaned = Any(default=None)
    # cleaned_df = Any()
    # cleaned_sd = Any()
    
    lowcode_operations = Any()

    processed_result = Any(default=None)

    analysis_klasses = None
    summary_sd = Any()

    merged_sd = Any()

    style_method = Unicode('')
    column_config = Any()

    column_config_overrides = {}

    merged_column_config = Any()

    widget_args_tuple = Any()


    @observe('raw_df', 'sample_method')
    def _sampled_df(self, change):
        self.sampled_df = compute_sampled_df(self.raw_df, self.sample_method)

    @observe('sampled_df', 'cleaning_method', 'existing_operations')
    def _operation_result(self, change):
        if self.sampled_df is None:
            return
        cleaning_operations = get_cleaning_operations(self.sampled_df, self.cleaning_method)
        cleaning_sd = get_cleaning_sd(self.sampled_df, self.cleaning_method)
        print("existing_operations", self.existing_operations, change)
        merged_operations = merge_ops(self.existing_operations, cleaning_operations)
        print("merged_operations", merged_operations)
        cleaned_df = run_df_interpreter(self.sampled_df, merged_operations)
        print("_cleaned_df", self.merged_operations)
        generated_code = run_code_generator(merged_operations)
        self.cleaned = [cleaned_df, cleaning_sd, generated_code, merged_operations]

    @property
    def cleaned_df(self):
        if self.cleaned is not None:
            return self.cleaned[0]

    @property
    def cleaned_sd(self):
        if self.cleaned is not None:
            return self.cleaned[1]
        return {}

    @property
    def generated_code(self):
        if self.cleaned is not None:
            return self.cleaned[2]

    @property
    def merged_operations(self):
        if self.cleaned is not None:
            return self.cleaned[3]

    @observe('cleaned', 'post_processing_method')
    def _processed_result(self, change):
        #for now this is a no-op because I don't have a post_processing_function or mechanism
        self.processed_result = [self.cleaned_df, {}]

    @property
    def processed_df(self):
        if self.processed_result is not None:
            return self.processed_result[0]
        return None

    @property
    def processed_sd(self):
        if self.processed_result is not None:
            return self.processed_result[1]
        return {}


    @observe('processed_result', 'analysis_klasses')
    def _summary_sd(self, change):
        #call dfstats stuff here
        self.summary_sd = get_summary_sd(
            self.processed_df, self.analysis_klasses)

    @observe('summary_sd')
    def _merged_sd(self, change):
        #slightly inconsitent that processed_sd gets priority over
        #summary_sd, given that processed_df is computed first. My
        #thinking was that processed_sd has greater total knowledge
        #and should supersede summary_sd.
        self.merged_sd = merge_sds(self.cleaned_sd, self.summary_sd, self.processed_sd)

    def get_column_config(self, sd, style_method):
        base_column_config = style_columns(style_method, sd)
        return merge_column_config(base_column_config, self.column_config_overrides)

    @observe('merged_sd', 'style_method')
    def _widget_config(self, change):
        # generated_code = operation_result[2]
        # processed_df = processed_result[0]
        column_config = self.get_column_config(self.merged_sd, self.style_method)
        return [self.processed_df, self.merged_sd, column_config]
