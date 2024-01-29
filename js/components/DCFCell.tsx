import React, { useState, Dispatch, SetStateAction } from 'react';
import _ from 'lodash';
import { OperationResult, baseOperationResults } from './DependentTabs';
import { ColumnsEditor, WidgetConfig } from './ColumnsEditor';
import {
  dfviewer_config_no_pinned,
  summaryDfForTableDf,
  tableDf,
} from '../baked_data/staticData';
import { DFData, DFViewerConfig } from './DFViewerParts/DFWhole';
import { DFViewer } from './DFViewerParts/DFViewer';
import { StatusBar } from './StatusBar';
import { BuckarooState } from './WidgetTypes';
import { BuckarooOptions } from './WidgetTypes';
import { DFMeta } from './WidgetTypes';
import { CommandConfigT } from './CommandUtils';
import { bakedCommandConfig } from './bakedOperationDefaults';
import { Operation, bakedOperations } from './OperationUtils';

export type CommandConfigSetterT = (
  setter: Dispatch<SetStateAction<CommandConfigT>>
) => void;

/*
  Widget DCFCell is meant to be used with callback functions and passed values, not explicit http calls

  TODO:add height settings to dfConfig rather than hardcoded.
 */
export interface IDisplayArgs {
  data_key: string;
  df_viewer_config: DFViewerConfig;
  summary_stats_key: string;
}
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
  //  df_dict: Record<string, DFWhole>;
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
  const widgetConfig: WidgetConfig = {
    showCommands: buckaroo_state.show_commands ? true : false,
  };

  const cDisp = df_display_args[buckaroo_state.df_display];
  if (cDisp === undefined) {
    //  console.log("cDisp undefined", buckaroo_state.df_display, buckaroo_options.df_display)
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
        style={{ height: '450px', overflow: 'hidden' }}
      >
        <StatusBar
          dfMeta={df_meta}
          buckarooState={buckaroo_state}
          setBuckarooState={on_buckaroo_state}
          buckarooOptions={buckaroo_options}
        />
        <DFViewer
          df={dfData}
          df_viewer_config={cDisp.df_viewer_config}
          summary_stats_data={summaryStatsData}
          activeCol={activeCol}
          setActiveCol={setActiveCol}
        />
      </div>
      {widgetConfig.showCommands ? (
        <ColumnsEditor
          df_viewer_config={cDisp.df_viewer_config}
          activeColumn={activeCol}
          operations={operations}
          setOperations={on_operations}
          operationResult={operation_results}
          commandConfig={commandConfig}
          widgetConfig={widgetConfig}
        />
      ) : (
        <span></span>
      )}
    </div>
  );
}

export function WidgetDCFCellExample() {
  const dfm: DFMeta = {
    columns: 5,
    rows_shown: 20,
    total_rows: 877,
  };

  const [bState, setBState] = useState<BuckarooState>({
    auto_clean: '',
    sampled: false,
    show_commands: false,
    df_display: 'main',
    post_processing: '',
    search_string: '',
  });

  const bOptions: BuckarooOptions = {
    auto_clean: ['', 'aggressive', 'conservative'],
    df_display: ['main', 'no_pinned_nonexistent_summary', 'no_pinned'],
    sampled: ['random'],
    post_processing: ['', 'foo', 'bar'],
    show_commands: ['on'],
    //    'summary_stats' : ['full', 'all', 'typing_stats']
  };

  const [operations, setOperations] = useState<Operation[]>(bakedOperations);

  const bakedDfDisplay: Record<string, IDisplayArgs> = {
    main: {
      data_key: 'main',
      df_viewer_config: tableDf.dfviewer_config,
      summary_stats_key: 'all',
    },
    no_pinned: {
      data_key: 'main',
      df_viewer_config: dfviewer_config_no_pinned,
      summary_stats_key: 'all',
    },
    no_pinned_nonexistent_summary: {
      data_key: 'main',
      df_viewer_config: dfviewer_config_no_pinned,
      summary_stats_key: 'nonexistent-key',
    },
  };

  return (
    <WidgetDCFCell
      df_meta={dfm}
      df_display_args={bakedDfDisplay}
      df_data_dict={{ main: tableDf.data, all: summaryDfForTableDf }}
      buckaroo_options={bOptions}
      buckaroo_state={bState}
      on_buckaroo_state={setBState}
      commandConfig={bakedCommandConfig}
      operations={operations}
      on_operations={setOperations}
      operation_results={baseOperationResults}
    />
  );
}
