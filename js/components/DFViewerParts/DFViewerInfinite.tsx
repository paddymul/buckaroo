import React, { useRef, CSSProperties } from 'react';
import _ from 'lodash';
import { DFData, DFViewerConfig } from './DFWhole';

import { dfToAgrid, extractPinnedRows } from './gridUtils';
import { replaceAtMatch } from '../utils';
import { AgGridReact } from '@ag-grid-community/react'; // the AG Grid React Component

import { getCellRendererSelector } from './gridUtils';

import {
  GridApi,
  GridOptions,
  IDatasource,
  ModuleRegistry,
  SortChangedEvent,
} from '@ag-grid-community/core';
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
import {
  getAutoSize,
  getGridOptions,
  getHeightStyle,
  SetColumFunc,
} from './DFViewer';
import { InfiniteRowModelModule } from '@ag-grid-community/infinite-row-model';

ModuleRegistry.registerModules([ClientSideRowModelModule]);
ModuleRegistry.registerModules([InfiniteRowModelModule]);

export interface DatasourceWrapper {
  datasource: IDatasource;
  data_type: 'DataSource';
  length: number; // length of full dataset, not most recent slice
  // maybe include the extra grid settings
}
export interface RawDataWrapper {
  data: DFData;
  length: number; // length of full dataset, not most recent slice
  data_type: 'Raw';
}

export type DatasourceOrRaw = DatasourceWrapper | RawDataWrapper;

export function DFViewerInfinite({
  data_wrapper,
  df_viewer_config,
  summary_stats_data,
  activeCol,
  setActiveCol,
}: {
  data_wrapper: DatasourceOrRaw;
  df_viewer_config: DFViewerConfig;
  summary_stats_data?: DFData;
  style?: CSSProperties;
  activeCol?: string;
  setActiveCol?: SetColumFunc;
}) {
  const agColsPure = dfToAgrid(df_viewer_config, summary_stats_data || []);
  const selectBackground =
    df_viewer_config?.component_config?.selectionBackground ||
    'var(--ag-range-selection-background-color-3)';
  const styledColumns = replaceAtMatch(
    _.clone(agColsPure),
    activeCol || '___never',
    {
      cellStyle: { background: selectBackground },
    }
  );

  const defaultColDef = {
    sortable: true,
    type: 'rightAligned',
    cellRendererSelector: getCellRendererSelector(df_viewer_config.pinned_rows),
  };

  const gridRef = useRef<AgGridReact<unknown>>(null);
  const pinned_rows = df_viewer_config.pinned_rows;
  const topRowData = summary_stats_data
    ? extractPinnedRows(summary_stats_data, pinned_rows ? pinned_rows : [])
    : [];

  const hs = getHeightStyle(df_viewer_config, data_wrapper.length);

  const divClass =
    df_viewer_config?.component_config?.className || 'ag-theme-alpine-dark';
  const gridOptions = getGridOptions(
    setActiveCol as SetColumFunc,
    df_viewer_config,
    defaultColDef,
    _.cloneDeep(styledColumns),
    hs.domLayout,
    getAutoSize(styledColumns.length)
  );
  if (data_wrapper.data_type === 'Raw') {
    return (
      <div className={`df-viewer  ${hs.classMode} ${hs.inIframe}`}>
        <div style={hs.applicableStyle} className={`theme-hanger ${divClass}`}>
          <AgGridReact
            ref={gridRef}
            gridOptions={gridOptions}
            rowData={data_wrapper.data}
            pinnedTopRowData={topRowData}
          ></AgGridReact>
        </div>
      </div>
    );
  } else if (data_wrapper.data_type === 'DataSource') {
    const dsGridOptions = getDsGridOptions(
      gridOptions,
      data_wrapper.datasource
    );
    return (
      <div className={`df-viewer  ${hs.classMode} ${hs.inIframe}`}>
        <div style={hs.applicableStyle} className={`theme-hanger ${divClass}`}>
          <AgGridReact
            ref={gridRef}
            gridOptions={dsGridOptions}
            pinnedTopRowData={topRowData}
          ></AgGridReact>
        </div>
      </div>
    );
  } else {
    return <div>Error</div>;
  }
}

const getDsGridOptions = (
  origGridOptions: GridOptions,
  datasource: IDatasource
): GridOptions => {
  const dsGridOptions: GridOptions = {
    ...origGridOptions,
    datasource: datasource,
    /*
    onModelUpdated: (event:ModelUpdatedEvent) => {
        console.log("modelUpdated");
        console.log(event);
    }
    */
    onSortChanged: (event: SortChangedEvent) => {
      const api: GridApi = event.api;
      console.log(
        'sortChanged',
        api.getFirstDisplayedRowIndex(),
        api.getLastDisplayedRowIndex(),
        event
      );
      // every time the sort is changed, scroll back to the top row.
      // Setting a sort and being in the middle of it makes no sense
      api.ensureIndexVisible(0);
    },
    rowBuffer: 0,
    rowModelType: 'infinite',
    cacheBlockSize: 100,
    cacheOverflowSize: 2,
    maxConcurrentDatasourceRequests: 1,
    maxBlocksInCache: 10,
    infiniteInitialRowCount: 1000,
  };
  return dsGridOptions;
};
