import React, { useState, Dispatch, SetStateAction } from 'react';
import _ from 'lodash';
import { OperationResult, baseOperationResults } from './DependentTabs';
import { ColumnsEditor, WidgetConfig } from './ColumnsEditor';
import { summaryDfForTableDf, tableDf } from '../baked_data/staticData';
import { DFWhole } from './DFViewerParts/DFWhole';
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
export function WidgetDCFCell({
  df_dict,
  df_meta,
  operations,
  on_operations,
  operation_results,
  commandConfig,
  buckaroo_state,
  on_buckaroo_state,
  buckaroo_options,
}: {
  df_dict: Record<string, DFWhole>;
  df_meta: DFMeta;
  operations: Operation[];
  on_operations: (ops: Operation[]) => void;
  operation_results: OperationResult;
  commandConfig: CommandConfigT;
  buckaroo_state: BuckarooState;
  on_buckaroo_state: React.Dispatch<React.SetStateAction<BuckarooState>>;
  buckaroo_options: BuckarooOptions;
}) {
  console.log("df_dict", df_dict);
  debugger;
  const [activeCol, setActiveCol] = useState('stoptime');
  const widgetConfig: WidgetConfig = {
    showCommands: buckaroo_state.show_commands ? true : false,
  };

  const dfToDisplay = df_dict[buckaroo_state.summary_stats || 'main'];
  const summaryStatsData = df_dict['all'].data;

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
          df={dfToDisplay}
          summaryStatsDf={summaryStatsData}
          activeCol={activeCol}
          setActiveCol={setActiveCol}
        />
      </div>
      {widgetConfig.showCommands ? (
        <ColumnsEditor
          df={df_dict['main']}
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
    auto_clean: 'conservative',
    reorderd_columns: false,
    sampled: false,
    show_commands: false,
    summary_stats: false,
    search_string: '',
  });

  const bOptions: BuckarooOptions = {
    auto_clean: ['aggressive', 'conservative'],
    reorderd_columns: [],
    sampled: ['random'],
    show_commands: ['on'],
    //    'summary_stats' : ['full', 'all', 'typing_stats']
    summary_stats: ['all'],
  };
  const wholeAllSummaryDF: DFWhole = {
    data: summaryDfForTableDf,
    dfviewer_config: {
      column_config: [], // pull in all columns
      pinned_rows: [],
    },
  };

  const [operations, setOperations] = useState<Operation[]>(bakedOperations);
  return (
    <WidgetDCFCell
      df_meta={dfm}
    
      df_dict={{ main: tableDf, all: wholeAllSummaryDF }}


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
