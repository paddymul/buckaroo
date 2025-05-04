import {useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { DFData } from "../components/DFViewerParts/DFWhole";
import {SelectBox } from './StoryUtils'
import { AgGridReact } from "@ag-grid-community/react"; // the AG Grid React Component
import {
    //GridOptions,
    //IDatasource,
    ModuleRegistry,
    ColDef
} from "@ag-grid-community/core";
import { themeAlpine} from '@ag-grid-community/theming';
import { colorSchemeDark } from '@ag-grid-community/theming';

import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import { InfiniteRowModelModule } from "@ag-grid-community/infinite-row-model";

ModuleRegistry.registerModules([ClientSideRowModelModule]);
ModuleRegistry.registerModules([InfiniteRowModelModule]);

const myTheme = themeAlpine.withPart(colorSchemeDark).withParams({
    spacing:5,
    browserColorScheme: "dark",
    cellHorizontalPaddingScale: 0.3,
    columnBorder: true,
    rowBorder: false,
    rowVerticalPaddingScale: 0.5,
    wrapperBorder: false,
    fontSize: 12,
    dataFontSize: "12px",
    headerFontSize: 14,
    iconSize: 10,
    backgroundColor: "#181D1F",
    oddRowBackgroundColor: '#222628',
    headerVerticalPaddingScale: 0.6,
//    cellHorizontalPadding: 3,

})
const SubComponent = (
    { colDefs, data } :
    { colDefs:ColDef[], data:DFData}
) => {
    //@ts-ignore
    console.log("SubComponent, rendered", (new Date())-1)
    return (<div style={{border:"1px solid purple", height:"500px"}}>
        <AgGridReact
            columnDefs={colDefs}
            rowData={data}
            theme={myTheme}
            loadThemeGoogleFonts
        />
    </div>
    );
}



const ControlsWrapper = (
    {colDefs, data}:
    {colDefs:Record<string, ColDef[]>,
     data:Record<string, DFData>}
    ) => {

    // New state for selects
    const colDefKeys = Object.keys(colDefs);
    const dataKeys = Object.keys(data);
    const [activeColDefKey, setActiveColDefKey] = useState(colDefKeys[0] || '');
    const [activeDataKey, setActiveDataKey] = useState(dataKeys[0] || '');


    return (
        <div style={{ height: 500, width: 800 }}> 
  
            
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

