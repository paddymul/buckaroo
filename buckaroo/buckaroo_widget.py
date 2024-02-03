#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Paddy Mullen.
# Distributed under the terms of the Modified BSD License.

"""
TODO: Add module docstring
"""

from ipywidgets import DOMWidget
from traitlets import Unicode, List, Dict

from ._frontend import module_name, module_version
from .customizations.all_transforms import DefaultCommandKlsList


from .customizations.analysis import (TypingStats, ComputedDefaultSummaryStats, DefaultSummaryStats, ColDisplayHints)
from .customizations.histogram import (Histogram)
from .pluggable_analysis_framework.analysis_management import DfStats

from .serialization_utils import EMPTY_DF_WHOLE
from .dataflow_traditional import CustomizableDataflow, SimpleStylingAnalysis

"""

I have dfstats to manage the production of actual summary stats

I now need to manage the styles (column config)

I also want to manage the multipel summary stats presentations

summary stats presentations are just different pinned row configs that read from the same summary stats dictionary


"""


class BuckarooWidget(CustomizableDataflow, DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('DCEFWidgetModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('DCEFWidgetView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    operations = List().tag(sync=True)

    operation_results = Dict(
        {'transformed_df': EMPTY_DF_WHOLE, 'generated_py_code':'# instantiation, unused'}
    ).tag(sync=True)

    df_meta = Dict({
        'columns': 5,
        'rows_shown': 20,
        'total_rows': 877}).tag(sync=True)

    buckaroo_options = Dict({
        'sampled': ['random'],
        'auto_clean': ['aggressive', 'conservative'],
        'post_processing': [],
        'df_display': ['main', 'summary'],
        'show_commands': ['on'],
        'summary_stats': ['all'],
    }).tag(sync=True)
        
    #widget config.  Change these via inheritance to alter core behaviors of buckaroo
    command_klasses = DefaultCommandKlsList
    analysis_klasses = [TypingStats, DefaultSummaryStats,
                        Histogram,
                        ComputedDefaultSummaryStats,
                        SimpleStylingAnalysis,
                        ColDisplayHints]

    DFStatsClass = DfStats

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
