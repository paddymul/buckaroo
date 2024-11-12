import React, {
  useRef,
  CSSProperties,
  useState,
  useCallback,
  useMemo,
} from 'react';
import _ from 'lodash';
import { DFData, DFDataRow, DFViewerConfig } from './DFWhole';

import { dfToAgrid, extractPinnedRows } from './gridUtils';
import { replaceAtMatch } from '../utils';
import { AgGridReact } from '@ag-grid-community/react'; // the AG Grid React Component

import { getCellRendererSelector } from './gridUtils';

import {
  GetRowIdParams,
  GridApi,
  GridOptions,
  IDatasource,
  IGetRowsParams,
  ModuleRegistry,
  SortChangedEvent,
  //  ViewportChangedEvent,
} from '@ag-grid-community/core';
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
import {
  getAutoSize,
  getGridOptions,
  getHeightStyle,
  HeightStyleI,
  SetColumFunc,
} from './DFViewer';
import { InfiniteRowModelModule } from '@ag-grid-community/infinite-row-model';
import { Operation } from '../OperationUtils';

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
  operations,
  setActiveCol,
}: {
  data_wrapper: DatasourceOrRaw;
  df_viewer_config: DFViewerConfig;
  operations: Operation[];
  summary_stats_data?: DFData;
  style?: CSSProperties;
  activeCol?: string;
  setActiveCol?: SetColumFunc;
}) {
  const styledColumns = useMemo(() => {
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
    return styledColumns;
  }, [df_viewer_config, summary_stats_data, activeCol]);
  const defaultColDef = {
    sortable: true,
    type: 'rightAligned',
    enableCellChangeFlash: false,
    cellRendererSelector: getCellRendererSelector(df_viewer_config.pinned_rows),
  };

  const gridRef = useRef<AgGridReact<unknown>>(null);
  const pinned_rows = df_viewer_config.pinned_rows;
  const topRowData = (
    summary_stats_data
      ? extractPinnedRows(summary_stats_data, pinned_rows ? pinned_rows : [])
      : []
  ) as DFDataRow[];

  const hs = getHeightStyle(df_viewer_config, data_wrapper.length);

  const divClass =
    df_viewer_config?.component_config?.className || 'ag-theme-alpine-dark';
  const getRowId = useCallback((params: GetRowIdParams) => {
    const retVal = String(params?.data?.index);
    return retVal;
  }, []);
  /*
  const purgeCache = () => {
    console.log('purge cache called');
    if (gridRef !== undefined) {
      console.log('purging infinite cache', ds_creation_time);
      //@ts-ignore
      window.gridApi = gridRef?.current?.api;
      gridRef?.current?.api?.purgeInfiniteCache();
      gridRef?.current?.api?.purgeInfiniteCache();
      gridRef?.current?.api.ensureIndexVisible(0);
    }
  };
  useCallback(() => {
    console.log('purge Cache ds_creation_time');
    purgeCache();
  }, [ds_creation_time]);
  useCallback(() => {
    console.log('purge Cache gridRef');
    purgeCache();
  }, [gridRef]);
  useCallback(() => {
    console.log('purge Cache operations');
    purgeCache();
  }, [ds_creation_time]);
  */
  const gridOptions: GridOptions = {
    ...getGridOptions(
      setActiveCol as SetColumFunc,
      df_viewer_config,
      defaultColDef,
      _.cloneDeep(styledColumns),
      hs.domLayout,
      getAutoSize(styledColumns.length)
    ),
    getRowId,
    rowModelType: 'clientSide',
  };

  if (data_wrapper.data_type === 'Raw') {
    const rdGridOptions: GridOptions = {
      ...gridOptions,
      rowData: data_wrapper.data,
      suppressNoRowsOverlay: true,
    };

    return (
      <RowDataViewer
        hs={hs}
        divClass={divClass}
        gridRef={gridRef}
        rdGridOptions={rdGridOptions}
        topRowData={topRowData}
      />
    );
  } else if (data_wrapper.data_type === 'DataSource') {
    const dsGridOptions = getDsGridOptions(gridOptions);
    return (
      <div className={`df-viewer  ${hs.classMode} ${hs.inIframe}`}>
        <div style={hs.applicableStyle} className={`theme-hanger ${divClass}`}>
          <AgGridReact
            ref={gridRef}
            gridOptions={dsGridOptions}
            datasource={data_wrapper.datasource}
            pinnedTopRowData={topRowData}
            columnDefs={_.cloneDeep(styledColumns)}
            context={{ operations }}
          ></AgGridReact>
        </div>
      </div>
    );
  } else {
    return <div>Error</div>;
  }
}
// used to make sure there is a different element returned when
// Raw is used, so the component properly swaps over.
// Otherwise pinnedRows appear above the last scrolled position
// of the InfiniteRowSource vs having an empty data set.

const RowDataViewer = ({
  hs,
  divClass,
  gridRef,
  rdGridOptions,
  topRowData,
}: {
  hs: HeightStyleI;
  divClass: string;
  gridRef: any; // AgGridReact<unknown>;
  rdGridOptions: GridOptions;
  topRowData: DFData;
}): React.JSX.Element => {
  console.log('gridRef');
  return (
    <div className={`df-viewer  ${hs.classMode} ${hs.inIframe}`}>
      <div style={hs.applicableStyle} className={`theme-hanger ${divClass}`}>
        <AgGridReact
          gridOptions={rdGridOptions}
          pinnedTopRowData={topRowData}
          columnDefs={_.cloneDeep(rdGridOptions.columnDefs)}
        ></AgGridReact>
      </div>
    </div>
  );
};

const getDsGridOptions = (origGridOptions: GridOptions): GridOptions => {
  const dsGridOptions: GridOptions = {
    ...origGridOptions,
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
    /*
    onBodyScroll: (event:BodyScrollEvent<any,any>) => {
      // this is where I want to trigger the next request
      console.log("scrollStart", event.direction,event.top)
      //event.top is in pixels
    },
    onViewportChanged: (event: ViewportChangedEvent<any>) => {
      console.log('onVieweportChanged', event.firstRow, event.lastRow);
    },
    */

    rowBuffer: 5,
    rowModelType: 'infinite',
    cacheBlockSize: 49,
    cacheOverflowSize: 2,
    maxConcurrentDatasourceRequests: 1,
    maxBlocksInCache: 5,
    infiniteInitialRowCount: 49,
  };
  return dsGridOptions;
};

export const StaticWrapDFViewerInfinite = ({
  df_data,
  df_viewer_config,
  summary_stats_data,
}: {
  df_data: DFData;
  df_viewer_config: DFViewerConfig;
  summary_stats_data?: DFData;
  style?: CSSProperties;
}) => {
  // used for demos to exercise DFViewerInfinite

  const data_wrapper: DatasourceWrapper = {
    length: df_data.length,

    data_type: 'DataSource',
    datasource: {
      getRows: (params: IGetRowsParams) => {
        console.log('StaticWrapDFViewerInfinite', params);
        params.successCallback(
          df_data.slice(params.startRow, params.endRow),
          df_data.length
        );
      },
    },
  };

  const [activeCol, setActiveCol] = useState('stoptime');

  return (
    <div style={{ height: 500 }}>
      <DFViewerInfinite
        data_wrapper={data_wrapper}
        df_viewer_config={df_viewer_config}
        summary_stats_data={summary_stats_data}
        activeCol={activeCol}
        setActiveCol={setActiveCol}
        operations={[]}
      />
    </div>
  );
};
