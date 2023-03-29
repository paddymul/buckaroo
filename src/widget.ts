// Copyright (c) Paddy Mullen
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';


import {DCFCell  } from 'paddy-react-edit-list';


import { createRoot } from "react-dom/client";
//import ReactDOM from 'react-dom/client';
//import * as rd from "react-dom/client";

import { MODULE_NAME, MODULE_VERSION } from './version';

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
      value: 'Hello World',
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
    console.log("this.el", this.el)
    this.value_changed();
    console.log("this", this)
    try {
      // console.log("RDCreateroot", ReactDOM.createRoot);
      // const createRoot = ReactDOM.createRoot
      console.log("DCFCell2", DCFCell)
      console.log("112", createRoot)
      const root = createRoot(this.el as HTMLElement)
      console.log("root2", root)
      //root.render(React.createElement(DCFCell, {}, null));
    } catch (e:any) {
      console.log("error", e)
    }


    this.model.on('change:value', this.value_changed, this);


    //console.log("this.model", this.model)
    


    // const root = createRoot(document.getElementById("app") as HTMLElement)
    // root.render(React.createElement(Main, { app: this }, null));


  }

  value_changed() {
    this.el.textContent = this.model.get('value') + "from_js";
  }
}
// console.log("local createRoot module", createRoot)
// const root = createRoot(document.body as HTMLElement)
// console.log("Rroot", root)
