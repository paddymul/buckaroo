#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Paddy Mullen.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import DOMWidget
from traitlets import Unicode, List, Dict, observe

from ._frontend import module_name, module_version
from .customizations.all_transforms import DefaultCommandKlsList


from .customizations.analysis import (TypingStats, ComputedDefaultSummaryStats, DefaultSummaryStats)
from .customizations.histogram import (Histogram)
from .customizations.styling import (DefaultSummaryStatsStyling, DefaultMainStyling)
from .pluggable_analysis_framework.analysis_management import DfStats
from .pluggable_analysis_framework.pluggable_analysis_framework import ColAnalysis

from .serialization_utils import EMPTY_DF_WHOLE
from .dataflow.dataflow import CustomizableDataflow, StylingAnalysis, exception_protect


class BuckarooWidget(CustomizableDataflow, DOMWidget):
    """Extends CustomizableDataFlow and DOMWIdget

    Replaces generic options in CustomizableDataFlow with Pandas implementations
    Also adds buckaroo_state object and communication to simpler CustomizableDataFlow implementations
    
    """

    #### DOMWidget Boilerplate
    _model_name = Unicode('DCEFWidgetModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('DCEFWidgetView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)
    #END DOMWidget Boilerplate

    operations = List().tag(sync=True)
    operation_results = Dict(
        {'transformed_df': EMPTY_DF_WHOLE, 'generated_py_code':'# instantiation, unused'}
    ).tag(sync=True)

    df_meta = Dict({
        'columns': 5,
        'rows_shown': 20,
        'total_rows': 877}).tag(sync=True)


    buckaroo_state = Dict({
        'auto_clean': 'conservative',
        'post_processing': '',
        'sampled': False,
        'show_commands': False,
        'df_display': 'main',
        'search_string': '',
    }).tag(sync=True)


    @observe('buckaroo_state')
    @exception_protect('buckaroo_state-protector')
    def _buckaroo_state(self, change):
        #how to control ordering of column_config???
        # dfviewer_config = self._get_dfviewer_config(self.merged_sd, self.style_method)
        # self.widget_args_tuple = [self.processed_df, self.merged_sd, dfviewer_config]
        old, new = change['old'], change['new']
        if not old['post_processing'] == new['post_processing']:
            self.post_processing_method = new['post_processing']


        
    #widget config.  Change these via inheritance to alter core behaviors of buckaroo
    command_klasses = DefaultCommandKlsList
    analysis_klasses = [TypingStats, DefaultSummaryStats,
                        Histogram,
                        ComputedDefaultSummaryStats,
                        StylingAnalysis,
                        DefaultSummaryStats,
                        DefaultSummaryStatsStyling, DefaultMainStyling]


    DFStatsClass = DfStats


    def add_analysis(self, analysis_klass):
        """
        same as get_summary_sd, call whatever to set summary_sd and trigger further comps
        """

        stats = self.DFStatsClass(
            self.processed_df,
            self.analysis_klasses,
            self.df_name, debug=self.debug)
        stats.add_analysis(analysis_klass)
        self.analysis_klasses = stats.ap.ordered_a_objs
        self.setup_options_from_analysis()
        self.summary_sd = stats.sdf

    def add_processing(self, df_processing_func):
        proc_func_name = df_processing_func.__name__
        class DecoratedProcessing(ColAnalysis):
            provides_defaults = {}
            @classmethod
            def post_process_df(kls, df):
                new_df = df_processing_func(df)
                return [new_df, {}]
            post_processing_method = proc_func_name
        self.add_analysis(DecoratedProcessing)
        temp_buckaroo_state = self.buckaroo_state.copy()
        temp_buckaroo_state['post_processing'] = proc_func_name
        self.buckaroo_state = temp_buckaroo_state


class RawDFViewerWidget(DOMWidget):
    """Extends CustomizableDataFlow and DOMWIdget

    Replaces generic options in CustomizableDataFlow with Pandas implementations
    Also adds buckaroo_state object and communication to simpler CustomizableDataFlow implementations
    
    """

    #### DOMWidget Boilerplate
    _model_name = Unicode('DFViewerModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('DFViewerView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)
    #END DOMWidget Boilerplate

    # def __init__(self, raw_df, **kwargs):

    #     kwargs['df_data'] = pd_to_obj(raw_df)
        
    #     super().__init__(**kwargs)

    df_data = List([
        {'a':  5  , 'b':20, 'c': 'Paddy'},
        {'a': 58.2, 'b': 9, 'c': 'Margaret'}]).tag(sync=True)

    df_viewer_config = Dict({
        'column_config': [
            { 'col_name': 'a',
              'displayer_args': { 'displayer': 'float',   'min_fraction_digits': 2, 'max_fraction_digits': 8 }},
            { 'col_name': 'b',
              'displayer_args': { 'displayer': 'integer', 'min_digits': 3, 'max_digits': 5 }},
            { 'col_name': 'c',
              'displayer_args': { 'displayer': 'string',  'min_digits': 3, 'max_digits': 5 }}],
        'pinned_rows': [
            { 'primary_key_val': 'dtype', 'displayer_args': { 'displayer': 'obj' }},
            { 'primary_key_val': 'mean', 'displayer_args': { 'displayer': 'integer', 'min_digits': 3, 'max_digits': 5 }}]}
                            ).tag(sync=True)

    summary_stats_data = List([
        { 'index': 'mean',  'a':      28,   'b':      14, 'c': 'Padarget' },
        { 'index': 'dtype', 'a': 'float64', 'b': 'int64', 'c': 'object' }]).tag(sync=True)

    

def find_most_specific_styling(klasses, df_display_name):
    """if we have multiple styling klasses, all of which extend StylingAnalysis keyed to df_display_name='main'
    we want a deterministic result for which one is the called class to provide styling for that key

    if B extends A, B is more specific.

    Since most class extension for styling will work by extending
    DefaultMainStyling, try to follow the user's intent by making sure
    the most specific class is chosen

    https://stackoverflow.com/questions/23660447/how-can-i-sort-a-list-of-python-classes-by-inheritance-depth
    """

    

def configure_buckaroo(
        BaseBuckarooKls,
        column_config_overrides=None,
        extra_pinned_rows=None, pinned_rows=None,
        extra_analysis_klasses=None, analysis_klasses=None):
    """Used to instantiate a synthetic Buckaroo class with easier extension methods.

    It seemed more straight forward to write this as a completely
    separate function vs a classmethod so that things are clear vs
    inheritance
    """

    # In this case we are going to extend PolarsBuckarooWidget so we can take this combination with us
    base_a_klasses = BaseBuckarooKls.analysis_klasses.copy()
    if extra_analysis_klasses:
        if analysis_klasses is not None:
            raise Exception("Must specify either extra_analysis_klasses or analysis_klasses, not both")
        base_a_klasses.extend(extra_analysis_klasses)
    elif analysis_klasses:
        base_a_klasses = analysis_klasses


    #there could possibly be another way of picking off the styling
    #klass vs just knowing that it's default BaseStylingKls
    BaseStylingKls = DefaultMainStyling 

    base_pinned_rows = BaseStylingKls.pinned_rows.copy()
    if extra_pinned_rows:
        if pinned_rows is not None:
            raise Exception("Must specify either extra_pinned_rows or pinned_rows, not both")
        base_pinned_rows.extend(extra_pinned_rows)
    elif pinned_rows is not None: # is not None accomodates empty list
        base_pinned_rows = pinned_rows

    class SyntheticStyling(BaseStylingKls):
        pinned_rows = base_pinned_rows
        df_display_name = "dfviewer_special"

    

def DFViewer(df,
             column_config_overrides=None,
             extra_pinned_rows=None, pinned_rows=None,
             extra_analysis_klasses=None, analysis_klasses=None):

        
    if extra_analysis_klasses:
        if analysis_klasses is not None:
            raise Exception("Must specify either extra_analysis_klasses or analysis_klasses, not both")

    
        
                        
    bw = BuckarooWidget(df)
    dfv_config = bw.df_display_args['main']['df_viewer_config']
    dfv_config['pinned_rows'] = []
    df_data = bw.df_data_dict['main']
    return DFViewerWidget(df_data=df_data, df_viewer_config=dfv_config)



