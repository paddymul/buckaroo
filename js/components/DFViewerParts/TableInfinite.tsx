"use strict";

import {
    ColDef,
    IDatasource,
    ModuleRegistry,
} from "@ag-grid-community/core";
import { InfiniteRowModelModule } from "@ag-grid-community/infinite-row-model";
import { AgGridReact, CustomCellRendererProps } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import React, { useCallback, useMemo, useState } from "react";

//import { GridReadyEvent } from "@ag-grid-community/core";


import { GridOptions } from "@ag-grid-community/core";
import { winners } from "../../baked_data/olympic-winners";
import { DFData } from "./DFWhole";

ModuleRegistry.registerModules([InfiniteRowModelModule]);

interface PayloadArgs {
    sourceName: string;
    start: number;
    end: number
}
interface PayloadResponse {
    key: PayloadArgs;
    data: DFData;
}


export const InfiniteExSimple = () => {

    const dataSource: IDatasource = {
        rowCount: undefined,
        getRows: (params) => {
            console.log(
                "asking for " + params.startRow + " to " + params.endRow
            );
            // At this point in your code, you would call the server.
            // To make the demo look real, wait for 500ms before returning
            setTimeout(function () {
                // take a slice of the total rows
                console.log("timeoutFunc", params.startRow, params.endRow)
                console.log("params", params)

                const rowsThisPage = winners.slice(params.startRow, params.endRow);
                // if on or after the last page, work out the last row.
                let lastRow = -1;
                if (winners.length <= params.endRow) {
                    lastRow = winners.length;
                }
                // call the success callback
                console.log("about to call successCallback");
                params.successCallback(rowsThisPage, lastRow);
            }, 500);
        },
    };
    return <InfiniteViewer dataSource={dataSource} />
}
export const InfiniteViewer = ({ dataSource }: { dataSource: IDatasource }) => {
    const containerStyle = useMemo(() => ({ width: "100%", height: "500px", border: "2px solid red" }), []);
    const gridStyle = useMemo(() => ({ height: "100%", width: "100%", border: "2px solid green" }), []);

    const [columnDefs, setColumnDefs] = useState<ColDef[]>([
        // this row shows the row index, doesn't use any data from the row
        {
            headerName: "ID",
            maxWidth: 100,
            // it is important to have node.id here, so that when the id changes (which happens
            // when the row is loaded) then the cell is refreshed.
            valueGetter: "node.id",
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
        { field: "athlete", minWidth: 150 },
        { field: "age" },
        { field: "total" }
    ]);
    console.log("setColumnDefs", setColumnDefs, useCallback);
    const defaultColDef = useMemo<ColDef>(() => {
        return {
            flex: 1,
            minWidth: 100,
            sortable: false,
        };
    }, []);

    const gridOptions: GridOptions = { datasource: dataSource };

    return (
        <div style={containerStyle}>
            <div style={gridStyle} className={"ag-theme-quartz-dark"}>
                <AgGridReact
                    columnDefs={columnDefs}
                    defaultColDef={defaultColDef}
                    rowBuffer={0}
                    rowModelType={"infinite"}
                    cacheBlockSize={100}
                    cacheOverflowSize={2}
                    maxConcurrentDatasourceRequests={1}
                    infiniteInitialRowCount={1000}
                    maxBlocksInCache={10}
                    gridOptions={gridOptions}
                />
            </div>
        </div>
    );
};

const getPayloadKey = (payloadArgs: PayloadArgs): string => {
    return `${payloadArgs.sourceName}-${payloadArgs.start}-${payloadArgs.end}`;
}


const respCache: Record<string, PayloadResponse> = {};
const sourceName = "paddy";

export const PayloadGetter = ({ payloadArgs, on_PayloadArgs, payloadResponse, ds }: {
    payloadArgs: PayloadArgs,
    on_PayloadArgs: (pa: PayloadArgs) => void,
    payloadResponse: PayloadResponse,
    ds:IDatasource
}) => {
    respCache[getPayloadKey(payloadArgs)] = payloadResponse;
    return <InfiniteViewer dataSource={ds} />
}

export const GetterWrapper = ({ payloadArgs, on_PayloadArgs, ds }: {
    payloadArgs: PayloadArgs,
    on_PayloadArgs: (pa: PayloadArgs) => void,
    ds:IDatasource
}) => {
    console.log("GetterWrapper 164");
    const paToResp = (pa: PayloadArgs): PayloadResponse => {
        console.log("in paToResp", pa.start, pa.end)
        return {
            data: winners.slice(pa.start, pa.end),
            key: pa
        }
    }
    const resp: PayloadResponse = paToResp(payloadArgs);
    return (<PayloadGetter
        payloadArgs={payloadArgs}
        on_PayloadArgs={on_PayloadArgs}
        payloadResponse={resp}
        ds={ds}
        />);
}


export const InfiniteEx = () => {
    // this is supposed to simulate the IPYwidgets backend
    const initialPA: PayloadArgs = { sourceName: sourceName, start: 0, end: 100 };

    const [paState, setPaState] = useState<PayloadArgs>(initialPA);
    const globalDS: IDatasource = {
        rowCount: undefined,
        getRows: (params) => {
            console.log(
                "asking for " + params.startRow + " to " + params.endRow
            );
            // At this point in your code, you would call the server.
            // To make the demo look real, wait for 500ms before returning
            const dsPayloadArgs = { sourceName: sourceName, start: params.startRow, end: params.endRow };

            const resp = respCache[getPayloadKey(dsPayloadArgs)];
            if (resp === undefined) {
                setTimeout(function () {
                    const toResp = respCache[getPayloadKey(dsPayloadArgs)];
                    if (toResp === undefined) {
                        console.log("didn't find the data inside of respCache after waiting");
                    } else {
                        //endRow is possibly wrong
                        console.log("calling success callback", getPayloadKey(dsPayloadArgs) === getPayloadKey(toResp.key), dsPayloadArgs, toResp.key);
                        params.successCallback(toResp.data, -1);
                    }
                }, 3000);
                console.log("after setTimeout, about to call setPayloadArgs")
                setPaState(dsPayloadArgs);
            } else {
                console.log("data already in cache", getPayloadKey(dsPayloadArgs) === getPayloadKey(resp.key), dsPayloadArgs, resp.key);
                params.successCallback(resp.data, -1);
            }
        }
    };
    return (<GetterWrapper
        payloadArgs={paState}
        on_PayloadArgs={setPaState}
        ds={globalDS}
    />);

}
