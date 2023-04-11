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
from .all_transforms import configure_dcf, DefaultCommandKlsList
import json


class DCFWidget(DOMWidget):
    """TODO: Add docstring here
    """
    _model_name = Unicode('DCFWidgetModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('DCFWidgetView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    value = Unicode('Hello World').tag(sync=True)
    command_config = Dict({}).tag(sync=True)

    commands = List().tag(sync=True)

    command_classes = DefaultCommandKlsList

    js_df = Dict({}).tag(sync=True)

    transformed_df = Dict({}).tag(sync=True)
    transform_error = Unicode('').tag(sync=True)

    generated_py_code = Unicode('').tag(sync=True)
    generated_py_error = Unicode('').tag(sync=True)
    
    def __init__(self, df):
        super().__init__()
        self.df = df
        self.js_df = json.loads(df.to_json(orient='table', indent=2))
        self.setup_from_command_kls_list()

    @observe('commands')
    def interpret_commands(self, change):
        try:
            commands = change['new']
            if len(commands) == 1:
                self.transform_error = "matched"
                self.transformed_df = self.js_df
                return
            transformed_df = self.dcf_transform(commands, self.df)
            self.transformed_df = json.loads(transformed_df.to_json(orient='table', indent=2))
            self.transform_error = ''

            print("interpret_to_py_code", commands)
            self.generated_py_code = self.dcf_to_py_core(commands[1:])
        except Exception as e:
            self.transform_error = str(e)

            self.generated_py_error = str(e)

    def setup_from_command_kls_list(self):
        command_defaults, command_patterns, self.dcf_transform, self.dcf_to_py_core = configure_dcf(
            self.command_classes)
        self.command_config = dict(
            argspecs=command_patterns, defaultArgs=command_defaults)


    def add_command(self, incomingCommandKls):
        without_incoming = [x for x in self.command_classes if not x.__name__ == incomingCommandKls.__name__]
        without_incoming.append(incomingCommandKls)
        self.command_classes = without_incoming
        self.setup_from_command_kls_list()

        
        

        
        
