import {
  ValueFormatterFunc,
  ValueFormatterParams
} from 'ag-grid-community';
import {
  DisplayerArgs,
  cellRendererDisplayers,
  FloatDisplayerA,
  IntegerDisplayerA,
  DatetimeLocaleDisplayerA
} from './DFWhole';
import _ from 'lodash';
import { HistogramCell } from './CustomHeader';
import { CellRendererArgs, FormatterArgs } from './DFWhole';

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