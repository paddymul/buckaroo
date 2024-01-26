import React, { useRef, CSSProperties } from 'react';
import _ from 'lodash';
import { DFData, DFViewerConfig, EmptyDf } from './DFWhole';

import { dfToAgrid, extractPinnedRows } from './gridUtils';
import { replaceAtMatch } from '../utils';
import { AgGridReact } from 'ag-grid-react'; // the AG Grid React Component
import { GridOptions } from 'ag-grid-community';
import { getCellRendererSelector } from './gridUtils';

export type setColumFunc = (newCol: string) => void;

export function DFViewer(
  {
    df,
    df_viewer_config,
    summary_stats_data,
    style,
    activeCol,
    setActiveCol,
  }: {
    df: DFData;
    df_viewer_config: DFViewerConfig;
    summary_stats_data?: DFData;
    style?: CSSProperties;
    activeCol?: string;
    setActiveCol?: setColumFunc;
  } = {
    df: EmptyDf.data,
    df_viewer_config: EmptyDf.dfviewer_config,
    summary_stats_data: [],
    style: { height: '300px' },
    setActiveCol: () => null,
  }
) {
  //console.log("dfviewer df_viewer_config", df_viewer_config);
//  console.log("summary_stats_data", summary_stats_data);
//  console.log("full_object", {'df':df, 'df_viewer_config':df_viewer_config, 'summary_stats_data': summary_stats_data})
  const [agColsPure, agData] = dfToAgrid(
    df,
    df_viewer_config,
    summary_stats_data || []
  );
  const pinned_rows = df_viewer_config.pinned_rows;
  const styledColumns = replaceAtMatch(
    _.clone(agColsPure),
    activeCol || '___never',
    {
      cellStyle: { background: 'var(--ag-range-selection-background-color-3)' },
    }
  );

  const defaultColDef = {
    sortable: true,
    type: 'rightAligned',
    cellRendererSelector: getCellRendererSelector(df_viewer_config.pinned_rows),
  }

  const gridOptions: GridOptions = {
    rowSelection: 'single',
    onRowClicked: (event) => console.log('A row was clicked'),
    tooltipShowDelay: 0,

    // defaultColDef needs to be specifically passed in as a prop to the component, not defined here,
    // otherwise updates aren't reactive

    onCellClicked: (event) => {
      const colName = event.column.getColId();
      if (setActiveCol === undefined || colName === undefined) {
        return;
      } else {
        setActiveCol(colName);
      }
    },
  };
  const gridRef = useRef<AgGridReact<unknown>>(null);

  const makeCondtionalAutosize = (count: number, delay: number) => {
    /*
      this code is buggy and I'm not confident in it. I'm very
      surprised that automatically autosizing AG-grid requires custom
      functions to be written vs just a flag.
      */

    let counter = count;
    //let timer: NodeJS.Timeout;
    let timer: number;
    let colWidthHasBeenSet = false;
    let currentColWidth = -10;
    if (gridRef === undefined || gridRef.current === null) {
      currentColWidth = 200;
    } else {
      try {
        const dc = gridRef?.current?.columnApi.getAllDisplayedColumns();

        if (dc.length !== 0) {
          currentColWidth = dc[0].getActualWidth();
        } else {
          currentColWidth = 200;
        }
      } catch (e) {
        console.log('88, gridref not defined yet', e);
      }
    }

    const conditionallyAutosize = () => {

      if (gridRef.current !== undefined && gridRef.current !== null) {
        if (gridRef.current.columnApi !== undefined) {
          gridRef.current.columnApi.autoSizeAllColumns();
          const dc = gridRef.current.columnApi.getAllDisplayedColumns();

          if (dc.length !== 0) {
            const aw = dc[0].getActualWidth(); // this eventually changes after the resize
            if (colWidthHasBeenSet === false) {
              currentColWidth = aw;
              colWidthHasBeenSet = true;
            } else {
              currentColWidth = aw;
            }
          }
          gridRef.current.forceUpdate();
        }
      }

      if (counter > 0 && colWidthHasBeenSet === false) {
        counter -= 1;
        timer = window.setTimeout(conditionallyAutosize, delay);
        return;
      } else if (counter > 0 && currentColWidth === 200) {
        counter -= 1;
        timer = window.setTimeout(conditionallyAutosize, delay);
        return;
      }
    };
    timer = window.setTimeout(conditionallyAutosize, delay);
    return () => window.clearTimeout(timer);
  };

  makeCondtionalAutosize(50, 350);

const topRowData =    (   summary_stats_data
? extractPinnedRows(
    summary_stats_data,
    //df_viewer_config.pinned_rows
    pinned_rows ? pinned_rows:[]
  )
: [] )

  return (
    <div className="df-viewer">
      <div
        style={{ height: 400 }}
        className="theme-hanger ag-theme-alpine-dark"
      >
        <AgGridReact
          ref={gridRef}
          defaultColDef={defaultColDef}
          gridOptions={gridOptions}
          rowData={agData}
          pinnedTopRowData={topRowData}
          columnDefs={styledColumns}
        ></AgGridReact>
      </div>
    </div>
  );
}

export function DFViewerEx() {
//  const [activeCol, setActiveCol] = useState('tripduration');
  return (
    <div>paddy</div>
  );
}

/*
    //import { summaryDfForTableDf, tableDf } from '../../baked_data/staticData';

    <DFViewer
      df={tableDf.data}
      df_viewer_config={tableDf.dfviewer_config}
      summary_stats_data={summaryDfForTableDf}
      activeCol={activeCol}
      setActiveCol={setActiveCol}
    />

    */
