import * as React from "react";
import * as extraComponents from "buckaroo-js-core";


export default function (
    {
        df_meta, df_data_dict, df_display_args,
        buckaroo_state, setBuckaroo_state,
        buckaroo_options,
        command_config,
        operations, setOperations,
        operation_results, style_block }) {
    console.log("extraComponents", extraComponents);
    extraComponents.default.widgetUtils.injectBuckarooCSS(style_block)
    const set_buckaroo_state = setBuckaroo_state;
    const on_operations = setOperations;
    console.log("df_data_dict", df_data_dict);
    console.log("buckaroo_state", buckaroo_state);
    console.log("buckaroo_options", buckaroo_options);
    console.log("df_display_args", df_display_args);
    return (
        <div className="buckaroo_anywidget">
            <extraComponents.default.WidgetDCFCell
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
};
