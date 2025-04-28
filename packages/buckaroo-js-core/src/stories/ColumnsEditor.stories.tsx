import React, { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { ColumnsEditor } from "../components/ColumnsEditor";
import { Operation, OperationResult } from "../components/DependentTabs";
import { CommandConfigT } from "../components/CommandUtils";
import { DFViewerConfig } from "../components/DFViewerParts/DFWhole";

const bakedArgSpecs = {
  dropcol: [null],
  fillna: [[3, "fillVal", "type", "integer"] as [number, string, "type", "integer"]],
  remove_outliers: [[3, "tail", "type", "float"] as [number, string, "type", "float"]],
  search: [[3, "needle", "type", "string"] as [number, string, "type", "string"]],
  resample: [
    [3, "frequency", "enum", ["daily", "weekly", "monthly"]] as [number, string, "enum", string[]],
    [4, "colMap", "colEnum", ["null", "sum", "mean", "count"]] as [number, string, "colEnum", string[]],
  ],
};

const bakedOperationDefaults = {
  dropcol: [{ symbol: "dropcol" }, { symbol: "df" }, "col"] as Operation,
  fillna: [{ symbol: "fillna" }, { symbol: "df" }, "col", 8] as Operation,
  remove_outliers: [{ symbol: "remove_outliers" }, { symbol: "df" }, "col", 0.02] as Operation,
  search: [{ symbol: "search" }, { symbol: "df" }, "col", "term"] as Operation,
  resample: [{ symbol: "resample" }, { symbol: "df" }, "col", "monthly", {}] as Operation,
};

const bakedCommandConfig: CommandConfigT = {
  argspecs: bakedArgSpecs,
  defaultArgs: bakedOperationDefaults,
};

const bakedOperations: Operation[] = [
  [{ symbol: "dropcol" }, { symbol: "df" }, "col1"],
  [{ symbol: "fillna" }, { symbol: "df" }, "col2", 5],
  [{ symbol: "resample" }, { symbol: "df" }, "month", "monthly", {}],
];

const df_viewer_config: DFViewerConfig = {
  column_config: [
    {
      col_name: "index",
      displayer_args: { displayer: "integer", min_digits: 3, max_digits: 5 },
    },
    {
      col_name: "svg_column",
      displayer_args: { displayer: "SVGDisplayer" },
    },
    {
      col_name: "link_column",
      displayer_args: { displayer: "linkify" },
    },
    {
      col_name: "nanObject",
      displayer_args: { displayer: "integer", min_digits: 3, max_digits: 5 },
      color_map_config: {
        color_rule: "color_map",
        map_name: "BLUE_TO_YELLOW",
        val_column: "tripduration",
      },
    },
  ],
  extra_grid_config: { rowHeight: 105 },
  component_config: { height_fraction: 1 },
  pinned_rows: [],
};

const baseOperationResults: OperationResult = {
  transformed_df: {
    dfviewer_config: {
      pinned_rows: [],
      column_config: [],
    },
    data: [],
  },
  generated_py_code: "default py code",
  transform_error: undefined,
};

const meta = {
  title: "Buckaroo/ColumnsEditor",
  component: ColumnsEditor,
  parameters: {
    layout: "centered",
  },
  tags: ["autodocs"],
} satisfies Meta<typeof ColumnsEditor>;

export default meta;
type Story = StoryObj<typeof meta> | any;

export const Primary: Story = {
  render: () => {
    const [operations, setOperations] = useState<Operation[]>(bakedOperations);
    return (
      <ColumnsEditor
        df_viewer_config={df_viewer_config}
        activeColumn="index"
        operation_result={baseOperationResults}
        command_config={bakedCommandConfig}
        operations={operations}
        setOperations={setOperations}
      />
    );
  },
}; 