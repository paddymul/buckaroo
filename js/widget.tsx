import * as React from "react";
import { createRender, useModelState } from "@anywidget/react";
import { extraComponents } from "paddy-vite-demo";
import "./widget.css";
import { Operation } from "paddy-vite-demo/dist/components/OperationUtils";
//import { DFWhole, EmptyDf } from "paddy-vite-demo/dist/components/DFViewerParts/DFWhole";
//import { bakedArgSpecs, CommandConfigT } from "paddy-vite-demo/dist/components/CommandUtils";
import { BuckarooOptions, BuckarooState } from "paddy-vite-demo/dist/components/WidgetTypes";
import "paddy-vite-demo/dist/style.css";
//import { OperationResult } from "paddy-vite-demo/dist/components/DependentTabs";
//import { IDisplayArgs } from "paddy-vite-demo/dist/components/DFViewerParts/gridUtils";




const render = createRender(() => {

    const [df_meta, _set_df_meta] = useModelState<any>('df_meta');
    const [df_data_dict, _set_df_data_dict] = useModelState<any>('df_data_dict');
    const [df_display_args, _set_df_display_args] = useModelState<any>('df_display_args')
    const [buckaroo_state, set_buckaroo_state] = useModelState<BuckarooState>('buckaroo_state');
    const [buckaroo_options, _set_buckaroo_options] = useModelState<BuckarooOptions>('buckaroo_options');
    const [command_config, _set_cc] = useModelState<any>('command_config');
    const [operations, on_operations] = useModelState<Operation[]>("operations");
    const [operation_results, _set_or] = useModelState<any>("operation_results");
    console.log("df_data_dict", df_data_dict);
    console.log("buckaroo_state", buckaroo_state);
    console.log("buckaroo_options", buckaroo_options);
    console.log("df_display_args", df_display_args);
	return (
		<div className="buckaroo_anywidget">
		    <extraComponents.WidgetDCFCell
	                df_meta={df_meta}
	                df_data_dict={df_data_dict}
                        df_display_args={df_display_args}
	                        buckaroo_state={buckaroo_state}
				on_buckaroo_state={set_buckaroo_state}
	                        buckaroo_options={buckaroo_options}
				command_config={command_config}
				operations={operations}
				on_operations={on_operations}
				operation_results={operation_results}
			/>
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
