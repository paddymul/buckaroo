import React, { useRef, CSSProperties, useState } from 'react';
import _ from 'lodash';
import { DFData, DFViewerConfig, EmptyDf } from './DFWhole';

import { dfToAgrid, extractPinnedRows } from './gridUtils';
import { replaceAtMatch } from '../utils';
import { AgGridReact } from 'ag-grid-react'; // the AG Grid React Component
import { GridOptions } from 'ag-grid-community';
import { getCellRendererSelector } from './gridUtils';
import { summaryDfForTableDf, tableDf } from 'js/baked_data/staticData';

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
  const [agColsPure, agData] = dfToAgrid(
    df,
    df_viewer_config,
    summary_stats_data || []
  );

  const styledColumns = replaceAtMatch(
    _.clone(agColsPure),
    activeCol || '___never',
    {
      cellStyle: { background: 'var(--ag-range-selection-background-color-3)' },
    }
  );

  const gridOptions: GridOptions = {
    rowSelection: 'single',
    onRowClicked: (event) => console.log('A row was clicked'),
    tooltipShowDelay: 0,

    defaultColDef: {
      sortable: true,
      type: 'rightAligned',
      cellRendererSelector: getCellRendererSelector(
        df_viewer_config.pinned_rows
      ),
    },

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
      if (gridRef !== undefined) {
        if (gridRef.current !== undefined && gridRef.current !== null) {
          if (gridRef.current.columnApi !== undefined) {
            gridRef.current.columnApi.autoSizeAllColumns();
            const dc = gridRef.current.columnApi.getAllDisplayedColumns();
            // console.log("bodyWidth", cm.bodyWidth)
            // console.log("cm", cm)

            if (dc.length !== 0) {
              const aw = dc[0].getActualWidth(); // this eventually changes after the resize
              //console.log("dc", aw);
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
      }
      //	    console.log("counter", counter, "colWidthHasBeenSet", colWidthHasBeenSet, originalColWidth, currentColWidth);
      if (counter > 0 && colWidthHasBeenSet === false) {
        counter -= 1;
        // console.log("no gridRef or gridRef.current, setting delay", counter)
        timer = window.setTimeout(conditionallyAutosize, delay);
        return;
      } else if (counter > 0 && currentColWidth === 200) {
        counter -= 1;

        // console.log(
        //     "new colwidth not recognized yet",
        //     counter, originalColWidth, gridRef.current!.columnApi!.columnModel!.displayedColumns[0].actualWidth)
        timer = window.setTimeout(conditionallyAutosize, delay);
        return;
      }
    };
    timer = window.setTimeout(conditionallyAutosize, delay);
    return () => window.clearTimeout(timer);
  };

  makeCondtionalAutosize(50, 350);
  //const pinnedTopRowData = [df.table_hints];
  //pinnedTopRowData={pinnedTopRowData}

  return (
    <div className="df-viewer">
      <div
        style={{ height: 400 }}
        className="theme-hanger ag-theme-alpine-dark"
      >
        <AgGridReact
          ref={gridRef}
          gridOptions={gridOptions}
          rowData={agData}
          pinnedTopRowData={
            summary_stats_data
              ? extractPinnedRows(
                  summary_stats_data,
                  df_viewer_config.pinned_rows
                )
              : []
          }
          columnDefs={styledColumns}
        ></AgGridReact>
      </div>
    </div>
  );
}

export function DFViewerEx() {
  const [activeCol, setActiveCol] = useState('tripduration');
  return (
    <DFViewer
      df={tableDf.data}
      df_viewer_config={tableDf.dfviewer_config}
      summary_stats_data={summaryDfForTableDf}
      activeCol={activeCol}
      setActiveCol={setActiveCol}
    />
  );
}
