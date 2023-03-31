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
from .dcf.all_transforms import dcf_transform
import json


class ExampleWidget(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('ExampleModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('ExampleView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    value = Unicode('Hello World').tag(sync=True)
    value2 = Dict({}).tag(sync=True)
    commands = List().tag(sync=True)

    js_df = Dict({}).tag(sync=True)
    transformed_df = Dict({}).tag(sync=True)
    transform_error = Unicode('').tag(sync=True)
    
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.js_df = json.loads(df.to_json(orient='table', indent=2))

    @observe('commands')
    def interpret_commands(self, change):
        try:
            commands = change['new']
            if len(commands) == 1:
                self.transform_error = "matched"
                self.transformed_df = self.js_df
                return
            transformed_df = dcf_transform(commands, self.df)
            self.transformed_df = json.loads(transformed_df.to_json(orient='table', indent=2))
            self.transform_error = ''
        except Exception as e:
            self.transform_error = str(e)
        

        
        

        
        
