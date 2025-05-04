import {useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { DFData } from "../components/DFViewerParts/DFWhole";

import { AgGridReact } from "@ag-grid-community/react"; // the AG Grid React Component
import {
    //GridOptions,
    //IDatasource,
    ModuleRegistry,
    ColDef
} from "@ag-grid-community/core";

import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { InfiniteRowModelModule } from "@ag-grid-community/infinite-row-model";

ModuleRegistry.registerModules([ClientSideRowModelModule]);
ModuleRegistry.registerModules([InfiniteRowModelModule]);

const SubComponent = (
    { colDefs, data } :
    { colDefs:ColDef[], data:DFData}
) => {
    //@ts-ignore
    console.log("SubComponent, rendered", (new Date())-1)
    return (<div>
        <AgGridReact
            columnDefs={colDefs}
            rowData={data}
        />
    </div>
    );
}

// Reusable SelectBox component
type SelectBoxProps<T extends string> = {
  label: string;
  options: T[];
  value: T;
  onChange: (value: T) => void;
};

const SelectBox = <T extends string>({ label, options, value, onChange }: SelectBoxProps<T>) => {
  return (
    <label style={{ margin: '0 10px' }}>
      {label}:
      <select 
        value={value} 
        onChange={(e) => onChange(e.target.value as T)}
        style={{ marginLeft: '5px' }}
      >
        {options.map(option => (
          <option key={option} value={option}>{option}</option>
        ))}
      </select>
    </label>
  );
};

const ControlsWrapper = (
    {colDefs, data}:
    {colDefs:Record<string, ColDef[]>,
     data:Record<string, DFData>}
    ) => {
    const [useSecondaryConfig, setUseSecondaryConfig] = useState(false);
    const [showError, setShowError] = useState(false);
    // New state for selects
    const colDefKeys = Object.keys(colDefs);
    const dataKeys = Object.keys(data);
    const [activeColDefKey, setActiveColDefKey] = useState(colDefKeys[0] || '');
    const [activeDataKey, setActiveDataKey] = useState(dataKeys[0] || '');
    const errString = showError ? 'Error' : 'No Error';

    return (
        <div style={{ height: 500, width: 800 }}> 
            <button
              onClick={() => setUseSecondaryConfig(!useSecondaryConfig)}
            >
              Toggle Config
            </button>
            <span>Current Config: {useSecondaryConfig ? 'Secondary' : 'Primary'}</span>
            <button
              onClick={() => setShowError(!showError)}
            >
              Toggle Error
            </button>
            <span>Error State: {errString}</span>
            
            <SelectBox
              label="ColDef"
              options={colDefKeys}
              value={activeColDefKey}
              onChange={setActiveColDefKey}
            />
            
            <SelectBox
              label="Data"
              options={dataKeys}
              value={activeDataKey}
              onChange={setActiveDataKey}
            />
            
            <SubComponent colDefs={colDefs[activeColDefKey]} data={data[activeDataKey]} />
          </div>);
}


const meta = {
    title: "ConceptExamples/AGGrid",
    component: ControlsWrapper,
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof ControlsWrapper>;

export default meta;
type Story = StoryObj<typeof meta>;

//based on ColorMapDFViewerConfig... doesn't realy do anything without the cell renderers
const config1:ColDef[] = [
    {
      "field": "a",
      "headerName": "a",
      "cellDataType": false
    },
    {
      "field": "b",
      "headerName": "b",
      "cellDataType": false
    },
    {
      "field": "c",
      "headerName": "c",
      "cellDataType": false
    }
  ]

//based on IntFloatConfig
const config2:ColDef[] = [
    {
      "field": "a",
      "headerName": "a",
      "cellDataType": false
    },
    {
      "field": "a",
      "headerName": "a",
    },
    {
      "field": "b",
      "headerName": "b",
    }
  ]

export const Default: Story = {
    args: {
        colDefs:{colormapconfig: config1, IntFloatConfig:config2 },
        data: {'simple':[
            {a:50,  b:5,   c: 8},
            {a:70,  b:10,  c: 3},
            {a:300, b:3,   c:42},
            {a:200, b:19,  c:20},
          ],
        }
    },
};

