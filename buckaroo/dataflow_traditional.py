import json
import pandas as pd
from traitlets import Unicode, Any, observe, HasTraits, Dict, List
from ipywidgets import DOMWidget
from .serialization_utils import df_to_obj, EMPTY_DF_WHOLE, pd_to_obj    
from buckaroo.pluggable_analysis_framework.pluggable_analysis_framework import (ColAnalysis)
from buckaroo.pluggable_analysis_framework.analysis_management import DfStats


SENTINEL_DF_1 = pd.DataFrame({'foo'  :[10, 20], 'bar' : ["asdf", "iii"]})
SENTINEL_DF_2 = pd.DataFrame({'col1' :[55, 55], 'col2': ["pppp", "333"]})
SENTINEL_DF_3 = pd.DataFrame({'pp'   :[99, 33], 'ee':   [     6,     9]})
SENTINEL_DF_4 = pd.DataFrame({'vvv'  :[12, 49], 'oo':   [ 'ccc', 'www']})


def merge_ops(existing_ops, cleaning_ops):
    """ strip cleaning_ops from existing_ops, reinsert cleaning_ops at the beginning """
    a = existing_ops.copy()
    a.extend(cleaning_ops)
    return a

def merge_column(base, new):
    """
    merge individual column dictionaries, with special handling for column_config_override
    """
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




def style_columns(style_method:str, sd):
    if style_method == "foo":
        return sentinel_column_config_2
    else:
        ret_col_config = []
        for col in sd.keys():
            ret_col_config.append(
                {'col_name':col, 'displayer_args': {'displayer': 'obj'}})
        return {
            'pinned_rows': [
            #    {'primary_key_val': 'dtype', 'displayer_args': {'displayer': 'obj'}}
            ],
            'column_config': ret_col_config}

def merge_column_config(styled_column_config, overide_column_configs):
    ret_column_config = styled_column_config.copy()
    for row in ret_column_config:
        col = row['col_name']
        if col in overide_column_configs:
            row.update(overide_column_configs[col])
    return ret_column_config

def compute_sampled_df(raw_df, sample_method):
    if sample_method == "first":
        return raw_df[:1]
    return raw_df

class DataFlow(HasTraits):
    """This class is meant to only represent the dataflow through
    buckaroo with no accomodation for widget particulars

    It generally has stub methods for implementations that enable basic testing of the 'data flow' .
    It is meant to be extended by Customizable DataFlow that can specify multiple different options

    CustomizableDataflow is meant to be extended by BuckarooWidget whcih connects frontend values to the following properties

    sample_method
    cleaning_method
    existing_operations
    style_method ... became df_display_args

    all of this results in values for df_dict being updated
    
    """
    def __init__(self, raw_df):
        super().__init__()
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
    
    lowcode_operations = Any()

    processed_result = Any(default=None)

    analysis_klasses = None
    summary_sd = Any()

    merged_sd = Any()

    style_method = Unicode('simple')
    column_config = Any()

    column_config_overrides = {}

    merged_column_config = Any()

    widget_args_tuple = Any()

    


    @observe('raw_df', 'sample_method')
    def _sampled_df(self, change):
        self.sampled_df = compute_sampled_df(self.raw_df, self.sample_method)

    def _run_df_interpreter(self, df, ops):
        if len(ops) == 1:
            return SENTINEL_DF_1
        if len(ops) == 2:
            return SENTINEL_DF_2
        return df

    def _run_code_generator(self, ops):
        if len(ops) == 1:
            return "codegen 1"
        if len(ops) == 2:
            return "codegen 2"
        return ""

    def _run_cleaning(self, df, cleaning_method):
        cleaning_ops = []
        if cleaning_method == "one op":
            cleaning_ops =  [""]
        if cleaning_method == "two op":
            cleaning_ops = ["", ""]
        cleaning_sd = {}
        return cleaning_ops, cleaning_sd

    @observe('sampled_df', 'cleaning_method', 'existing_operations')
    def _operation_result(self, change):
        if self.sampled_df is None:
            return
        cleaning_operations, cleaning_sd = self._run_cleaning(self.sampled_df, self.cleaning_method)
        merged_operations = merge_ops(self.existing_operations, cleaning_operations)
        cleaned_df = self._run_df_interpreter(self.sampled_df, merged_operations)
        generated_code = self._run_code_generator(merged_operations)
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

    def _get_summary_sd(self, df):
        analysis_klasses = self.analysis_klasses
        if analysis_klasses == "foo":
            return {'some-col': {'foo':8}}
        if analysis_klasses == "bar":
            return {'other-col': {'bar':10}}
        index_name = df.index.name or "index"
        ret_summary = {index_name: {}}
        for col in df.columns:
            ret_summary[col] = {}
        return ret_summary

    @observe('processed_result', 'analysis_klasses')
    def _summary_sd(self, change):
        self.summary_sd = self._get_summary_sd(self.processed_df)

    @observe('summary_sd')
    def _merged_sd(self, change):
        #slightly inconsitent that processed_sd gets priority over
        #summary_sd, given that processed_df is computed first. My
        #thinking was that processed_sd has greater total knowledge
        #and should supersede summary_sd.
        self.merged_sd = merge_sds(self.cleaned_sd, self.summary_sd, self.processed_sd)

    def _get_dfviewer_config(self, sd, style_method):
        dfviewer_config = style_columns(style_method, sd)
        base_column_config = dfviewer_config['column_config']
        dfviewer_config['column_config'] =  merge_column_config(
            base_column_config, self.column_config_overrides)
        return dfviewer_config

    @observe('merged_sd', 'style_method')
    def _widget_config(self, change):
        #how to control ordering of column_config???
        dfviewer_config = self._get_dfviewer_config(self.merged_sd, self.style_method)
        self.widget_args_tuple = [self.processed_df, self.merged_sd, dfviewer_config]

class SimpleStylingAnalysis(ColAnalysis):
    pinned_rows = [
        { 'primary_key_val': 'dtype', 'displayer_args': { 'displayer': 'obj' } },
      { 'primary_key_val': 'histogram', 'displayer_args': { 'displayer': 'histogram' }, }
    ]

    @staticmethod
    def sd_to_column_config(col, sd):
        return {'col_name':col, 'displayer_args': {'displayer': 'obj'}}
    
    @classmethod
    def style_columns(kls, sd):
        ret_col_config = []
        for col in sd.keys():
            ret_col_config.append(kls.sd_to_column_config(col, sd[col]))
        return {
            'pinned_rows': kls.pinned_rows,
            'column_config': ret_col_config}

    style_method = "simple"
    #the analysis code always runs
    analysis_stuff = None #functions that add dtype and na_per to sumary_sd

class UnknownStyleMethod(Exception):

    def __init__(self, style_method, available_methods, analysis_klasses):
        self.style_method = style_method
        self.available_methods = available_methods
        self.msg =\
            "style_method of '{self.style_method}' not found in '{available_methods}', all analysis_klasses is []'"

def filter_analysis(klasses, attr):
    ret_klses = {}
    for k in klasses:
        attr_val = getattr(k, attr, None)
        if attr_val is not None:
            ret_klses[attr_val] = k
    return ret_klses
            
from .customizations.all_transforms import configure_buckaroo, DefaultCommandKlsList
class CustomizableDataflow(DataFlow):
    """
    This allows targetd extension and customization of DataFlow
    """
    analysis_klasses = [SimpleStylingAnalysis]
    command_klasses = DefaultCommandKlsList
    commandConfig = Dict({}).tag(sync=True)
    DFStatsClass = DfStats

    def __init__(self, *args, **kwargs):
        self.styling_options = filter_analysis(self.analysis_klasses, "style_method")
        self.df_name = "placeholder"
        self.debug = True
        self._setup_from_command_kls_list()
        self.populate_df_meta()
        super().__init__(*args, **kwargs)


    def populate_df_meta(self):
            # df_meta = Dict({
            #     'columns': 5,
            #     'rows_shown': 20,
            #     'total_rows': 877}).tag(sync=True)
            pass


    ### start code interpreter block
    def _setup_from_command_kls_list(self):
        #used to initially setup the interpreter, and when a command
        #is added interactively
        c_klasses = self.command_klasses
        c_defaults, c_patterns, df_interpreter, gencode_interpreter = configure_buckaroo(c_klasses)
        self.df_interpreter, self.gencode_interpreter = df_interpreter, gencode_interpreter
        self.commandConfig = dict(argspecs=c_patterns, defaultArgs=c_defaults)

    def add_command(self, incomingCommandKls):
        without_incoming = [x for x in self.command_classes if not x.__name__ == incomingCommandKls.__name__]
        without_incoming.append(incomingCommandKls)
        self.command_klasses = without_incoming
        self.setup_from_command_kls_list()

    def _run_df_interpreter(self, df, operations):
        full_ops = [{'symbol': 'begin'}]
        full_ops.extend(operations)
        if len(full_ops) == 1:
            return df
        return self.buckaroo_transform(new_operations , df)

    def run_code_generator(self, operations):
        if len(operations) == 0:
            return 'no operations'
        return self.gencode_interpreter(operations)
    ### end code interpeter block


    ### start summary stats block
    def _get_summary_sd(self, processed_df):
        stats = self.DFStatsClass(
            processed_df,
            self.analysis_klasses,
            self.df_name, debug=self.debug)
        return stats.sdf

    def add_analysis(self, analysis_klass):
        """
        same as get_summary_sd, call whatever to set summary_sd and trigger further comps
        """
        stats = self.DFStatsClass(
            self.processed_df,
            self.analysis_klasses,
            self.df_name, debug=self.debug)
        stats.add_analysis(analysis_klass)
        return stats.sdf
    # ### end summary stats block        

    ### style_method config
    def _get_dfviewer_config(self, sd, style_method):
        if style_method not in self.styling_options:
            raise UnknownStyleMethod(style_method, self.styling_options.keys(), self.analysis_klasses)
        
        styling_analysis = self.styling_options[style_method]
        dfviewer_config = styling_analysis.style_columns(sd)
        base_column_config = dfviewer_config['column_config']
        dfviewer_config['column_config'] =  merge_column_config(
            base_column_config, self.column_config_overrides)
        return dfviewer_config

    @property
    def stats_df_viewer_config(self):
        return {
        'pinned_rows': [
      { 'primary_key_val': 'dtype', 'displayer_args': { 'displayer': 'obj' } },
      { 'primary_key_val': 'histogram', 'displayer_args': { 'displayer': 'histogram' }, },

        ],
        'column_config': [
            {'col_name':'index', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'a', 'displayer_args': {'displayer': 'obj'}},
            {'col_name':'b', 'displayer_args': {'displayer': 'obj'}}]}
    

    df_display_args = Any().tag(sync=True)
    df_data_dict = Any().tag(sync=True)

    @observe('widget_args_tuple')
    def _handle_widget_change(self, change):
        """
        put together df_dict for consumption by the frontend
        """
        processed_df, merged_sd, df_viewer_config = self.widget_args_tuple
        if processed_df is None:
            return 
        self.df_display_args = {
            'main': {'data_key': 'main', 'df_viewer_config': json.loads(json.dumps(df_viewer_config)),
                     'summary_stats_key': 'all_stats'},
            # 'summary': {'data_key':'empty', 'df_viewer_config': self.stats_df_viewer_config,
            #             'summary_stats_key': 'all_stats'},

            'summary': {'data_key':'empty', 'df_viewer_config': self.stats_df_viewer_config,
                            'summary_stats_key': 'all_stats'},


            #iterate over all analysis_klasses that provide styling, rename
        }

        temp_sd = merged_sd.copy()
        del temp_sd['index']
        self.df_data_dict = {'main': pd_to_obj(processed_df),
                             'all_stats': pd_to_obj(pd.DataFrame(temp_sd)),
                             'empty': []}

