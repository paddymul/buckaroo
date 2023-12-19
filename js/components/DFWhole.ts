// I'm not sure about adding underlying types too

import _ from 'lodash';

// they are implied, just not sure
export interface ObjDisplayerA {
  displayer: 'obj';
}
export interface BooleanDisplayerA {
  displayer: 'boolean';
}
export interface StringDisplayerA {
  displayer: 'string';
} //max_length?: number;
export interface FloatDisplayerA {
  displayer: 'float';
}
export interface HistogramDisplayerA {
  displayer: 'histogram';
}
export interface DatetimeDefaultDisplayerA {
  displayer: 'datetimeDefault';
}
export interface IntegerDisplayerA {
  displayer: 'integer';
  min_digits: number;
  max_digits: number;
}

export interface ColorMapRules {
  color_rule: 'color_map';
  map_name: "BLUE_TO_YELLOW" | 'DIVERGING_RED_WHITE_BLUE';
}

//if exist_column is not null,  set cell style to condtional_color... used for highlighting changed values or errored_rows
export interface ErrorMapRules {
  color_rule: 'error_map';
  conditional_color: 'red';
  exist_column: string;
}

export type ColorMappingRules =
ColorMapRules| ErrorMapRules;

export interface DatetimeLocaleDisplayerA {
  displayer: 'datetimeLocaleString';
  locale: 'en-US' | 'en-GB' | 'en-CA' | 'fr-FR' | 'es-ES' | 'de-DE' | 'ja-JP';
  args: Intl.DateTimeFormatOptions;
}

// Used DisplayerA instead of FormatterArgs,  Displayer makes sense from the python side
// python doesn't care that histogram requires a cellRenderer and Integer only changes the formatter
export type FormatterArgs =
  | ObjDisplayerA
  | BooleanDisplayerA
  | StringDisplayerA
  | FloatDisplayerA
  | DatetimeDefaultDisplayerA
  | DatetimeLocaleDisplayerA
  | IntegerDisplayerA;
export type CellRendererArgs = HistogramDisplayerA;
export type DisplayerArgs = FormatterArgs | CellRendererArgs;

export const cellRendererDisplayers = ['histogram'];
export interface DFColumn {
  name: string;
  type: string;
}

export type DFDataRow = Record<
  string,
  string | number | boolean | any[] | Record<string, any> | null
>;

export type DFData = DFDataRow[];

/*
When I want to start tagging metadata onto DFData
export interface DFData {
  rows: DFDataRow[];
  //data_meta expansion point for typing info about the data as needed by non-display stuff
  // typing,  sorting, null handling I'm not sure about it
};
*/

//actually SDFT is summary stats transposed to be useful
// SDFT[col][stat_name]
// SDFT really only needs histogramBins and histogramLogBins and...? at this point
//type SDFT = any;

export interface SDFMeasure {
  histogram_bins: number[];
  histogram_log_bins: number[];
}

export type SDFT = Record<string, SDFMeasure>;

export type ColumnConfig = {
  col_name: string;
  displayer_args: DisplayerArgs;
  highlight_rules?: ColorMapRules;
  //extra column info ???
};

export type PinnedRowConfig = {
  primary_key_val: string;
  displayer_args: DisplayerArgs;
  highlight_rules?: any;
  tooltip_rules?: any;
};

export interface DFViewerConfig {
  pinned_rows: PinnedRowConfig[];
  column_config: ColumnConfig[];
  //extra_config: Any;
}

export interface DFWhole {
  dfviewer_config: DFViewerConfig;
  data: DFData;
}

export const EmptyDf: DFWhole = {
  dfviewer_config: {
    pinned_rows: [],
    column_config: [],
  },
  data: [],
};
