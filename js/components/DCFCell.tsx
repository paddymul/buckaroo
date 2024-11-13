import React, { useState } from 'react';
import _ from 'lodash';
import { OperationResult } from './DependentTabs';
import { ColumnsEditor } from './ColumnsEditor';

import { DFData } from './DFViewerParts/DFWhole';
import { DFViewer } from './DFViewerParts/DFViewer';
import { StatusBar } from './StatusBar';
import { BuckarooState } from './WidgetTypes';
import { BuckarooOptions } from './WidgetTypes';
import { DFMeta } from './WidgetTypes';
import { CommandConfigT } from './CommandUtils';
import { Operation } from './OperationUtils';
import { IDisplayArgs } from './DFViewerParts/gridUtils';

export function WidgetDCFCell({
  df_data_dict,
  df_display_args,
  df_meta,
  operations,
  on_operations,
  operation_results,
  commandConfig,
  buckaroo_state,
  on_buckaroo_state,
  buckaroo_options,
}: {
  df_meta: DFMeta;
  df_data_dict: Record<string, DFData>;
  df_display_args: Record<string, IDisplayArgs>;
  operations: Operation[];
  on_operations: (ops: Operation[]) => void;
  operation_results: OperationResult;
  commandConfig: CommandConfigT;
  buckaroo_state: BuckarooState;
  on_buckaroo_state: React.Dispatch<React.SetStateAction<BuckarooState>>;
  buckaroo_options: BuckarooOptions;
}) {
  const [activeCol, setActiveCol] = useState('stoptime');

  const cDisp = df_display_args[buckaroo_state.df_display];
  if (cDisp === undefined) {
    console.log(
      'cDisp undefined',
      buckaroo_state.df_display,
      buckaroo_options.df_display
    );
  } else {
    //  console.log("cDisp", cDisp);
  }
  const dfData = df_data_dict[cDisp.data_key];
  //console.log("dfData", dfData);
  const summaryStatsData = df_data_dict[cDisp.summary_stats_key];

  return (
    <div
      className="dcf-root flex flex-col"
      style={{ width: '100%', height: '100%' }}
    >
      <div
        className="orig-df flex flex-row"
        style={{
          // height: '450px',
          overflow: 'hidden',
        }}
      >
        <StatusBar
          dfMeta={df_meta}
          buckarooState={buckaroo_state}
          setBuckarooState={on_buckaroo_state}
          buckarooOptions={buckaroo_options}
        />
        <DFViewer
          df_data={dfData}
          df_viewer_config={cDisp.df_viewer_config}
          summary_stats_data={summaryStatsData}
          activeCol={activeCol}
          setActiveCol={setActiveCol}
        />
      </div>
      {buckaroo_state.show_commands ? (
        <ColumnsEditor
          df_viewer_config={cDisp.df_viewer_config}
          activeColumn={activeCol}
          operations={operations}
          setOperations={on_operations}
          operationResult={operation_results}
          commandConfig={commandConfig}
        />
      ) : (
        <span></span>
      )}
    </div>
  );
}
