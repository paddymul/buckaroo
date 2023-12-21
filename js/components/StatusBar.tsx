// https://plnkr.co/edit/QTNwBb2VEn81lf4t?open=index.tsx
import React, { useState, useRef } from 'react';
import _ from 'lodash';
import { AgGridReact } from 'ag-grid-react'; // the AG Grid React Component
import { ColDef, GridOptions } from 'ag-grid-community';
import { basicIntFormatter } from './DFViewerParts/Displayer';
export type setColumFunc = (newCol: string) => void;


const columnDefs: ColDef[] = [
  {
    field: 'summary_stats',
    headerName: 'Σ', //note the greek symbols instead of icons which require buildchain work
    headerTooltip: 'Summary Stats',
    width: 120,
  },
  {
    field: 'auto_clean',
    //headerName: 'Σ', //note the greek symbols instead of icons which require buildchain work
    headerName: 'auto cleaning',
    headerTooltip: 'Auto Cleaning config',
    width: 120,
  },

  //   { field: 'reorderdColumns',
  //   headerName: "Θ",
  //   headerTooltip:"Reorder Columns",
  //   width:30
  // },
  {
    field: 'show_commands',
    headerName: 'λ',
    headerTooltip: 'Show Commands',
    width: 30,
  },

  { field: 'sampled', headerName: 'Ξ', headerTooltip: 'Sampled', width: 30 },
  {
    field: 'help',
    headerName: '?',
    headerTooltip: 'Help',
    width: 30,
    cellRenderer: function (params: any) {
      return (
        <a
          href="https://buckaroo-data.readthedocs.io/en/latest/feature_reference.html"
          target="_blank"
          rel="noopener"
        >
          ?
        </a>
      );
    },
  },

  { field: 'totalRows', width: 100 },
  { field: 'columns', width: 100 },
  { field: 'rowsShown', width: 120 },
  { field: 'sampleSize', width: 120 },
];


export interface DFMeta { // static, 
  totalRows: number;
  columns: number;
  rowsShown: number;
  sampleSize: number;
}

export interface BuckarooState {
  sampled: string | false;
  summary_stats: string| false; // there could be multiple 
  show_commands: string | false;
  auto_clean: string | false;
  reorderd_columns: string | false;
}

export interface BuckarooOptions {
  sampled: string[];
  summary_stats: string[];
  show_commands: string[];
  auto_clean: string[];
  reorderd_columns: string[];
}

export type BKeys = keyof BuckarooState;


export function StatusBarEx() {

  const dfm: DFMeta = {
    'columns': 5,
    'rowsShown' : 20,
    'sampleSize' : 10_000,
    'totalRows' : 877
  }

  const [bState, setBState] = useState<BuckarooState>({
    'auto_clean': 'conservative',
    'reorderd_columns': false,
    'sampled' : false,
    'show_commands' : false,
    'summary_stats' : 'typing_stats'
  })

  const bOptions: BuckarooOptions = {
    'auto_clean': ['aggressive', 'conservative'],
    'reorderd_columns': [],
    'sampled' : ['random'],
    'show_commands' : ['on'],
    'summary_stats' : ['full', 'all', 'typing_stats']
  }


  return <StatusBar 
                      dfMeta={dfm}
                      buckarooState={bState}
                      setBuckarooState={setBState}
                      buckarooOptions={bOptions}
                      />
}
export function StatusBar({
  dfMeta,
  buckarooState,
  setBuckarooState,
  buckarooOptions,
}: {
  dfMeta: DFMeta;
  buckarooState:BuckarooState;
  setBuckarooState:React.Dispatch<React.SetStateAction<BuckarooState>>;
  buckarooOptions:BuckarooOptions;
}) {

  const rowData = [
    {
      totalRows: basicIntFormatter.format(dfMeta.totalRows),
      'columns': dfMeta.columns,
      rowsShown: basicIntFormatter.format(dfMeta.rowsShown),
      sampleSize: basicIntFormatter.format(dfMeta.sampleSize),
      sampled: buckarooState.sampled ||  '0',
      auto_clean: buckarooState.auto_clean || '0',  
      summary_stats: buckarooState.summary_stats ||  '0',
      show_commands: buckarooState.show_commands  || '0',
    },
  ];

  const optionCycles =  _.fromPairs(_.map(buckarooOptions, (v:any, k) => [k, _.concat([false], v)]));
  //@ts-ignore
  const idxs = _.fromPairs(_.map(_.keys(optionCycles), (k) => [k, _.indexOf(optionCycles[k], buckarooState[k])]))

  const nextIndex = (curIdx:number, arr:any[]) => {
    if (curIdx == (arr.length - 1)) {
      return 0;
    }
    return curIdx + 1;
  }

  const newBuckarooState = (k:BKeys) => {
    const arr = optionCycles[k];
    const curIdx = idxs[k];
    const nextIdx = nextIndex(curIdx, arr);
    const newVal = arr[nextIdx];
    const newState = _.clone(buckarooState);
    //console.log("k", k, "arr", arr, 'curIdx', curIdx, 'nextIdx', nextIdx, 'newVal', newVal);
    newState[k] = newVal;
    return newState;
  }
  const updateDict = (event: any) => {
    const colName = event.column.getColId();
    setBuckarooState(newBuckarooState( colName as BKeys));
  };

  const gridOptions: GridOptions = {
    rowSelection: 'single',
  };

  const gridRef = useRef<AgGridReact<unknown>>(null);
  const defaultColDef = {
//    type: 'left-aligned',
    cellStyle: { textAlign: 'left' },
  };
  return (
    <div className="statusBar">
      <div style={{ height: 50 }} className="theme-hanger ag-theme-alpine-dark">
        <AgGridReact
          ref={gridRef}
          onCellClicked={updateDict}
          gridOptions={gridOptions}
          defaultColDef={defaultColDef}
          rowData={rowData}
          columnDefs={columnDefs}
        ></AgGridReact>
      </div>
    </div>
  );
}
