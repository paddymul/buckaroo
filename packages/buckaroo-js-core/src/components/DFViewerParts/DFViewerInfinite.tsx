import {
    useCallback,
    useMemo,
    useEffect,
    useRef,
} from "react";
import _ from "lodash";
import { DFData, DFDataRow, DFViewerConfig, SDFT, ColumnConfig } from "./DFWhole";

import { dfToAgrid, extractPinnedRows, extractSDFT, extractSingleSeriesSummary } from "./gridUtils";
import { AgGridReact } from "@ag-grid-community/react"; // the AG Grid React Component

import { getCellRendererSelector } from "./gridUtils";

import {
    GetRowIdParams,
    GridApi,
    GridOptions,
    IDatasource,
    ModuleRegistry,
    SortChangedEvent,
    CellClassParams,
    ColDef
} from "@ag-grid-community/core";
import { ClientSideRowModelModule } from "@ag-grid-community/client-side-row-model";
import {
    getAutoSize,
    getGridOptions,
    getHeightStyle,
    HeightStyleI,
    SetColumnFunc
} from "./gridUtils";
import { InfiniteRowModelModule } from "@ag-grid-community/infinite-row-model";
import { themeAlpine} from '@ag-grid-community/theming';
import { colorSchemeDark } from '@ag-grid-community/theming';

ModuleRegistry.registerModules([ClientSideRowModelModule]);
ModuleRegistry.registerModules([InfiniteRowModelModule]);


const myTheme = themeAlpine.withPart(colorSchemeDark).withParams({
    spacing:5,
    browserColorScheme: "dark",
    cellHorizontalPaddingScale: 0.3,
    columnBorder: true,
    rowBorder: false,
    rowVerticalPaddingScale: 0.5,
    wrapperBorder: false,
    fontSize: 12,
    dataFontSize: "12px",
    headerFontSize: 14,
    iconSize: 10,
    backgroundColor: "#181D1F",
    oddRowBackgroundColor: '#222628',
    headerVerticalPaddingScale: 0.6,
//    cellHorizontalPadding: 3,

})


export interface DatasourceWrapper {
    datasource: IDatasource;
    data_type: "DataSource";
    length: number; // length of full dataset, not most recent slice
    // maybe include the extra grid settings
}
export interface RawDataWrapper {
    data: DFData;
    length: number; // length of full dataset, not most recent slice
    data_type: "Raw";
}

export type DatasourceOrRaw = DatasourceWrapper | RawDataWrapper;

const staticGridOptions:GridOptions = {
    rowSelection: "single",
    enableCellTextSelection: true,
    tooltipShowDelay: 0,
    onRowClicked: (event) => {
        const sel = document.getSelection();
        if (sel === null) {
            return;
        }
        const range = document.createRange();
        const el = event?.event?.target;
        if (el === null || el === undefined) {
            return;
        }
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        //@ts-ignore
        range.selectNodeContents(el);
        sel.removeAllRanges();
        sel.addRange(range);
    },
};

/* these are gridOptions that should be fairly constant */
const outerGridOptions = (setActiveCol:SetColumnFunc, extra_grid_config?:GridOptions):GridOptions => {
    return {
        ...staticGridOptions,
        ...(extra_grid_config ? extra_grid_config : {}),
        onCellClicked: (event) => {
            const colName = event.column.getColId();
            if (setActiveCol === undefined || colName === undefined) {
                console.log("returning because setActiveCol is undefined");
                return;
            } else {
                console.log("calling setActiveCol with", colName);
                setActiveCol(colName);
            }
        },
    }
};
export function DFViewerInfinite({
    data_wrapper,
    df_viewer_config,
    summary_stats_data,
    activeCol,
    setActiveCol,
    outside_df_params,
    error_info,
}: {
    data_wrapper: DatasourceOrRaw;
    df_viewer_config: DFViewerConfig;
    summary_stats_data?: DFData;
    activeCol?: string;
    setActiveCol: SetColumnFunc;
    // these are the parameters that could affect the table,
    // dfviewer doesn't need to understand them, but it does need to use
    // them as keys to get updated data
    outside_df_params?: any;
    error_info?: string;
}) {
    const renderStartTime = useRef<number>(Date.now());
    const lastProps = useRef<any>(null);
    
    useEffect(() => {
        const now = Date.now();
        const timeSinceLastRender = now - renderStartTime.current;
        console.log(`[DFViewerInfinite] Render started at ${new Date(now).toISOString()}`);
        console.log(`[DFViewerInfinite] Time since last render: ${timeSinceLastRender}ms`);
        
        if (lastProps.current) {
            const changes = Object.keys(lastProps.current).filter(key => {
                return lastProps.current[key] !== {
                    data_wrapper,
                    df_viewer_config,
                    summary_stats_data,
                    activeCol,
                    outside_df_params,
                    error_info
                }[key];
            });
            console.log(`[DFViewerInfinite] Props that changed:`, changes);
        }
        
        lastProps.current = {
            data_wrapper,
            df_viewer_config,
            summary_stats_data,
            activeCol,
            outside_df_params,
            error_info
        };
        
        renderStartTime.current = now;
    }, [data_wrapper, df_viewer_config, summary_stats_data, activeCol, outside_df_params, error_info]);

    const styledColumns = useMemo(() => {
        return dfToAgrid(df_viewer_config, summary_stats_data || []);
    }, [df_viewer_config, summary_stats_data]);
    //const selectBackground =  df_viewer_config?.component_config?.selectionBackground ||  "var(--ag-range-selection-background-color-3)";

    const defaultColDef = useMemo( () => {
        return {
            sortable: true,
            type: "rightAligned",
            cellStyle: (params:CellClassParams) => {
                const colDef = params.column.getColDef();
                const field = colDef.field;
                const activeCol = params.context?.activeCol;
                ///console.log("defaultColDef cellStyle params", params, colDef, field, params, activeCol);
                if(activeCol  === field) {
                    //return {background:selectBackground}
                    return {background:"green"}

                }
                return {background:"red"}
            },
            enableCellChangeFlash: false,
            cellRendererSelector: getCellRendererSelector(df_viewer_config.pinned_rows)};
    }, [df_viewer_config.pinned_rows]);
    const histogram_stats:SDFT = extractSDFT(summary_stats_data||[]);

    const extra_context = {
        activeCol,
        histogram_stats,
        pinned_rows_config:df_viewer_config.pinned_rows
    }
    //const gridRef = useRef<AgGridReact<unknown>>(null);
    const pinned_rows = df_viewer_config.pinned_rows;
    const topRowData = (
        summary_stats_data
            ? extractPinnedRows(summary_stats_data, pinned_rows ? pinned_rows : [])
            : []
    ) as DFDataRow[];

    const hs = getHeightStyle(df_viewer_config, data_wrapper.length);

    const divClass = df_viewer_config?.component_config?.className || "ag-theme-alpine-dark";
    const getRowId = useCallback(
        (params: GetRowIdParams) => {
            const retVal = String(params?.data?.index) + params.context?.outside_df_params;
            return retVal;
        },
        [outside_df_params],
    );

    const gridOptions: GridOptions = {
        ...outerGridOptions(setActiveCol, df_viewer_config.extra_grid_config),
        ...getGridOptions(
            hs.domLayout,
            getAutoSize(styledColumns.length),
        ),
        onFirstDataRendered: (_params) => {
            console.log(`[DFViewerInfinite] AG-Grid finished rendering at ${new Date().toISOString()}`);
            console.log(`[DFViewerInfinite] Total render time: ${Date.now() - renderStartTime.current}ms`);
        },
        columnDefs:styledColumns,
        getRowId,
        rowModelType: "clientSide",
    };

        const [finalGridOptions, datasource] = getFinalGridOptions(data_wrapper, gridOptions, hs);
        return (
            <div className={`df-viewer  ${hs.classMode} ${hs.inIframe}`}>
                <pre>{error_info ? error_info : ""}</pre>
                <div style={hs.applicableStyle} className={`theme-hanger ${divClass}`}>
                <AgGridReact
                    theme={myTheme}
                    loadThemeGoogleFonts
                    gridOptions={finalGridOptions}
                    defaultColDef={defaultColDef}
                    datasource={datasource}
                    pinnedTopRowData={topRowData}
                    columnDefs={styledColumns}
                    context={{ outside_df_params, ...extra_context }}


                ></AgGridReact>
                </div>
            </div>
        );
        return <div>Error</div>;

}
// used to make sure there is a different element returned when
// Raw is used, so the component properly swaps over.
// Otherwise pinnedRows appear above the last scrolled position
// of the InfiniteRowSource vs having an empty data set.
const getFinalGridOptions =( 
    data_wrapper: DatasourceOrRaw, gridOptions:GridOptions, hs: HeightStyleI,
     ): [GridOptions, IDatasource] => {
    if (data_wrapper.data_type === "Raw") {
        const fakeDatasource:IDatasource = {
            rowCount:data_wrapper.data.length,
            getRows: (_params: any) => {
                console.debug("fake datasource get rows called, unexpected");
                throw new Error("fake datasource get rows called, unexpected");
            }
        }
        return [{
            ...gridOptions,
            rowData: data_wrapper.data,
            suppressNoRowsOverlay: true,

        }, fakeDatasource];
    } else if (data_wrapper.data_type === "DataSource") {
        return [getDsGridOptions(gridOptions, hs.maxRowsWithoutScrolling ), data_wrapper.datasource];
    } else {
        throw new Error(`Unexpected data_wrapper.data_type on  ${data_wrapper}`)
    }
 }

const getDsGridOptions = (origGridOptions: GridOptions, maxRowsWithoutScrolling:number):
 GridOptions => {
    const dsGridOptions: GridOptions = {
        ...origGridOptions,
        animateRows:false,
        onSortChanged: (event: SortChangedEvent) => {
            const api: GridApi = event.api;
	    //@ts-ignore
            console.log(
                "sortChanged",
                api.getFirstDisplayedRowIndex(),
                api.getLastDisplayedRowIndex(),
                event,
            );
            // every time the sort is changed, scroll back to the top row.
            // Setting a sort and being in the middle of it makes no sense
            api.ensureIndexVisible(0);
        },
        rowBuffer: 20,
        rowModelType: "infinite",
        cacheBlockSize: maxRowsWithoutScrolling + 50,
        cacheOverflowSize: 0,
        maxConcurrentDatasourceRequests: 2,
        maxBlocksInCache: 0,
        infiniteInitialRowCount: maxRowsWithoutScrolling + 50
    };
    return dsGridOptions;
};export function DFViewer({
    df_data, df_viewer_config, summary_stats_data, activeCol, setActiveCol,
}: {
    df_data: DFData;
    df_viewer_config: DFViewerConfig;
    summary_stats_data?: DFData;
    activeCol?: string;
    setActiveCol?: SetColumnFunc;
}) {
    const defaultSetColumnFunc = (newCol:string):void => {
        console.log("defaultSetColumnFunc", newCol)
    }
    const sac:SetColumnFunc = setActiveCol || defaultSetColumnFunc;
    
    return (
        <DFViewerInfinite
            data_wrapper={{
                data_type: "Raw",
                data: df_data,
                length: df_data.length
            }}
            df_viewer_config={df_viewer_config}
            summary_stats_data={summary_stats_data}
            activeCol={activeCol}
            setActiveCol={sac} />
    );
}

