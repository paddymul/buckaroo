import React, { useMemo, useState } from 'react';
import _ from 'lodash';
import { OperationResult } from './DependentTabs';
import { ColumnsEditor } from './ColumnsEditor';

import { DFData } from './DFViewerParts/DFWhole';
import { StatusBar } from './StatusBar';
import { BuckarooState } from './WidgetTypes';
import { BuckarooOptions } from './WidgetTypes';
import { DFMeta } from './WidgetTypes';
import { CommandConfigT } from './CommandUtils';
import { Operation } from './OperationUtils';
import {
  getDs,
  getPayloadKey,
  IDisplayArgs,
  PayloadArgs,
  PayloadResponse,
} from './DFViewerParts/gridUtils';
import {
  DatasourceOrRaw,
  DFViewerInfinite,
} from './DFViewerParts/DFViewerInfinite';
import { IDatasource } from '@ag-grid-community/core';

export const getDataWrapper = (
  data_key: string,
  df_data_dict: Record<string, DFData>,
  ds: IDatasource
): DatasourceOrRaw => {
  if (data_key === 'main') {
    return {
      data_type: 'DataSource',
      datasource: ds,
      length: 50, //hack
    };
  } else {
    return {
      data_type: 'Raw',
      data: df_data_dict[data_key],
      length: df_data_dict[data_key].length,
    };
  }
};

export function BuckarooInfiniteWidget({
  payload_args,
  on_payload_args,
  payload_response,
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
  payload_args: PayloadArgs;
  on_payload_args: (pa: PayloadArgs) => void;
  payload_response: PayloadResponse;
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
  const [mainDs, respCache] = useMemo(() => getDs(on_payload_args), []);
  const cacheKey = getPayloadKey(payload_response.key);
  console.log('setting respCache', cacheKey, payload_response);
  respCache[cacheKey] = payload_response;

  const [activeCol, setActiveCol] = useState('stoptime');

  const cDisp = df_display_args[buckaroo_state.df_display];
  if (cDisp === undefined) {
    console.log(
      'cDisp undefined',
      buckaroo_state.df_display,
      buckaroo_options.df_display
    );
  }

  const data_wrapper = getDataWrapper(cDisp.data_key, df_data_dict, mainDs);
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
        <DFViewerInfinite
          data_wrapper={data_wrapper}
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
