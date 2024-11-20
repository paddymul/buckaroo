import * as React from "react";
import * as  extraComponents from "buckaroo-js-core";


export default function (
    {
        df_data, df_viewer_config,
        summary_stats_data, style_block
    }) {
    extraComponents.default.widgetUtils.injectBuckarooCSS(style_block)
    console.log("df_data", df_data);

    return (
        <div className="buckaroo_anywidget">
            <extraComponents.default.DFViewer
                df_data={df_data}
                df_viewer_config={df_viewer_config}
                summary_stats_data={summary_stats_data}
            />
        </div>
    );
};
