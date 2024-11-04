"use strict";

import {
    ColDef,
    GridApi,
    IDatasource,
    IGetRowsParams,
    INumberFilterParams,
    ITextFilterParams,
    ModuleRegistry,
    SortChangedEvent,
} from "@ag-grid-community/core";
import { InfiniteRowModelModule } from "@ag-grid-community/infinite-row-model";
import { AgGridReact, CustomCellRendererProps } from "@ag-grid-community/react";
import "@ag-grid-community/styles/ag-grid.css";
import "@ag-grid-community/styles/ag-theme-quartz.css";
import React, { useCallback, useMemo, useState } from "react";

import { GridOptions } from "@ag-grid-community/core";
import { winners } from "../../baked_data/olympic-winners";
import { DFData } from "./DFWhole";

ModuleRegistry.registerModules([InfiniteRowModelModule]);

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
        { field: "athlete", minWidth: 150,
            filterParams: {
                filterOptions: ["contains", "startsWith", "endsWith"],
                defaultOption: "startsWith",
              } as ITextFilterParams,

         },
        { field: "age",
            filter: "agNumberColumnFilter",
            filterParams: {
              numAlwaysVisibleConditions: 2,
              defaultJoinOperator: "OR",
            } as INumberFilterParams,
        },
        { field: "total" }
    ]);
    console.log("setColumnDefs", setColumnDefs, useCallback);
    const defaultColDef = useMemo<ColDef>(() => {
        return {
            flex: 1,
            minWidth: 100,
            //sortable: false,
            filter: true,

        };
    }, []);

    const gridOptions: GridOptions = { datasource: dataSource ,
        /*
        onModelUpdated: (event:ModelUpdatedEvent) => {
            console.log("modelUpdated");
            console.log(event);
        }
        */
       onSortChanged: (event:SortChangedEvent) => {
        const api: GridApi = event.api;
        console.log("sortChanged",
            api.getFirstDisplayedRowIndex(),
            api.getLastDisplayedRowIndex(),
            event)
        api.ensureIndexVisible(0);
       }
       



    };

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
    return `${payloadArgs.sourceName}-${payloadArgs.start}-${payloadArgs.end}-${payloadArgs.sort}-${payloadArgs.sort_direction}`;
}

interface PayloadArgs {
    sourceName: string;
    start: number;
    end: number;
    sort?: string;
    sort_direction?: string;
}
interface PayloadResponse {
    key: PayloadArgs;
    data: DFData;
}


const respCache: Record<string, PayloadResponse> = {};
const sourceName = "paddy";
const getDs = (setPaState2: (pa: PayloadArgs) => void): IDatasource => {

    const dsLoc: IDatasource = {
        rowCount: undefined,
        getRows: (params:IGetRowsParams) => {
            /*
            console.log(
                "asking for " + params.startRow + " to " + params.endRow
            );
            */
            console.log("params", params);
            console.log("params.filter", params.filterModel)
            console.log("params.filter", params.sortModel)

            // At this point in your code, you would call the server.
            // To make the demo look real, wait for 500ms before returning
            const sm = params.sortModel
            const dsPayloadArgs = { sourceName: sourceName, start: params.startRow, end: params.endRow,
                sort: sm.length === 1 ? sm[0].colId : undefined, sort_direction: sm.length === 1 ? sm[0].sort : undefined
             };
            console.log("dsPayloadArgs", dsPayloadArgs, getPayloadKey(dsPayloadArgs))
            const resp = respCache[getPayloadKey(dsPayloadArgs)];
            if (resp === undefined) {

                setTimeout(function () {
                    const toResp = respCache[getPayloadKey(dsPayloadArgs)];
                    if (toResp === undefined) {
                        console.log("didn't find the data inside of respCache after waiting");
                    } else {
                        //endRow is possibly wrong
                        const expectedPayload = getPayloadKey(dsPayloadArgs) === getPayloadKey(toResp.key);
                        console.log("calling success callback", expectedPayload, dsPayloadArgs, toResp.key);
                        if(!expectedPayload) {
                            console.log("got back the wrong payload");
                            debugger;
                        }
                        params.successCallback(toResp.data, -1);
                    }
                }, 100);
                console.log("after setTimeout, about to call setPayloadArgs")
                setPaState2(dsPayloadArgs);
            } else {
                const expectedPayload = getPayloadKey(dsPayloadArgs) === getPayloadKey(resp.key);
                console.log("data already in cache", expectedPayload, dsPayloadArgs, resp.key);
                if(!expectedPayload) {
                    console.log("got back the wrong payload");
                    debugger;
                }
                params.successCallback(resp.data, -1);
            }
        }
    };
    return dsLoc;
}


export const InfiniteWrapper = ({ payloadArgs, on_payloadArgs, payloadResponse }: {
    payloadArgs: PayloadArgs,
    on_payloadArgs: (pa: PayloadArgs) => void,
    payloadResponse: PayloadResponse,

}) => {
    const ds = getDs(on_payloadArgs);
    respCache[getPayloadKey(payloadArgs)] = payloadResponse;
    return <InfiniteViewer dataSource={ds} />
}

export const InfiniteEx = () => {

    // this is supposed to simulate the IPYwidgets backend
    const initialPA: PayloadArgs = { sourceName: sourceName, start: 0, end: 100 };

    const [paState, setPaState] = useState<PayloadArgs>(initialPA);
    console.log("GetterWrapper 164");
    const paToResp = (pa: PayloadArgs): PayloadResponse => {
        console.log("in paToResp", pa.start, pa.end)
        return {
            data: winners.slice(pa.start, pa.end),
            key: pa
        }
    }
    const resp: PayloadResponse = paToResp(paState);


    return (<InfiniteWrapper
        payloadArgs={paState}
        on_payloadArgs={setPaState}
        payloadResponse={resp}

    />);
}