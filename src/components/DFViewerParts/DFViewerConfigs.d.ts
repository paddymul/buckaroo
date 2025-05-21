import { ColumnConfig, DFViewerConfig } from './DFWhole';
export declare const objColumn: (col_name: string) => ColumnConfig;
export declare const floatColumn: (col_name: string, min_fraction_digits: number, max_fraction_digits: number) => ColumnConfig;
export declare const integerColumn: (col_name: string, min_digits: number, max_digits: number) => ColumnConfig;
export declare const primaryConfigPrimary: DFViewerConfig;
