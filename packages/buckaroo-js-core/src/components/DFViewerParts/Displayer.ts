import { ValueFormatterFunc, ValueFormatterParams } from "@ag-grid-community/core";
import {
    DisplayerArgs,
    cellRendererDisplayers,
    FloatDisplayerA,
    IntegerDisplayerA,
    DatetimeLocaleDisplayerA,
    StringDisplayerA,
    ObjDisplayerA,
} from "./DFWhole";
import * as _ from "lodash";

import { HistogramCell } from "./HistogramCell";
import { Base64PNGDisplayer, LinkCellRenderer, SVGDisplayer } from "./OtherRenderers";
import { CellRendererArgs, FormatterArgs } from "./DFWhole";
import { getChartCell } from "./ChartCell";

/*
  this code should all be unit tested and in examples. Examples will
  show potential developers how this behaves. Examples should be made
  inside of AG-Grid, and independently.
  */

export const basicIntFormatter = new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 3,
});

export const getStringFormatter = (args: StringDisplayerA) => {
    const stringFormatter = (params: ValueFormatterParams): string => {
        const val = params.value;
        if (val && args.max_length && typeof val === "string") {
            try {
                return val.slice(0, args.max_length);
            } catch (e) {
                console.log("e", e, "val", val);
                return "";
            }
        }
        return val;
    };
    return stringFormatter;
};

const dictDisplayer = (val: Record<string, any>): string => {
    const objBody = _.map(val, (value, key) => `'${key}': ${objDisplayer(value)}`).join(",");
    return `{ ${objBody} }`;
};

export const isValidDate = (possibleDate: any): boolean => {
    if (_.isDate(possibleDate) && isFinite(possibleDate.getTime())) {
        return true;
    }
    return false;
};
const DEFAULT_DATE_FORMAT: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    second: "numeric",
    hour12: false,
};

export const dateDisplayerDefault = (d: Date): string => {
    const fullStr = d.toLocaleDateString("en-CA", DEFAULT_DATE_FORMAT);
    const [dateStr, timeStr] = fullStr.split(",");
    const retVal = `${dateStr} ${timeStr}`;
    return retVal;
};
const objDisplayer = (val: any | any[]): string => {
    if (val === undefined || val === null) {
        return "None";
    } else if (_.isArray(val)) {
        return `[ ${val.map(objDisplayer).join(", ")}]`;
    } else if (_.isBoolean(val)) {
        return boolDisplayer(val);
    } else if (_.isObject(val)) {
        return dictDisplayer(val);
    } else {
        return val.toString();
    }
    return val;
};

export const getObjectFormatter = (fArgs: ObjDisplayerA) => {
    const objFormatter = (params: ValueFormatterParams): string => {
        const val = params.value;
        const fullString = objDisplayer(val);
        if (fArgs.max_length) {
            return fullString.slice(0, fArgs.max_length);
        } else {
            return fullString;
        }
    };
    return objFormatter;
};
export const objFormatter = getObjectFormatter({ displayer: "obj" });

export const boolDisplayer = (val: boolean) => {
    if (val === true) {
        return "True";
    } else if (val === false) {
        return "False";
    }
    return "";
};

export const booleanFormatter = (params: ValueFormatterParams): string => {
    const val = params.value;
    return boolDisplayer(val);
};
const getIntegerFormatter = (hint: IntegerDisplayerA) => {
    const commas = Math.floor(hint.max_digits / 3);
    const totalWidth = commas + hint.max_digits;

    const formatter = new Intl.NumberFormat("en-US");
    const numericFormatter = (params: ValueFormatterParams): string => {
        const val = params.value;
        if (val === null) {
            return "";
        } else if(val === undefined) {
            return ""
        }
        return formatter.format(params.value).padStart(totalWidth, " ");
    };
    return numericFormatter;
};
export const getFloatFormatter = (hint: FloatDisplayerA) => {
    const floatFormatter = new Intl.NumberFormat("en-US", {
        minimumFractionDigits: hint.min_fraction_digits,
        maximumFractionDigits: hint.max_fraction_digits,
    });
    return (params: ValueFormatterParams): string => {
        if (params.value === null || params.value === undefined) {
            return "";
        }

        const res: string = floatFormatter.format(params.value);
        if (!_.includes(res, ".")) {
            const padLength = res.length + hint.max_fraction_digits + 1;
            return res.padEnd(padLength);
        } else {
            const fracPart = res.split(".")[1];
            const padLength = hint.max_fraction_digits - fracPart.length + res.length;
            return res.padEnd(padLength);
        }
    };
};

export const getDatetimeFormatter = (colHint: DatetimeLocaleDisplayerA) => {
    return (params: ValueFormatterParams): string => {
        const val = params.value;
        if (val === null || val === undefined) {
            return "";
        }
        const d = new Date(val);
        if (!isValidDate(d)) {
            return "";
        }
        return d.toLocaleDateString(colHint.locale, colHint.args);
    };
};

export const defaultDatetimeFormatter = (params: ValueFormatterParams): string => {
    const val = params.value;
    if (val === null || val === undefined) {
        return "";
    }
    const d = new Date(val);
    if (!isValidDate(d)) {
        return "";
    }
    return dateDisplayerDefault(d);
};

export function getFormatter(fArgs: FormatterArgs): ValueFormatterFunc<unknown> {
    switch (fArgs.displayer) {
        case "integer":
            return getIntegerFormatter(fArgs);
        case "string":
            return getStringFormatter(fArgs);
        case "datetimeDefault":
            return defaultDatetimeFormatter;
        case "datetimeLocaleString":
            return getDatetimeFormatter(fArgs);
        case "float":
            return getFloatFormatter(fArgs);
        case "boolean":
            return booleanFormatter;
        case "obj":
            return getObjectFormatter(fArgs);
        default:
            return getStringFormatter({ displayer: "string" });
    }
}

/*
{
  cellRenderer: 'agCheckboxCellRenderer',
  cellRendererParams: {   disabled: true}
  }
  */
export function getCellRenderer(crArgs: CellRendererArgs) {
    switch (crArgs.displayer) {
        case "histogram":
            return HistogramCell;
        case "chart":
            return getChartCell(crArgs)
        case "linkify":
            return LinkCellRenderer;
        case "Base64PNGImageDisplayer":
            return Base64PNGDisplayer;
        case "boolean_checkbox":
            return "agCheckboxCellRenderer";
        case "SVGDisplayer":
            return SVGDisplayer;
    }
}

export function getFormatterFromArgs(dispArgs: DisplayerArgs) {
    if (_.includes(cellRendererDisplayers, dispArgs.displayer)) {
        return undefined;
    }
    const fArgs = dispArgs as FormatterArgs;
    return getFormatter(fArgs);
}
