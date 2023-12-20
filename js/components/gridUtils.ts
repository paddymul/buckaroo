import {
  CellClassParams,
  CellRendererSelectorResult,
  ColDef,
  ICellRendererParams,
  ValueFormatterFunc,
  ValueFormatterParams,
} from 'ag-grid-community';
import { BLUE_TO_YELLOW, DIVERGING_RED_WHITE_BLUE } from './colorMap';

import {
  DFWhole,
  DisplayerArgs,
  cellRendererDisplayers,
  FloatDisplayerA,
  IntegerDisplayerA,
  DatetimeLocaleDisplayerA,
  ColumnConfig,
  ColorMappingConfig,
  ColorMapRules,
  TooltipConfig,
} from './DFWhole';
import _, { zipObject } from 'lodash';
import { HistogramCell, getTextCellRenderer } from './CustomHeader';

import { DFData, SDFMeasure, SDFT } from './DFWhole';

import { CellRendererArgs, FormatterArgs, PinnedRowConfig } from './DFWhole';
import { getBakedDFViewer } from './BakedDFVIewer';


export const updateAtMatch = (
  cols: ColDef[],
  key: string,
  subst: Partial<ColDef>,
  negative: Partial<ColDef>
) => {
  const retColumns = cols.map((x) => {
    if (x.field === key) {
      return { ...x, ...subst };
    } else {
      return { ...x, ...negative };
    }
  });
  return retColumns;
};

export const replaceAtMatch = (
  cols: ColDef[],
  key: string,
  subst: Partial<ColDef>
) => {
  const retColumns = cols.map((x) => {
    if (x.field === key) {
      return { ...x, ...subst };
    } else {
      return { ...x };
    }
  });
  return retColumns;
};

/*
  this code should all be unit tested and in examples. Examples will
  show potential developers how this behaves. Examples should be made
  inside of AG-Grid, and independently.
  */

export const basicIntFormatter = new Intl.NumberFormat('en-US', {
  minimumFractionDigits: 0,
  maximumFractionDigits: 3,
});

export const stringFormatter = (params: ValueFormatterParams): string => {
  const val = params.value;
  return val;
};

const dictDisplayer = (val: Record<string, any>): string => {
  const objBody = _.map(
    val,
    (value, key) => `'${key}': ${objDisplayer(value)}`
  ).join(',');
  return `{ ${objBody} }`;
};

export const isValidDate = (possibleDate: any): boolean => {
  if (_.isDate(possibleDate) && isFinite(possibleDate.getTime())) {
    return true;
  }
  return false;
};

const DEFAULT_DATE_FORMAT: Intl.DateTimeFormatOptions = {
  year: 'numeric',
  month: 'numeric',
  day: 'numeric',
  hour: 'numeric',
  minute: 'numeric',
  second: 'numeric',
  hour12: false,
};

export const dateDisplayerDefault = (d: Date): string => {
  const fullStr = d.toLocaleDateString('en-CA', DEFAULT_DATE_FORMAT);
  const [dateStr, timeStr] = fullStr.split(',');
  const retVal = `${dateStr} ${timeStr}`;
  return retVal;
};

const objDisplayer = (val: any | any[]): string => {
  if (val === undefined || val === null) {
    return 'None';
  } else if (_.isArray(val)) {
    return `[ ${val.map(objDisplayer).join(', ')}]`;
  } else if (_.isBoolean(val)) {
    return boolDisplayer(val);
  } else if (_.isObject(val)) {
    return dictDisplayer(val);
  } else {
    return val.toString();
  }
  return val;
};

export const objFormatter = (params: ValueFormatterParams): string => {
  const val = params.value;
  return objDisplayer(val);
};

export const boolDisplayer = (val: boolean) => {
  if (val === true) {
    return 'True';
  } else if (val === false) {
    return 'False';
  }
  return '';
};

export const booleanFormatter = (params: ValueFormatterParams): string => {
  const val = params.value;
  return boolDisplayer(val);
};

const getIntegerFormatter = (hint: IntegerDisplayerA) => {
  const commas = Math.floor(hint.max_digits / 3);
  const totalWidth = commas + hint.max_digits;

  const formatter = new Intl.NumberFormat('en-US');
  const numericFormatter = (params: ValueFormatterParams): string => {
    const val = params.value;
    if (val === null) {
      return '';
    }
    return formatter.format(params.value).padStart(totalWidth, ' ');
  };
  return numericFormatter;
};

const getFloatFormatter = (hint: FloatDisplayerA) => {
  const floatFormatter = new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 3,
    maximumFractionDigits: 3,
  });
  return (params: ValueFormatterParams): string => {
    if (params.value === null) {
      return '';
    }
    return floatFormatter.format(params.value);
  };
};

export const getDatetimeFormatter = (colHint: DatetimeLocaleDisplayerA) => {
  return (params: ValueFormatterParams): string => {
    const val = params.value;
    if (val === null || val === undefined) {
      return '';
    }
    const d = new Date(val);
    if (!isValidDate(d)) {
      return '';
    }
    return d.toLocaleDateString(colHint.locale, colHint.args);
  };
};

export const defaultDatetimeFormatter = (
  params: ValueFormatterParams
): string => {
  const val = params.value;
  if (val === null || val === undefined) {
    return '';
  }
  const d = new Date(val);
  if (!isValidDate(d)) {
    return '';
  }
  return dateDisplayerDefault(d);
};

export function getFormatter(
  fArgs: FormatterArgs
): ValueFormatterFunc<unknown> {
  switch (fArgs.displayer) {
    case 'integer':
      return getIntegerFormatter(fArgs);
    case 'string':
      return stringFormatter;
    case 'datetimeDefault':
      return defaultDatetimeFormatter;
    case 'datetimeLocaleString':
      return getDatetimeFormatter(fArgs);
    case 'float':
      return getFloatFormatter(fArgs);
    case 'boolean':
      return booleanFormatter;
    case 'obj':
      return objFormatter;
    default:
      return stringFormatter;
  }
}

export function getCellRenderer(crArgs: CellRendererArgs) {
  if (crArgs.displayer === 'histogram') {
    return HistogramCell;
  }
  return undefined;
}

export function getFormatterFromArgs(dispArgs: DisplayerArgs) {
  if (_.includes(cellRendererDisplayers, dispArgs.displayer)) {
    return undefined;
  }
  const fArgs = dispArgs as FormatterArgs;
  return getFormatter(fArgs);
}

export function addToColDef(
  dispArgs: DisplayerArgs,
  summary_stats_column: SDFMeasure
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
  if (histogram_edges.length == 0) {
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
    const scaledIndex = Math.round(
      (histoIndex / histogram_edges.length) * cmap.length
    );
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

export function extractPinnedRows(sdf: DFData, prc: PinnedRowConfig[]) {
  return _.map(_.map(prc, 'primary_key_val'), (x) => _.find(sdf, { index: x }));
}

export function getStyler(cmr: ColorMappingConfig, foo: SDFMeasure) {
  switch (cmr.color_rule) {
    case 'color_map':
      return colorMap(cmr, foo.histogram_bins);
  }
}


export function getTooltip(ttc: TooltipConfig, single_series_summary_df:DFWhole): Partial<ColDef> {
  switch (ttc.tooltip_type) {
    case 'simple':
      return {tooltipField: ttc.val_column}

    case 'summary_series':
      return {tooltipComponent: getBakedDFViewer(single_series_summary_df), 
        tooltipField:'index', tooltipComponentParams: { }    };
  }
}

export function extractSingleSeriesSummary(full_summary_stats_df:DFData, col_name:string):DFWhole {

  return {
    dfviewer_config : { 
      column_config: [
        {col_name:'index', displayer_args: { displayer: 'obj' }},
        {col_name:col_name, displayer_args: { displayer: 'obj' }}],
      pinned_rows:[
      ],
    },
    data: _.filter(
      _.map(full_summary_stats_df, (row) => _.pick(row, ['index', col_name])),
      {'index': 'dtype'})
  }
}

export function dfToAgrid(
  tdf: DFWhole,
  full_summary_stats_df: DFData
): [ColDef[], unknown[]] {
  //more convienient df format for some formatters

  const histogram_bin_summary_df = extractSDFT(full_summary_stats_df || [])

  const retColumns: ColDef[] = tdf.dfviewer_config.column_config.map(
    (f: ColumnConfig) => {
      const single_series_summary_df = extractSingleSeriesSummary(full_summary_stats_df, f.col_name);
      const colDef: ColDef = {
        field: f.col_name,
        headerName: f.col_name,
        cellStyle: {}, // necessary for colormapped columns to have a default
        ...addToColDef(f.displayer_args, histogram_bin_summary_df[f.col_name]),
        ...(f.color_map_config
          ? getStyler(f.color_map_config, histogram_bin_summary_df[f.col_name])
          : {}),
        ...(f.tooltip_config? getTooltip(f.tooltip_config, single_series_summary_df) : {}  )
      };
      if (f.col_name === 'index') {
        colDef.pinned = 'left';
      }
      return colDef;
    }
  );
  return [retColumns, tdf.data];
}

// this is very similar to the colDef parts of dfToAgrid
export function getCellRendererSelector(pinned_rows: PinnedRowConfig[]) {
  const anyRenderer: CellRendererSelectorResult = {
    component: getTextCellRenderer(objFormatter),
  };
  return (
    params: ICellRendererParams<any, any, any>
  ): CellRendererSelectorResult | undefined => {
    if (params.node.rowPinned) {
      const pk = _.get(params.node.data, 'index');
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
      const possibCellRenderer = getCellRenderer(
        prc.displayer_args as CellRendererArgs
      );
      if (possibCellRenderer === undefined) {
        const formattedRenderer: CellRendererSelectorResult = {
          component: getTextCellRenderer(
            getFormatter(prc.displayer_args as FormatterArgs)
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
  const maybeHistogramBins =
    _.find(summaryStatsDf, { index: 'histogram_bins' }) || {};
  const maybeHistogramLogBins =
    _.find(summaryStatsDf, { index: 'histogram_log_bins' }) || {};
  const allColumns: string[] = _.without(
    _.union(_.keys(maybeHistogramBins), _.keys(maybeHistogramLogBins)),
    'index'
  );
  const vals: SDFMeasure[] = _.map(allColumns, (colName) => {
    return {
      histogram_bins: _.get(maybeHistogramBins, colName, []) as number[],
      histogram_log_bins: _.get(maybeHistogramLogBins, colName, []) as number[],
    };
  });
  return zipObject(allColumns, vals) as SDFT;
}


/*
I would love for extractSDF to be more elegant like the following function.  I just can't quite get it to work
time to move on

export function extractSDFT2(summaryStatsDf:DFData) : SDFT  {
  const rows = ['histogram_bins', 'histogram_log_bins']

  const extracted = _.map(rows, (pk) => {
    return _.find(summaryStatsDf,  {'index': pk}) || {}
  })
  const dupKeys: string[][] = _.map(extracted, _.keys);
  const allColumns: string[] = _.without(_.union(...dupKeys), 'index');
  const vals:SDFMeasure[] = _.map(allColumns, (colName) => {
    const pairs = _.map(_.zip(rows, extracted), (rname, row) => {
      return [rname, (_.get(row, colName, []) as number[])];
    })
    return _.fromPairs(pairs) as SDFMeasure;
  });
  return zipObject(allColumns, vals) as SDFT;
}
*/
