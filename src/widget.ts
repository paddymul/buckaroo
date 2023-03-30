// Copyright (c) Paddy Mullen
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';


import _ from 'lodash';

import {WidgetDCFCell  } from 'paddy-react-edit-list';



import { createRoot } from "react-dom/client";
//import React, { Component, useState } from "react";
import React from "react";

import { MODULE_NAME, MODULE_VERSION } from './version';
import { tableDf } from './static';

// Import the CSS
import '../css/widget.css';




export class ExampleModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: ExampleModel.model_name,
      _model_module: ExampleModel.model_module,
      _model_module_version: ExampleModel.model_module_version,
      _view_name: ExampleModel.view_name,
      _view_module: ExampleModel.view_module,
      _view_module_version: ExampleModel.view_module_version,
      value2: {commands:[]},
      commands: []

    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
    // Add any extra serializers here
  };

  static model_name = 'ExampleModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'ExampleView'; // Set to null if no view
  static view_module = MODULE_NAME; // Set to null if no view
  static view_module_version = MODULE_VERSION;
}

export class ExampleView extends DOMWidgetView {
  render() {
    this.el.classList.add('custom-widget');
    //this.value_changed();
    const root = createRoot(this.el as HTMLElement)

    const widgetModel = this.model
    const widgetGetTransformRequester = (setDf:any) => {
      const baseRequestTransform = (passedInstructions:any) => {
	console.log("passedInstructions", passedInstructions)
	const valueCopy = _.clone(widgetModel.get('value2'))
	valueCopy['commands'] = passedInstructions
	widgetModel.set('commands', passedInstructions)
        widgetModel.set('value2', valueCopy)
	widgetModel.save_changes()

      };
      return baseRequestTransform;
    };

    root.render(React.createElement(WidgetDCFCell, {origDf:tableDf, getTransformRequester:widgetGetTransformRequester}, null));
    //this.model.on('change:value', this.value_changed, this);


  }

  value_changed() {
    this.el.textContent = this.model.get('value') + "from_js";
  }
}
// console.log("local createRoot module", createRoot)
// const root = createRoot(document.body as HTMLElement)
// console.log("Rroot", root)
