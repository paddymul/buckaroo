#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Paddy Mullen.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""
import warnings
import traceback

from ipywidgets import DOMWidget
from traitlets import Unicode, List, Dict, observe

from ._frontend import module_name, module_version
from .customizations.all_transforms import configure_buckaroo, DefaultCommandKlsList
from .jlisp.lisp_utils import (lists_match, split_operations)

from .auto_clean.auto_clean import get_auto_type_operations, get_typing_metadata, recommend_type
from .customizations.down_sample import sample

from .customizations.analysis import (TypingStats, ComputedDefaultSummaryStats, DefaultSummaryStats, ColDisplayHints)
from .customizations.histogram import (Histogram)
from .pluggable_analysis_framework.analysis_management import DfStats
from .pluggable_analysis_framework.utils  import get_df_name

from .serialization_utils import df_to_obj, EMPTY_DF_WHOLE


"""

I have dfstats to manage the production of actual summary stats

I now need to manage the styles (column config)

I also want to manage the multipel summary stats presentations

summary stats presentations are just different pinned row configs that read from the same summary stats dictionary


"""


FAST_SUMMARY_WHEN_GREATER = 1_000_000
class BuckarooWidget(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('DCEFWidgetModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('DCEFWidgetView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    commandConfig = Dict({}).tag(sync=True)
    operations = List().tag(sync=True)

    #df_dict: Dict[str, DFWhole] = Dict({}).tag(sync=True)
    df_dict = Dict({}).tag(sync=True)


    operation_results = Dict(
        {'transformed_df': EMPTY_DF_WHOLE, 'generated_py_code':'# instantiation, unused'}
    ).tag(sync=True)


    df_meta = Dict({
        'columns': 5,
        'rows_shown': 20,
        'total_rows': 877}).tag(sync=True)


    buckaroo_options = Dict({
        'auto_clean': ['aggressive', 'conservative'],
        'reorderd_columns': [],
        'sampled': ['random'],
        'show_commands': ['on'],
        #//    'summary_stats' : ['full', 'all', 'typing_stats']
        'summary_stats': ['all'],
    }).tag(sync=True)
        

    
    # dfConfig = Dict(
    #     {
    #     'totalRows': 1234569,
    #     'columns': 30,
    #     'rowsShown': 0,
    #     'sampleSize': 10_000,
    #     'sampled':False,
    #     'summaryStats': False,
    #     'reorderdColumns': False,
    #     'showCommands': True,
    #     'auto_clean': False,
    # }).tag(sync=True)


    #widget config.  Change these via inheritance to alter core behaviors of buckaroo
    command_classes = DefaultCommandKlsList
    analysis_classes = [TypingStats, DefaultSummaryStats,
                        Histogram,
                        ComputedDefaultSummaryStats,
                        ColDisplayHints]
    DFStatsClass = DfStats
    typing_metadata_f = staticmethod(get_typing_metadata)
    typing_recommend_f = staticmethod(recommend_type)



    #used by auto_cleaning
    machine_gen_operations = List().tag(sync=True)

    def should_sample(self, df, sampled):
        item_count = len(df) * len(df.columns)
        if (item_count > FAST_SUMMARY_WHEN_GREATER) or sampled:
            return True
        return False
    
    def __init__(self, df,
                 debug=False
                 ):

        super().__init__()
        if not debug:
            warnings.filterwarnings('ignore')
        #moving setup_from_command_kls_list early in the init because
        #it's relatively benign and not tied to other linked updates
        self.processed_result = None
        self.transformed_df = None
        self.debug = debug
        self.df_name = get_df_name(df)

        # self.setup_from_command_kls_list()
        # self.dfConfig = self.get_df_config(df, sampled, showCommands)
        # #we need dfConfig setup first before we get the proper working_df for auto_cleaning
        # self.raw_df = df
        # self.run_autoclean(auto_clean)
        self.df_dict = {'main':
                        df_to_obj(df, {})}
        
        warnings.filterwarnings('default')


    def run_autoclean(self, auto_clean):
        if auto_clean:
            # this will trigger the setting of self.typed_df
            self.operations = get_auto_type_operations(
                self.raw_df, metadata_f=self.typing_metadata_f,
                recommend_f=self.typing_recommend_f)
        else:
            self.set_typed_df(self.get_working_df())
            #need to run this for the no autoclean case
            #self.run_post_processing()
        
    def set_metadata_f(self, new_f):
        self.typing_metadata_f = staticmethod(new_f)
        self.run_autoclean()

    def set_recommend_f(self, new_f):
        self.typing_recommend_f = staticmethod(new_f)
        self.run_autoclean()

    def set_typed_df(self, new_df):
        self.typed_df = new_df
        # stats need to be rerun each time 
        self.stats = self.DFStatsClass(
            self.typed_df,
            self.analysis_classes,
            self.df_name, debug=self.debug)
        # setting summary_df is removed here because summary_df_json is handled by df_dict
        # summary_df can be accessed through self.stats.presentation_sdf
        self.ensure_df_sync()

    def ensure_df_sync(self):
        self.df_dict = df_to_obj(self.typed_df, self.stats.sdf)


    @observe('operations')
    def handle_operations(self, change):
        if lists_match(change['old'], change['new']):
            return
        new_ops = change['new']
        split_ops = split_operations(new_ops)
        self.machine_gen_operations = split_ops[0]
        
        user_gen_ops = split_ops[1]

        #if either the user_gen part or the machine_gen part changes,
        #we still have to recompute the generated code and
        #resulting_df because the input df will be different

        results = {}
        try:
            self.transformed_df = self.interpret_ops(user_gen_ops, self.typed_df)
            #note we call gneerate_py_code based on the full
            #self.operations, this makes sure that machine_gen
            #cleaning code shows up too
            results['generated_py_code'] = self.generate_code(new_ops)
            results['transformed_df'] = df_to_obj(self.transformed_df, {})
            results['transform_error'] = False
            #self.run_post_processing()            
        except Exception as e:
            results['transformed_df'] = EMPTY_DF_WHOLE
            traceback.print_exc()
            results['transform_error'] = str(e)
        self.operation_results = results

    @observe('machine_gen_operations')
    def interpret_machine_gen_ops(self, change, force=False):
        if (not force) and lists_match(change['old'], change['new']):
            return # nothing changed, do no computations
        new_ops = change['new']
        self.set_typed_df(self.interpret_ops(new_ops, self.get_working_df()))

    def get_working_df(self):
        #this won't listen to sampled changes properly
        if self.dfConfig['sampled']:
            return sample(self.raw_df, self.dfConfig['sampleSize'])
        else:
            return self.raw_df        
        

    def generate_code(self, operations):
        if len(operations) == 0:
            return 'no operations'
        return self.buckaroo_to_py_core(operations)
    
    def interpret_ops(self, new_ops, df):
        operations = [{'symbol': 'begin'}]
        operations.extend(new_ops)
        if len(operations) == 1:
            return df
        return self.buckaroo_transform(operations , df)

    def setup_from_command_kls_list(self):
        #used to initially setup the interpreter, and when a command
        #is added interactively
        command_defaults, command_patterns, self.buckaroo_transform, self.buckaroo_to_py_core = configure_buckaroo(
            self.command_classes)
        self.commandConfig = dict(argspecs=command_patterns, defaultArgs=command_defaults)

    def add_command(self, incomingCommandKls):
        without_incoming = [x for x in self.command_classes if not x.__name__ == incomingCommandKls.__name__]
        without_incoming.append(incomingCommandKls)
        self.command_classes = without_incoming
        self.setup_from_command_kls_list()

    def add_analysis(self, analysis_obj):
        self.stats.add_analysis(analysis_obj)
        self.ensure_df_sync()


'''
removed for later consideration

    def run_post_processing(self):
        if self.postProcessingF:
            try:
                if self.transformed_df is None:
                    working_df = self.get_working_df()
                else:
                    working_df = self.transformed_df
                self.processed_result = self.postProcessingF(working_df)
            except Exception:
                traceback.print_exc()



'''
