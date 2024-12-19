import * as React from "react";
import { createRender, useModelState } from "@anywidget/react";
import srt from "buckaroo-js-core";
import "./widget.css";
import "../packages/buckaroo-js-core/dist/style.css"
const unused = () => {
    	const [value, setValue] = useModelState<number>("value");
	return (
		<div className="anyw2_react">
			<button onClick={() => setValue(value + 1)}>
				count is {value}
			</button>
		</div>
	);
}
const render2 = createRender(() => {
    console.log("old render 17");
    return <srt.Counter />
});

const realSummaryConfig = {
	pinned_rows: [
	    { primary_key_val: 'dtype', displayer_args: { displayer: 'obj' } },
	    {
		primary_key_val: 'min',
		displayer_args: {
		    displayer: 'float',
		    min_fraction_digits: 3,
		    max_fraction_digits: 3,
		},
	    },
	    {
		primary_key_val: 'mean',
		displayer_args: {
		    displayer: 'float',
		    min_fraction_digits: 3,
		    max_fraction_digits: 3,
		},
	    },
	    {
		primary_key_val: 'max',
		displayer_args: {
		    displayer: 'float',
		    min_fraction_digits: 3,
		    max_fraction_digits: 3,
		},
	    },
	    {
		primary_key_val: 'unique_count',
		displayer_args: {
		    displayer: 'float',
		    min_fraction_digits: 0,
		    max_fraction_digits: 0,
		},
	    },
	    {
		primary_key_val: 'distinct_count',
		displayer_args: {
		    displayer: 'float',
		    min_fraction_digits: 0,
		    max_fraction_digits: 0,
		},
	    },
	    {
		primary_key_val: 'empty_count',
		displayer_args: {
		    displayer: 'float',
		    min_fraction_digits: 0,
		    max_fraction_digits: 0,
		},
	    },
	],
	column_config: [
	    {
		col_name: 'index',
		displayer_args: { displayer: 'string' },
		ag_grid_specs: { minWidth: 150, pinned: 'left' },
	    },
	    { col_name: 'int_col', displayer_args: { displayer: 'obj' } },
	    { col_name: 'float_col', displayer_args: { displayer: 'obj' } },
	    { col_name: 'str_col', displayer_args: { displayer: 'obj' } },
	],
    };

 const realSummaryTableData = [
	{ index: 'dtype', int_col: 'int64', float_col: 'float64', str_col: 'object' },
	{ index: 'min', int_col: 1, float_col: 1.4285714286 },
	{ index: 'max', int_col: 49, float_col: 41.4285714286, str_col: null },
	{ index: 'mean', int_col: 24.75, float_col: 22.4714285714 },
	{ index: 'unique_count', int_col: 4, float_col: 0, str_col: 0 },
	{ index: 'empty_count', int_col: 0, float_col: 0, str_col: 0 },
	{ index: 'distinct_count', int_col: 49, float_col: 29, str_col: 1 },
    ];


const ex_df_data = [
  {
    "index": 0,
    "int_col": 111111,
    "b": 111111
  },
  {
    "index": 1,
    "int_col": 77777,
    "b": 555555
  },
  {
    "index": 2,
    "int_col": 777777,
    "b": 0
  },
  {
    "index": 3,
    "int_col": 1000000,
    "b": 28123
  },
  {
    "index": 4,
    "int_col": 2111111,
    "b": 482388
  },
  {
    "index": 5,
    "int_col": 1235999,
    "b": 5666
  }
]


const renderDFV = createRender(() => {

    const [df_data, _set_df_meta] = useModelState('df_data');
    const [df_viewer_config, _set_dfvc] = useModelState('df_viewer_config');
    const [summary_stats_data, _set_ssd] = useModelState('summary_stats_data');
    console.log("df_data", df_data);
    console.log("df_viewer_config", df_viewer_config);
    console.log("summary_stats_data", summary_stats_data);
    /*
      
	                df_data={df_data}
					df_viewer_config={df_viewer_config}
					summary_stats_data={summary_stats_data}
    */

	return (
		<div className="buckaroo_anywidget">
 		    <srt.DFViewer
			df_data={df_data}
			df_viewer_config={df_viewer_config}
            summary_stats_data={summary_stats_data}
					/>
 		</div>
 	);
 });

const renderBaked = createRender(() => {
	return (
		<div className="buckaroo_anywidget">
 		    <srt.DFViewer
			df_data={realSummaryTableData}
			df_viewer_config={realSummaryConfig}
                        summary_stats_data={[]}
		/>
 		</div>
 	);
});

/*
export function createRender(Widget) {
	return ({ el, model, experimental }) => {
		let root = ReactDOM.createRoot(el);
		root.render(
			React.createElement(
				React.StrictMode,
				null,
				React.createElement(
					RenderContext.Provider,
					{ value: { model, experimental } },
					React.createElement(Widget),
				),
			),
		);
		return () => root.unmount();
	};
}

*/
const render = ({ el, model, experimental }) => {
    console.log("model", model);
    renderBaked({el, model, experimental});
}

export default { render };
