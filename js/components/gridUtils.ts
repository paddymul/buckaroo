import {
  CellClassParams,
  ColDef,
  ValueFormatterFunc,
  ValueFormatterParams,
} from 'ag-grid-community';

import {
  DFWhole,
  CellRendererArgs,
  DisplayerArgs,
  cellRendererDisplayers,
  FormatterArgs,
  FloatDisplayerA,
  IntegerDisplayerA,
  DatetimeLocaleDisplayerA,
  ColumnConfig,
  DFData,
  PinnedRowConfig
} from './DFWhole';
import _ from 'lodash';
import { HistogramCell } from './CustomHeader';
import { SDFMeasure, SDFT } from './DFWhole';
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

export const defaultDatetimeFormatter = (params: ValueFormatterParams): string => {
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


export function getFormatter(fArgs: FormatterArgs): ValueFormatterFunc<unknown> {
  if (fArgs === undefined) {
    return stringFormatter;
  }
  if (fArgs.displayer === 'integer') {
    return getIntegerFormatter(fArgs);
  } else if (fArgs.displayer === 'string') {
    return stringFormatter;
  } else if (fArgs.displayer === 'datetimeDefault') {
    return defaultDatetimeFormatter;
  } else if (fArgs.displayer === 'datetimeLocaleString') {
    return getDatetimeFormatter(fArgs);
  } else if (fArgs.displayer === 'float') {
    return getFloatFormatter(fArgs);
  } else if (fArgs.displayer === 'boolean') {
    return booleanFormatter;
  } else if (fArgs.displayer === 'obj') {
    return objFormatter;
  }
  return stringFormatter;
}


export function getCellRenderer(crArgs: CellRendererArgs) {
  if (crArgs.displayer == 'histogram') {
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


export function addToColDef(dispArgs: DisplayerArgs, summary_stats_column: SDFMeasure) {
  const formatter = getFormatterFromArgs(dispArgs);
  if (formatter!== undefined) {
    const colDefExtras: ColDef = { valueFormatter: formatter};
    return colDefExtras
  }

  if (_.includes(cellRendererDisplayers, dispArgs.displayer)) {
    const crArgs: CellRendererArgs = dispArgs as CellRendererArgs;
    return {
      cellRenderer: getCellRenderer(crArgs)
    }
  }
  return undefined;
}

export function colorMap(mapName:string, histogram:number[]) {
   // https://colorcet.com/gallery.html#isoluminant
   // https://github.com/holoviz/colorcet/tree/main/assets/CET
   // https://github.com/bokeh/bokeh/blob/ed285b11ab196e72336b47bf12f44e1bef5abed3/src/bokeh/models/mappers.py#L304
  function numberToColor(val: number) {
    if (val === 0) {
      return "#ffaaaa";
    } else if (val == 1) {
      return "#aaaaff";
    } else {
      return "#aaffaa";
    }
  }

  function cellStyle(params: CellClassParams) {
    const color = numberToColor(params.value);
    return {
      backgroundColor: color,
    };
  }

  const retProps = {
    cellStyle: cellStyle,
  };
  return retProps
};




export function extractPinnedRows(sdf:DFData, prc:PinnedRowConfig[]) {
  return _.map(
    _.map(prc, 'primary_key_val'), 
    (x) => _.find(sdf, {'index':x}))
}


export function dfToAgrid(tdf: DFWhole, summary_stats_df:SDFT): [ColDef[], unknown[]] {
  const retColumns: ColDef[] = tdf.dfviewer_config.column_config.map(
    (f: ColumnConfig) => {
    const colDef: ColDef = {
      field: f.col_name,
      headerName: f.col_name,
      ...addToColDef(f.displayer_args, summary_stats_df[f.col_name])
    };
    if (f.col_name === 'index') {
      colDef.pinned = 'left';
    }
    return colDef;
  });
  return [retColumns, tdf.data];
}
