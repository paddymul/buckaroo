import { CellRendererSelectorResult, ColDef, DomLayoutType, ICellRendererParams, IDatasource, SizeColumnsToContentStrategy, SizeColumnsToFitProvidedWidthStrategy } from '@ag-grid-community/core';
import { DFWhole, DisplayerArgs, DFViewerConfig, ComponentConfig, DFData, SDFT, PinnedRowConfig } from './DFWhole';
import { CSSProperties, Dispatch, SetStateAction } from '../../../node_modules/.pnpm/react@18.3.1/node_modules/react';
import { CommandConfigT } from '../CommandUtils';
import { KeyAwareSmartRowCache, PayloadArgs } from './SmartRowCache';
import { Theme } from '@ag-grid-community/theming';
export declare function getCellRendererorFormatter(dispArgs: DisplayerArgs): ColDef;
export declare function extractPinnedRows(sdf: DFData, prc: PinnedRowConfig[]): (import('./DFWhole').DFDataRow | undefined)[];
export declare function extractSingleSeriesSummary(full_summary_stats_df: DFData, col_name: string): DFWhole;
export declare function dfToAgrid(dfviewer_config: DFViewerConfig): ColDef[];
export declare function getCellRendererSelector(pinned_rows: PinnedRowConfig[]): (params: ICellRendererParams<any, any, any>) => CellRendererSelectorResult | undefined;
export declare function extractSDFT(summaryStatsDf: DFData): SDFT;
export declare const getPayloadKey: (payloadArgs: PayloadArgs) => string;
export type CommandConfigSetterT = (setter: Dispatch<SetStateAction<CommandConfigT>>) => void;
export interface IDisplayArgs {
    data_key: string;
    df_viewer_config: DFViewerConfig;
    summary_stats_key: string;
}
export interface TimedIDatasource extends IDatasource {
    createTime: Date;
}
export declare const getDs: (src: KeyAwareSmartRowCache) => TimedIDatasource;
export type SetColumnFunc = (newCol: string) => void;
export type PossibleAutosizeStrategy = SizeColumnsToFitProvidedWidthStrategy | SizeColumnsToContentStrategy;
interface HeightStyleArgs {
    numRows: number;
    pinnedRowLen: number;
    readonly location: Location;
    rowHeight?: number;
    compC?: ComponentConfig;
}
export interface HeightStyleI {
    domLayout: DomLayoutType;
    inIframe: string;
    classMode: "short-mode" | "regular-mode";
    applicableStyle: CSSProperties;
    maxRowsWithoutScrolling: number;
}
export declare const getHeightStyle2: (maxDataPinnedRows: number, maxRows: number, component_config?: ComponentConfig, rowHeight?: number) => HeightStyleI;
export declare const heightStyle: (hArgs: HeightStyleArgs) => HeightStyleI;
export declare const getAutoSize: (numColumns: number) => SizeColumnsToFitProvidedWidthStrategy | SizeColumnsToContentStrategy;
export declare const myTheme: Theme;
export {};
