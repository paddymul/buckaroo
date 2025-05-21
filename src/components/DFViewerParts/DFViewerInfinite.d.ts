import { DFData, DFViewerConfig } from './DFWhole';
import { IDatasource } from '@ag-grid-community/core';
import { HeightStyleI, SetColumnFunc } from './gridUtils';
export interface DatasourceWrapper {
    datasource: IDatasource;
    data_type: "DataSource";
    length: number;
}
export interface RawDataWrapper {
    data: DFData;
    length: number;
    data_type: "Raw";
}
export type DatasourceOrRaw = DatasourceWrapper | RawDataWrapper;
export declare function DFViewerInfinite({ data_wrapper, df_viewer_config, summary_stats_data, activeCol, setActiveCol, outside_df_params, error_info, max_rows_in_configs }: {
    data_wrapper: DatasourceOrRaw;
    df_viewer_config: DFViewerConfig;
    summary_stats_data?: DFData;
    activeCol?: string;
    setActiveCol: SetColumnFunc;
    outside_df_params?: any;
    error_info?: string;
    max_rows_in_configs?: number;
}): import("react/jsx-runtime").JSX.Element;
export declare function DFViewerInfiniteInner({ data_wrapper, df_viewer_config, summary_stats_data, activeCol, setActiveCol, outside_df_params, renderStartTime, hs }: {
    data_wrapper: DatasourceOrRaw;
    df_viewer_config: DFViewerConfig;
    summary_stats_data: DFData;
    activeCol: string;
    setActiveCol: SetColumnFunc;
    outside_df_params?: any;
    renderStartTime: any;
    hs: HeightStyleI;
}): import("react/jsx-runtime").JSX.Element;
export declare function DFViewer({ df_data, df_viewer_config, summary_stats_data, activeCol, setActiveCol, }: {
    df_data: DFData;
    df_viewer_config: DFViewerConfig;
    summary_stats_data?: DFData;
    activeCol?: string;
    setActiveCol?: SetColumnFunc;
}): import("react/jsx-runtime").JSX.Element;
