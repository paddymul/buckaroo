// Copyright (c) Paddy Mullen
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';


import _ from 'lodash';

import {WidgetDCFCell, CommandConfigT, DFWhole, CommandConfigSetterT, Operation  } from 'paddy-react-edit-list';

import { createRoot } from "react-dom/client";
//import React, { Component, useState } from "react";
import React from "react";

import { MODULE_NAME, MODULE_VERSION } from './version';
//import { tableDf } from './static';

// Import the CSS
import '../style/widget.css';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import 'paddy-react-edit-list/css/dcf-npm.css';


console.log("dcf widget module level new styles ");

export class DCFWidgetModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: DCFWidgetModel.model_name,
      _model_module: DCFWidgetModel.model_module,
      _model_module_version: DCFWidgetModel.model_module_version,
      _view_name: DCFWidgetModel.view_name,
      _view_module: DCFWidgetModel.view_module,
      _view_module_version: DCFWidgetModel.view_module_version,
      //add typing from OperationUtils
      command_config: {} as CommandConfigT,
      commands: [] as Operation[]

    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'DCFWidgetModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'ExampleView'; // Set to null if no view
  static view_module = MODULE_NAME; // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

export class DCFWidgetView extends DOMWidgetView {
    render() {
	console.log('DCFWidget View... renamed ')
	this.el.classList.add('custom-widget');
	//this.value_changed();
	const root = createRoot(this.el as HTMLElement)
	
	const widgetModel = this.model
	const widget = this
	widgetModel.on(
	    'change:command_config',
	    () => {
		widget.setCommandConfig(widgetModel.get('command_config'))},
	    this)

	const widgetGetTransformRequester = (setDf:any) => {
	    widgetModel.on('change:transformed_df', () => {
		setDf(widgetModel.get('transformed_df') as DFWhole)
	    }, this)
	    
	    const baseRequestTransform = (passedInstructions:any) => {
		console.log("transform passedInstructions", passedInstructions)
		widgetModel.set('commands', passedInstructions)
		widgetModel.save_changes()
	    };
	    return baseRequestTransform;
	};

	const widgetGetPyRequester = (setPyCode:any) => {
	    //_.delay(() => setPyCode("padddy"), 200)
	    widgetModel.on('change:generated_py_code', () => {
		const genCode = widgetModel.get('generated_py_code')
		console.log("gen code", genCode)
		setPyCode(genCode)
		//setPyCode("padddy")
	    }, this)
	    
	    const unusedFunc = (passedInstructions:any) => {
		console.log("pyRequester passed instructions", passedInstructions)
	    }
	    return unusedFunc
	};

	//this onChange gets called, the one inside of widgetGetPyRequester doesn't get called
	widgetModel.on('change:generated_py_code', () => {
	    const genCode = widgetModel.get('generated_py_code')
	    console.log("gen code2", genCode)
	    //setPyCode(genCode)
	    //setPyCode("padddy")
	}, this)
	// widgetModel.on('change:generated_py_error', () => {
	//     console.log("generated_py_error", widgetModel.get('generated_py_error' as string))
	// }, this)

	const commandConfig = widgetModel.get('command_config')
	console.log("widget, commandConfig", commandConfig, widgetModel)
	const plumbCommandConfig:CommandConfigSetterT = (setter) => {
	    widget.setCommandConfig = setter
	}
	
	const reactEl = React.createElement(WidgetDCFCell, {
	    origDf:widgetModel.get('js_df'),
	    getTransformRequester:widgetGetTransformRequester,
	    commandConfig,
	    exposeCommandConfigSetter:plumbCommandConfig,
	    getPyRequester:widgetGetPyRequester
	    //getPyRequester:(foo:any) => {console.log("getPyRequester called with", foo)}
	}, null)
	
	root.render(reactEl);
    }

    setCommandConfig = (conf:CommandConfigT) => {
	console.log("default setCommandConfig")
    }
}
