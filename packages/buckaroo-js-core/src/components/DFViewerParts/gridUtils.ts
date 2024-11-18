import {
    CellClassParams,
    CellRendererSelectorResult,
    ColDef,
    ICellRendererParams,
    IDatasource,
    IGetRowsParams,
} from "@ag-grid-community/core";
import { BLUE_TO_YELLOW, DIVERGING_RED_WHITE_BLUE } from "../../baked_data/colorMap";

import {
    DFWhole,
    DisplayerArgs,
    cellRendererDisplayers,
    ColumnConfig,
    ColorMappingConfig,
    ColorMapRules,
    TooltipConfig,
    ColorWhenNotNullRules,
    DFViewerConfig,
} from "./DFWhole";
import _, { zipObject } from "lodash";
import { getTextCellRenderer } from "./OtherRenderers";

import { DFData, SDFMeasure, SDFT } from "./DFWhole";

import { CellRendererArgs, FormatterArgs, PinnedRowConfig } from "./DFWhole";
import { getBakedDFViewer, simpleTooltip } from "./SeriesSummaryTooltip";
import { getFormatterFromArgs, getCellRenderer, objFormatter, getFormatter } from "./Displayer";
import { Dispatch, SetStateAction } from "react";
import { CommandConfigT } from "../CommandUtils";

// for now colDef stuff with less than 3 implementantions should stay in this file
// as implementations grow large or with many implmentations, they should move to separate files
// like displayer

export function addToColDef(
    dispArgs: DisplayerArgs,
    //@ts-ignore
    summary_stats_column: SDFMeasure,
) {
    const formatter = getFormatterFromArgs(dispArgs);
    if (formatter !== undefined) {
        const colDefExtras: ColDef = { valueFormatter: formatter };
        return colDefExtras;
    }

    if (_.includes(cellRendererDisplayers, dispArgs.displayer)) {
        const crArgs: CellRendererArgs = dispArgs as CellRendererArgs;
        return {
            cellRenderer: getCellRenderer(crArgs),
        };
    }
    return undefined;
}

export function getHistoIndex(val: number, histogram_edges: number[]): number {
    /*
np.histogram([1, 2, 3, 4,  10, 20, 30, 40, 300, 300, 400, 500], bins=5)
( [  8,       0,     2,     1,     1], 
[  1. , 100.8, 200.6, 300.4, 400.2, 500. ])
The bottom matters for us, those are the endge

this means that 8 values are between 1 and 100.8  and 2 values are between 200.6 and 300.4
  */
    if (histogram_edges.length === 0) {
        return 0;
    }
    for (let i = 0; i < histogram_edges.length; i++) {
        if (val <= histogram_edges[i]) {
            return i;
        }
    }
    return histogram_edges.length;
}

export function colorMap(cmr: ColorMapRules, histogram_edges: number[]) {
    // https://colorcet.com/gallery.html#isoluminant
    // https://github.com/holoviz/colorcet/tree/main/assets/CET
    // https://github.com/bokeh/bokeh/blob/ed285b11ab196e72336b47bf12f44e1bef5abed3/src/bokeh/models/mappers.py#L304
    const maps: Record<string, string[]> = {
        BLUE_TO_YELLOW: BLUE_TO_YELLOW,
        DIVERGING_RED_WHITE_BLUE: DIVERGING_RED_WHITE_BLUE,
    };
    const cmap = maps[cmr.map_name];

    function numberToColor(val: number) {
        const histoIndex = getHistoIndex(val, histogram_edges);
        const scaledIndex = Math.round((histoIndex / histogram_edges.length) * cmap.length);
        return cmap[scaledIndex];
    }

    function cellStyle(params: CellClassParams) {
        const val = cmr.val_column ? params.data[cmr.val_column] : params.value;
        const color = numberToColor(val);
        return {
            backgroundColor: color,
        };
    }

    const retProps = {
        cellStyle: cellStyle,
    };
    return retProps;
}

export function colorNotNull(cmr: ColorWhenNotNullRules) {
    function cellStyle(params: CellClassParams) {
        if (params.data === undefined) {
            return { backgroundColor: "inherit" };
        }
        const val = params.data[cmr.exist_column];
        const valPresent = val && val !== null;
        const isPinned = params.node.rowPinned;
        const color = valPresent && !isPinned ? cmr.conditional_color : "inherit";
        return {
            backgroundColor: color,
        };
    }

    const retProps = {
        cellStyle: cellStyle,
    };
    return retProps;
}

export function getStyler(cmr: ColorMappingConfig, col_name: string, histogram_stats: SDFT) {
    switch (cmr.color_rule) {
        case "color_map": {
            //block necessary because you cant define varaibles in case blocks
            const statsCol = cmr.val_column || col_name;
            const summary_stats_cell = histogram_stats[statsCol];

            if (summary_stats_cell && summary_stats_cell.histogram_bins !== undefined) {
                return colorMap(cmr, summary_stats_cell.histogram_bins);
            } else {
                console.log("histogram bins not found for color_map");
                return {};
            }
        }
        case "color_not_null":
            return colorNotNull(cmr);
    }
}

export function extractPinnedRows(sdf: DFData, prc: PinnedRowConfig[]) {
    return _.map(_.map(prc, "primary_key_val"), (x) => _.find(sdf, { index: x }));
}

export function getTooltip(ttc: TooltipConfig, single_series_summary_df: DFWhole): Partial<ColDef> {
    switch (ttc.tooltip_type) {
        case "simple":
            return { tooltipField: ttc.val_column, tooltipComponent: simpleTooltip };

        case "summary_series":
            return {
                tooltipComponent: getBakedDFViewer(single_series_summary_df),
                tooltipField: "index",
                tooltipComponentParams: {},
            };
    }
}

export function extractSingleSeriesSummary(
    full_summary_stats_df: DFData,
    col_name: string,
): DFWhole {
    return {
        dfviewer_config: {
            column_config: [
                { col_name: "index", displayer_args: { displayer: "obj" } },
                { col_name: col_name, displayer_args: { displayer: "obj" } },
            ],
            pinned_rows: [],
        },
        data: _.filter(
            _.map(full_summary_stats_df, (row) => _.pick(row, ["index", col_name])),
            { index: "dtype" },
        ),
    };
}

export function dfToAgrid(
    dfviewer_config: DFViewerConfig,
    full_summary_stats_df: DFData,
): ColDef[] {
    //more convienient df format for some formatters
    const hdf = extractSDFT(full_summary_stats_df || []);

    const retColumns: ColDef[] = dfviewer_config.column_config.map((f: ColumnConfig) => {
        const single_series_summary_df = extractSingleSeriesSummary(
            full_summary_stats_df,
            f.col_name,
        );

        const color_map_config = f.color_map_config
            ? getStyler(f.color_map_config, f.col_name, hdf)
            : {};

        const tooltip_config = f.tooltip_config
            ? getTooltip(f.tooltip_config, single_series_summary_df)
            : {};
        const colDef: ColDef = {
            field: f.col_name,
            headerName: f.col_name,
            cellDataType: false,
            cellStyle: {}, // necessary for colormapped columns to have a default
            ...addToColDef(f.displayer_args, hdf[f.col_name]),
            ...color_map_config,
            ...tooltip_config,
            ...f.ag_grid_specs,
        };
        return colDef;
    });
    return retColumns;
}

// this is very similar to the colDef parts of dfToAgrid
export function getCellRendererSelector(pinned_rows: PinnedRowConfig[]) {
    const anyRenderer: CellRendererSelectorResult = {
        component: getTextCellRenderer(objFormatter),
    };
    return (params: ICellRendererParams<any, any, any>): CellRendererSelectorResult | undefined => {
        if (params.node.rowPinned) {
            const pk = _.get(params.node.data, "index");
            if (pk === undefined) {
                return anyRenderer; // default renderer
            }
            const maybePrc: PinnedRowConfig | undefined = _.find(pinned_rows, {
                primary_key_val: pk,
            });
            if (maybePrc === undefined) {
                return anyRenderer;
            }
            const prc: PinnedRowConfig = maybePrc;
            const currentCol = params.column?.getColId();
            if (
                (prc.default_renderer_columns === undefined && currentCol === "index") ||
                _.includes(prc.default_renderer_columns, currentCol)
            ) {
                return anyRenderer;
            }
            const possibCellRenderer = getCellRenderer(prc.displayer_args as CellRendererArgs);

            if (possibCellRenderer === undefined) {
                const formattedRenderer: CellRendererSelectorResult = {
                    component: getTextCellRenderer(
                        getFormatter(prc.displayer_args as FormatterArgs),
                    ),
                };
                return formattedRenderer;
            }
            return { component: possibCellRenderer };
        } else {
            return undefined; // rows that are not pinned don't use a row level cell renderer
        }
    };
}

export function extractSDFT(summaryStatsDf: DFData): SDFT {
    const maybeHistogramBins = _.find(summaryStatsDf, { index: "histogram_bins" }) || {};
    const maybeHistogramLogBins = _.find(summaryStatsDf, { index: "histogram_log_bins" }) || {};
    const allColumns: string[] = _.without(
        _.union(_.keys(maybeHistogramBins), _.keys(maybeHistogramLogBins)),
        "index",
    );
    const vals: SDFMeasure[] = _.map(allColumns, (colName) => {
        return {
            histogram_bins: _.get(maybeHistogramBins, colName, []) as number[],
            histogram_log_bins: _.get(maybeHistogramLogBins, colName, []) as number[],
        };
    });
    return zipObject(allColumns, vals) as SDFT;
}
export interface PayloadArgs {
    sourceName: string;
    start: number;
    end: number;
    sort?: string;
    sort_direction?: string;
}
export interface PayloadResponse {
    key: PayloadArgs;
    data: DFData;
    length: number;
    error_info?: string;
}
export const getPayloadKey = (payloadArgs: PayloadArgs): string => {
    return `${payloadArgs.sourceName}-${payloadArgs.start}-${payloadArgs.end}-${payloadArgs.sort}-${payloadArgs.sort_direction}`;
};
export type CommandConfigSetterT = (setter: Dispatch<SetStateAction<CommandConfigT>>) => void;

export interface IDisplayArgs {
    data_key: string;
    df_viewer_config: DFViewerConfig;
    summary_stats_key: string;
}

export class LruCache<T> {
    private values: Map<string, T> = new Map<string, T>();
    private maxEntries = 10;

    public get(key: string): T | undefined {
        const hasKey = this.values.has(key);
        if (hasKey) {
            // peek the entry, re-insert for LRU strategy
            const maybeEntry = this.values.get(key);
            if (maybeEntry === undefined) {
                throw new Error(`unexpected undefined for ${key}`);
            }
            const entry: T = maybeEntry;
            this.values.delete(key);
            this.values.set(key, entry);
            return entry;
        }
        return undefined;
    }

    public put(key: string, value: T) {
        if (this.values.size >= this.maxEntries) {
            // least-recently used cache eviction strategy
            const keyToDelete = this.values.keys().next().value;
            console.log(`deleting ${keyToDelete}`);
            this.values.delete(String(keyToDelete));
        }

        this.values.set(key, value);
    }
}
export type RespCache = LruCache<PayloadResponse>;

export interface TimedIDatasource extends IDatasource {
    createTime: Date;
}

export const getDs = (
    setPaState2: (pa: PayloadArgs) => void,
    respCache: LruCache<PayloadResponse>,
): TimedIDatasource => {
    const dsLoc: TimedIDatasource = {
        createTime: new Date(),
        rowCount: undefined,
        getRows: (params: IGetRowsParams) => {
            const sm = params.sortModel;
            const outside_params_string = JSON.stringify(params.context?.outside_df_params);
            const dsPayloadArgs = {
                sourceName: outside_params_string,
                start: params.startRow,
                end: params.endRow,
                sort: sm.length === 1 ? sm[0].colId : undefined,
                sort_direction: sm.length === 1 ? sm[0].sort : undefined,
            };

            const dsPayloadArgsNext = {
                sourceName: outside_params_string,
                start: params.endRow,
                end: params.endRow + (params.endRow - params.startRow),
                sort: sm.length === 1 ? sm[0].colId : undefined,
                sort_direction: sm.length === 1 ? sm[0].sort : undefined,
            };
            //      console.log('dsPayloadArgs', dsPayloadArgs, getPayloadKey(dsPayloadArgs));
            console.log("gridUtils context outside_df_params", params.context?.outside_df_params);
            const origKey = getPayloadKey(dsPayloadArgs);
            const resp = respCache.get(origKey);

            if (resp === undefined) {
                const tryFetching = (attempt: number) => {
                    //const retryWait = 30 * Math.pow(1.7, attempt);
                    //fetching is really cheap.  I'm going to go every 10ms up until 400 ms
                    const retryWait = 15;
                    setTimeout(() => {
                        const toResp = respCache.get(origKey);
                        if (toResp === undefined && attempt < 30) {
                            console.log(
                                `Attempt ${
                                    attempt + 1
                                }: Data not found in cache, retrying... in ${retryWait} tried`,
                                origKey,
                            );
                            tryFetching(attempt + 1);
                        } else if (toResp !== undefined) {
                            const expectedPayload =
                                getPayloadKey(dsPayloadArgs) === getPayloadKey(toResp.key);
                            if (!expectedPayload) {
                                console.log("got back the wrong payload");
                            }
                            console.log("found data for", origKey, toResp.data);
                            params.successCallback(toResp.data, toResp.length);
                            // after the first success, prepopulate the cache for the following request
                            setPaState2(dsPayloadArgsNext);
                        } else {
                            console.log("Failed to fetch data after 5 attempts");
                        }
                    }, retryWait); // Increase timeout exponentially
                };

                console.log("after setTimeout, about to call setPayloadArgs", dsPayloadArgs);
                tryFetching(0);
                setPaState2(dsPayloadArgs);
            } else {
                const expectedPayload = getPayloadKey(dsPayloadArgs) === getPayloadKey(resp.key);
                console.log(
                    "data already in cache",
                    dsPayloadArgs.start,
                    dsPayloadArgs.end,
                    expectedPayload,
                    dsPayloadArgs,
                    resp.key,
                );
                if (!expectedPayload) {
                    console.log("got back the wrong payload");
                    return;
                }
                params.successCallback(resp.data, resp.length);
                // after the first success, prepopulate the cache for the following request
                setPaState2(dsPayloadArgsNext);
            }
        },
    };
    return dsLoc;
};
