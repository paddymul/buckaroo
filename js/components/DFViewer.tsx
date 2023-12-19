import React, { useRef, CSSProperties } from 'react';
import _, { zipObject } from 'lodash';
import { CellRendererArgs, DFData, DFWhole, EmptyDf, FormatterArgs, PinnedRowConfig, SDFMeasure, SDFT } from './DFWhole';

import { updateAtMatch, dfToAgrid, extractPinnedRows, getCellRenderer, objFormatter, getFormatter } from './gridUtils';
import { AgGridReact } from 'ag-grid-react'; // the AG Grid React Component
import { CellRendererSelectorResult, GridOptions, ICellRendererParams } from 'ag-grid-community';
import { getTextCellRenderer } from './CustomHeader';


export type setColumFunc = (newCol: string) => void;


export function extractSDFT(summaryStatsDf:DFData) : SDFT  {
  const maybeHistogramBins =  _.find(summaryStatsDf,   {'index': 'histogram_bins'}) || {};
  const maybeHistogramLogBins = _.find(summaryStatsDf, {'index': 'histogram_log_bins'}) || {};
  const allColumns: string[] = _.without(_.union(_.keys(maybeHistogramBins), _.keys(maybeHistogramLogBins)), 'index')
  const vals:SDFMeasure[] = _.map(allColumns, (colName) => {
    return {
      'histogram_bins': _.get(maybeHistogramBins, colName, []) as number[],
      'histogram_log_bins': _.get(maybeHistogramLogBins, colName, []) as number[]}})
  return zipObject(allColumns, vals) as SDFT;
}

/*
I would love for extractSDF to be more elegant like the following function.  I just can't quite get it to work
time to move on

export function extractSDFT2(summaryStatsDf:DFData) : SDFT  {
  const rows = ['histogram_bins', 'histogram_log_bins']

  const extracted = _.map(rows, (pk) => {
    return _.find(summaryStatsDf,  {'index': pk}) || {}
  })
  const dupKeys: string[][] = _.map(extracted, _.keys);
  const allColumns: string[] = _.without(_.union(...dupKeys), 'index');
  const vals:SDFMeasure[] = _.map(allColumns, (colName) => {
    const pairs = _.map(_.zip(rows, extracted), (rname, row) => {
      return [rname, (_.get(row, colName, []) as number[])];
    })
    return _.fromPairs(pairs) as SDFMeasure;
  });
  return zipObject(allColumns, vals) as SDFT;
}
*/

export function getCellRendererSelector(pinned_rows:PinnedRowConfig[]) {
  const anyRenderer: CellRendererSelectorResult = {
    component: getTextCellRenderer(objFormatter)
  };
  return (params:ICellRendererParams<any, any, any>): CellRendererSelectorResult | undefined => {
    if (params.node.rowPinned) {
      const pk = _.get(params.node.data, 'index');
      if (pk === undefined) {
        return anyRenderer; // default renderer
      }
      const maybePrc: PinnedRowConfig|undefined = _.find(pinned_rows, {'primary_key_val': pk});
      if (maybePrc === undefined) {
        return anyRenderer;
      }
      const prc:PinnedRowConfig = maybePrc;
      const possibCellRenderer = getCellRenderer(prc.displayer_args as CellRendererArgs);
      if (possibCellRenderer === undefined) {
        const formattedRenderer: CellRendererSelectorResult = {
          component: getTextCellRenderer(  getFormatter(prc.displayer_args as FormatterArgs))
        };
        return formattedRenderer
      }
      return { component: possibCellRenderer }
    } else {
      return undefined; // rows that are not pinned don't use a row level cell renderer
    }
  }
}


export function DFViewer(
  {
    df,
    summaryStatsDf,
    style,
    activeCol,
    setActiveCol,
  }: {
    df: DFWhole;
    summaryStatsDf?: DFData;
    style?: CSSProperties;
    activeCol?: string;
    setActiveCol?: setColumFunc;
  } = {
    df: EmptyDf,
    style: { height: '300px' },
    setActiveCol: () => null,
  }
) {
  // DFViewer is responsible for populating pinnedTopRows from 
  const [agColsPure, agData] = dfToAgrid(df,extractSDFT(summaryStatsDf||[]) );
  // console.log('dfviewer agData', agData);

  const styledColumns = updateAtMatch(
    _.clone(agColsPure),
    activeCol || '___never',
    {
      cellStyle: { background: 'var(--ag-range-selection-background-color-3)' },
    },
    { cellStyle: {} }
  );

  const gridOptions: GridOptions = {
    rowSelection: 'single',
    onRowClicked: (event) => console.log('A row was clicked'),
    defaultColDef: {
      sortable: true,
      type: 'rightAligned',
      cellRendererSelector: getCellRendererSelector(df.dfviewer_config.pinned_rows),
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
          pinnedTopRowData={summaryStatsDf? extractPinnedRows(summaryStatsDf, df.dfviewer_config.pinned_rows) : []}
          columnDefs={styledColumns}
        ></AgGridReact>
      </div>
    </div>
  );
}
