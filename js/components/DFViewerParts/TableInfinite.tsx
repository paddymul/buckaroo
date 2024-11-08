'use strict';

import {
  ColDef,
  GridApi,
  IDatasource,
  IFilterOptionDef,
  INumberFilterParams,
  ITextFilterParams,
  ModuleRegistry,
  SortChangedEvent,
} from '@ag-grid-community/core';
import { InfiniteRowModelModule } from '@ag-grid-community/infinite-row-model';
import { AgGridReact, CustomCellRendererProps } from '@ag-grid-community/react';
import '@ag-grid-community/styles/ag-grid.css';
import '@ag-grid-community/styles/ag-theme-quartz.css';
import React, { useCallback, useMemo, useState } from 'react';

import { GridOptions } from '@ag-grid-community/core';
import { winners } from '../../baked_data/olympic-winners';
import {
  getDs,
  getPayloadKey,
  PayloadArgs,
  PayloadResponse,
  sourceName,
} from './gridUtils';
import { ClientSideRowModelModule } from '@ag-grid-community/client-side-row-model';
ModuleRegistry.registerModules([ClientSideRowModelModule]);

ModuleRegistry.registerModules([InfiniteRowModelModule]);

export const InfiniteViewer = ({ dataSource }: { dataSource: IDatasource }) => {
  const containerStyle = useMemo(
    () => ({ width: '100%', height: '500px', border: '2px solid red' }),
    []
  );
  const gridStyle = useMemo(
    () => ({ height: '100%', width: '100%', border: '2px solid green' }),
    []
  );
  const filterParams: INumberFilterParams = {
    filterOptions: [
      'empty',
      {
        displayKey: 'evenNumbers',
        displayName: 'Even Numbers',
        //            predicate: (_, cellValue) => cellValue != null && cellValue % 2 === 0,
        numberOfInputs: 0,
      },
      {
        displayKey: 'oddNumbers',
        displayName: 'Odd Numbers',
        predicate: (_, cellValue) => cellValue !== null && cellValue % 2 !== 0,
        numberOfInputs: 0,
      },
      {
        displayKey: 'blanks',
        displayName: 'Blanks',
        predicate: (_, cellValue) => cellValue === null,
        numberOfInputs: 0,
      },
      {
        displayKey: 'age5YearsAgo',
        displayName: 'Age 5 Years Ago',
        predicate: ([fv1]: any[], cellValue) =>
          cellValue === null || cellValue - 5 === fv1,
        numberOfInputs: 1,
      },
      {
        displayKey: 'betweenExclusive',
        displayName: 'Between (Exclusive)',
        predicate: ([fv1, fv2], cellValue) =>
          cellValue === null || (fv1 < cellValue && fv2 > cellValue),
        numberOfInputs: 2,
      },
    ] as IFilterOptionDef[],
    maxNumConditions: 1,
  };
  const [columnDefs, setColumnDefs] = useState<ColDef[]>([
    // this row shows the row index, doesn't use any data from the row
    {
      headerName: 'ID',
      maxWidth: 100,
      // it is important to have node.id here, so that when the id changes (which happens
      // when the row is loaded) then the cell is refreshed.
      valueGetter: 'node.id',
      cellRenderer: (props: CustomCellRendererProps) => {
        if (props.value !== undefined) {
          return props.value;
        } else {
          return (
            <img src="https://www.ag-grid.com/example-assets/loading.gif" />
          );
        }
      },
    },
    {
      field: 'athlete',
      minWidth: 150,
      filterParams: {
        filterOptions: ['contains', 'startsWith', 'endsWith'],
        defaultOption: 'startsWith',
      } as ITextFilterParams,
    },
    {
      field: 'age',
      filter: 'agNumberColumnFilter',
      filterParams: filterParams,
    },
    {
      field: 'total',
      filter: 'agNumberColumnFilter',
      filterParams: {
        numAlwaysVisibleConditions: 2,
        defaultJoinOperator: 'OR',
      } as INumberFilterParams,
    },
  ]);
  console.log('setColumnDefs', setColumnDefs, useCallback);
  const defaultColDef = useMemo<ColDef>(() => {
    return {
      flex: 1,
      minWidth: 100,
      //sortable: false,
      filter: true,
    };
  }, []);

  const gridOptions: GridOptions = {
    datasource: dataSource,
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

  return (
    <div style={containerStyle}>
      <div style={gridStyle} className={'ag-theme-quartz-dark'}>
        <AgGridReact
          columnDefs={columnDefs}
          defaultColDef={defaultColDef}
          gridOptions={gridOptions}
        />
      </div>
    </div>
  );
};

export const InfiniteWrapper = ({
  payloadArgs,
  on_payloadArgs,
  payloadResponse,
}: {
  payloadArgs: PayloadArgs;
  on_payloadArgs: (pa: PayloadArgs) => void;
  payloadResponse: PayloadResponse;
}) => {
  const [ds, respCache] = useMemo(() => getDs(on_payloadArgs), []);
  respCache.put(getPayloadKey(payloadResponse.key, []), payloadResponse);
  return <InfiniteViewer dataSource={ds} />;
};

export const InfiniteEx = () => {
  // this is supposed to simulate the IPYwidgets backend
  const initialPA: PayloadArgs = { sourceName: sourceName, start: 0, end: 100 };

  const [paState, setPaState] = useState<PayloadArgs>(initialPA);
  console.log('GetterWrapper 164');
  const paToResp = (pa: PayloadArgs): PayloadResponse => {
    console.log('in paToResp', pa.start, pa.end);
    return {
      data: winners.slice(pa.start, pa.end),
      key: pa,
    };
  };
  const resp: PayloadResponse = paToResp(paState);

  return (
    <InfiniteWrapper
      payloadArgs={paState}
      on_payloadArgs={setPaState}
      payloadResponse={resp}
    />
  );
};
