import * as React from "react";
import { createRender, useModelState } from "@anywidget/react";
import { extraComponents } from "paddy-vite-demo";
import "./widget.css";
import { Operation } from "paddy-vite-demo/dist/components/OperationUtils";
//import { DFWhole, EmptyDf } from "paddy-vite-demo/dist/components/DFViewerParts/DFWhole";
//import { bakedArgSpecs, CommandConfigT } from "paddy-vite-demo/dist/components/CommandUtils";
import { BuckarooState } from "paddy-vite-demo/dist/components/WidgetTypes";
import "paddy-vite-demo/dist/style.css";
//import { OperationResult } from "paddy-vite-demo/dist/components/DependentTabs";
//import { IDisplayArgs } from "paddy-vite-demo/dist/components/DFViewerParts/gridUtils";

export const tableDf = {
	data: [],
	dfviewer_config: {
		column_config: [
			{
				col_name: 'index',
				displayer_args: { displayer: 'integer', min_digits: 3, max_digits: 5 },
			},
			{
				col_name: 'svg_column',
				displayer_args: { displayer: 'SVGDisplayer' },
			},
			{
				col_name: 'link_column',
				displayer_args: { displayer: 'linkify' },
			},
			{
				col_name: 'nanObject',
				displayer_args: { displayer: 'integer', min_digits: 3, max_digits: 5 },
				color_map_config: {
					color_rule: 'color_map',
					//map_name: 'DIVERGING_RED_WHITE_BLUE',
					map_name: 'BLUE_TO_YELLOW',
					val_column: 'tripduration',
				},
			},
			{
				col_name: 'nanFloat',
				displayer_args: {
					displayer: 'float',
					min_fraction_digits: 2,
					max_fraction_digits: 8,
				},
				tooltip_config: { tooltip_type: 'summary_series' },
			},
			{ col_name: 'end station name', displayer_args: { displayer: 'obj' } },
			{
				col_name: 'tripduration',
				displayer_args: { displayer: 'integer', min_digits: 1, max_digits: 5 },
				color_map_config: {
					color_rule: 'color_map',
					map_name: 'BLUE_TO_YELLOW',
				},
			},
			{
				col_name: 'start station name',
				displayer_args: { displayer: 'obj' },
				color_map_config: {
					color_rule: 'color_not_null',
					conditional_color: 'red',
					exist_column: 'nanFloat',
				},
			},
			{
				col_name: 'floatCol',
				displayer_args: {
					displayer: 'float',
					min_fraction_digits: 1,
					max_fraction_digits: 3,
				},
			},
			{
				col_name: 'nanNumeric',
				displayer_args: { displayer: 'integer', min_digits: 3, max_digits: 5 },
				tooltip_config: {
					tooltip_type: 'simple',
					val_column: 'start station name',
				},
			},
			{
				col_name: 'img_',
				displayer_args: { displayer: 'Base64PNGImageDisplayer' },
				ag_grid_specs: { width: 150 },
			},
		],
		extra_grid_config: { rowHeight: 105 },
		component_config: { height_fraction: 1 },
		pinned_rows: [
			//      { primary_key_val: 'dtype', displayer_args: { displayer: 'obj' } },
			//      {        primary_key_val: 'histogram',        displayer_args: { displayer: 'histogram' },      },
		],
	},
};
export const baseOperationResults: extraComponents.OperationResult = {
	transformed_df: [],
	generated_py_code: 'default py code',
};
export const sym = (symbolName: string) => {
	return { symbol: symbolName };
};

//export const symDf: SymbolDf = {
export const symDf = {
	symbol: 'df',
};

const bakedDfDisplay: Record<string, extraComponents.IDisplayArgs> = {
	main: {
		data_key: 'main',
		df_viewer_config: tableDf.dfviewer_config,
		summary_stats_key: 'all'
	}
};


//const ArgNames = ['Idx', 'label', 'specName', 'extraSpecArgs'];
//export const bakedOperations: Operation[] = [

export const bakedOperations = [
	[sym('dropcol'), symDf, 'col1'],
	[sym('fillna'), symDf, 'col2', 5],
	[sym('resample'), symDf, 'month', 'monthly', {}],
];

//export const bakedOperationDefaults: OperationDefaultArgs = {
export const bakedOperationDefaults = {
	dropcol: [sym('dropcol'), symDf, 'col'],
	fillna: [sym('fillna'), symDf, 'col', 8],
	remove_outliers: [sym('remove_outliers'), symDf, 'col', 0.02],
	search: [sym('search'), symDf, 'col', 'term'],
	resample: [sym('resample'), symDf, 'col', 'monthly', {}],
};

//export const bakedCommandConfig: CommandConfigT = {
export const bakedCommandConfig = {
	argspecs: extraComponents.CommandUtils.bakedArgSpecs,
	defaultArgs: bakedOperationDefaults,
};


const render = createRender(() => {
	const [value, setValue] = useModelState<number>("value");
	const [operations, on_operations] = useModelState<Operation[]>("operations");
	const [bState, _setBState] = useModelState<BuckarooState>('buckaroo_state');
	const setBState2 = (foo: any) => { console.log(foo) };
	return (
		<div className="buckaroo_anywidget">
			<extraComponents.WidgetDCFCell
				df_meta={
					{
						'columns': 5,
						'rows_shown': 20,
						'total_rows': 877,
						'filtered_rows': 5,
					}
				}

	    df_data_dict={{'main':[], 'empty':[]}}
				df_display_args={bakedDfDisplay}

				buckaroo_state={bState}
				on_buckaroo_state={setBState2}

				buckaroo_options={{
					auto_clean: ['', 'aggressive', 'conservative'],
					df_display: ['main', 'realSummary', 'no_pinned'],
					sampled: ['random'],
					post_processing: ['', 'foo', 'bar'],
					show_commands: ['on']
				}}
				commandConfig={bakedCommandConfig}
				operations={operations}
				on_operations={on_operations}
				operation_results={baseOperationResults}
			/>
			<button onClick={() => setValue(value + 1)}>
				count is {value}
			</button>
		</div>
	);
});

export default { render };
/*
	buckaroo_state={{
				auto_clean: '',
				sampled: false,
				show_commands: false,
				df_display: 'main',
				post_processing: '',
				quick_command_args: {}
			}}*/
