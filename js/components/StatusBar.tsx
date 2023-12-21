// https://plnkr.co/edit/QTNwBb2VEn81lf4t?open=index.tsx
import React, { useState, useRef } from 'react';
import _ from 'lodash';
import { AgGridReact } from 'ag-grid-react'; // the AG Grid React Component
import { ColDef, GridOptions } from 'ag-grid-community';
import { basicIntFormatter } from './DFViewerParts/Displayer';
export type setColumFunc = (newCol: string) => void;

const getSearchForm = (initialVal:string, setSearchVal:any) => {
  return function MyForm() {
  function handleSubmit(e:any) {
    // Prevent the browser from reloading the page
    e.preventDefault();
    // Read the form data
    const form = e.target;
    const formData = new FormData(form);

    //@ts-ignore
    const entries = Array.from(formData.entries()) 
    //@ts-ignore
    const formDict: Record<string, string> = _.fromPairs(entries);

    console.log("formDict", formDict)
    setSearchVal(formDict['search'])
  }

  return (
    <form method="post" onSubmit={handleSubmit}>
      <label>
         <input name="search" defaultValue={initialVal} />
      </label>
    </form>
  );
}
}

const helpCell = function (params: any) {
  return (
    <a
      href="https://buckaroo-data.readthedocs.io/en/latest/feature_reference.html"
      target="_blank"
      rel="noopener"
    >
      ?
    </a>
  );
}


export interface DFMeta { // static, 
  total_rows: number;
  columns: number;
  rows_shown: number;
}

export interface BuckarooState {
  sampled: string | false;
  summary_stats: string| false; // there could be multiple 
  show_commands: string | false;
  auto_clean: string | false;
  reorderd_columns: string | false;
  search_string: string;
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
    'rows_shown' : 20,
    'total_rows' : 8_777_444
  }

  const [bState, setBState] = useState<BuckarooState>({
    'auto_clean': 'conservative',
    'reorderd_columns': false,
    'sampled' : false,
    'show_commands' : false,
    'summary_stats' : 'typing_stats',
    'search_string' : ''
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
    if(colName == 'search') {
      return;
    }
    if ( _.includes(_.keys(buckarooState), colName)){
      setBuckarooState(newBuckarooState( colName as BKeys));
    }
  };
  
  const localSetSearchString = (search_query:string) => {
    setBuckarooState({...buckarooState,
      search_string:search_query
    })

  }

const columnDefs: ColDef[] = [
  {
    field: 'search',
    width: 200,
    cellRenderer: getSearchForm( buckarooState.search_string, localSetSearchString)
  },
  {
    field: 'summary_stats',
    headerName: 'Σ', //note the greek symbols instead of icons which require buildchain work
    headerTooltip: 'Summary Stats',
    width: 120
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
    cellRenderer: helpCell
  },
  { field: 'total_rows', width: 100 },
  { field: 'rows_shown', headerName: 'displayed', width: 85 },
  { field: 'columns', width: 75 },
];

  const rowData = [
    {
      total_rows: basicIntFormatter.format(dfMeta.total_rows),
      'columns': dfMeta.columns,
      rows_shown: basicIntFormatter.format(dfMeta.rows_shown),
      sampled: buckarooState.sampled ||  '0',
      auto_clean: buckarooState.auto_clean || '0',  
      summary_stats: buckarooState.summary_stats ||  '0',
      show_commands: buckarooState.show_commands  || '0',
    },
  ];


  const gridOptions: GridOptions = {
    suppressRowClickSelection: true,
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



 