import React, {
    Component,
    useState,
    useRef,
    useEffect,
    useLayoutEffect,
    useCallback,
    CSSProperties
} from 'react';
import _ from 'lodash';
import {updateAtMatch, dfToAgrid} from './gridUtils';
import {AgGridReact} from 'ag-grid-react'; // the AG Grid React Component
import {
    ColDef,
    Grid,
    GridOptions,
    GridColumnsChangedEvent,
    GridReadyEvent
} from 'ag-grid-community';
import {bakedOperations} from './OperationUtils';

export type setColumFunc = (newCol: string) => void;

export interface DfConfig {
    totalRows: number;
    columns: number;
    rowsShown: number;
    sampleSize: number;
    summaryStats: boolean;
    reorderdColumns: boolean;
}

const columnDefs: ColDef[] = [
    {field: 'totalRows'},
    {field: 'columns'},
    {field: 'rowsShown'},
    {field: 'sampleSize'},
    {field: 'summaryStats'},
    {field: 'reorderdColumns'}
];

export function StatusBar({config, setConfig}) {
    const {totalRows, columns, rowsShown, sampleSize, summaryStats, reorderdColumns} = config;

    const rowData = [
        {
            totalRows,
            columns,
            rowsShown,
            sampleSize,
            summaryStats: summaryStats.toString(),
            reorderdColumns: reorderdColumns.toString()
        }
    ];

    const updateDict = (event) => {
        const colName = event.column.getColId();
        if (colName === 'summaryStats') {
            setConfig({...config, summaryStats: !config.summaryStats});
        } else if (colName === 'reorderdColumns') {
            setConfig({...config, reorderdColumns: !config.reorderdColumns});
        }
    };
    const gridOptions: GridOptions = {
        rowSelection: 'single'
    };

    const gridRef = useRef<AgGridReact<unknown>>(null);
    const defaultColDef = {
        type: 'left-aligned',
        cellStyle: {textAlign: 'left'}
    };
    return (
        <div className='statusBar'>
            <div style={{height: 50}} className='theme-hanger ag-theme-alpine-dark'>
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

export function StatusBarEx() {
    const [sampleConfig, setConfig] = useState<DfConfig>({
        totalRows: 1309,
        columns: 30,
        rowsShown: 500,
        sampleSize: 10_000,
        summaryStats: false,
        reorderdColumns: false
    });

    return <StatusBar config={sampleConfig} setConfig={setConfig} />;
}
