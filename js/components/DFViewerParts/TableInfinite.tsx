'use strict';
import React, { useMemo, useState } from 'react';

import { winners } from '../../baked_data/olympic-winners';
import {
  getDs,
  getPayloadKey,
  PayloadArgs,
  PayloadResponse,
  sourceName,
} from './gridUtils';
import { InfiniteViewer } from './InfiniteViewerImpl';
import { Operation } from '../OperationUtils';
import _ from 'lodash';

const data: [string, Operation[]][] = [
  ['Swimming', [[{ symbol: 'foo' }, { symbol: 'df' }, 'green']]],
  ['Gymnastics', [[{ symbol: 'bar' }, { symbol: 'df' }, 'green', 'purple']]],
  ['Tennis', []],
  ['Speed Skating', []],
];

const MySelect = ({
  selectedCategory,
  setSelectedCategory,
}: {
  selectedCategory: string;
  setSelectedCategory: any;
}) => {
  const handleCategoryChange = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    setSelectedCategory(event.target.value);
  };
  return (
    <div>
      <label>
        Category:
        <select value={selectedCategory} onChange={handleCategoryChange}>
          {data.map(([category]) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
};

function addSequentialIndex(list: Record<string, any>[]) {
  return _.map(list, (item, index) => ({
    ...item,
    idx: index + 1, // Adding 1 to start the index from 1
  }));
}

function filterBySport(list: any[], sport: string): any[] {
  return _.filter(list, { sport: sport });
}

const getDataset = (sportName: string) => {
  return addSequentialIndex(filterBySport(winners, sportName));
};

export const InfiniteWrapper = ({
  payloadArgs,
  on_payloadArgs,
  payloadResponse,
  operations,
}: {
  payloadArgs: PayloadArgs;
  on_payloadArgs: (pa: PayloadArgs) => void;
  payloadResponse: PayloadResponse;
  operations: Operation[];
}) => {
  //@ts-ignore
  const key = getPayloadKey(payloadResponse.key, undefined);
  const [ds, respCache] = useMemo(() => {
    console.log("recreating ds") 
    return getDs(on_payloadArgs)
  }, []);
  respCache.put(key, payloadResponse);
  console.log(`found ${payloadResponse.data.length} rows for `, key);
  return <InfiniteViewer dataSource={ds} operations={operations} />;
};

export const InfiniteEx = () => {
  // this is supposed to simulate the IPYwidgets backend
  const [selectedSport, setSelectedSport] = useState<string>('Tennis');
  const initialPA: PayloadArgs = { sourceName: selectedSport, start: 0, end: 100 };
  const [paState, setPaState] = useState<PayloadArgs>(initialPA);

  const paToResp = (pa: PayloadArgs): PayloadResponse => {
    return {
//      data: getDataset(pa.sourceName).slice(pa.start, pa.end),
      data: getDataset(selectedSport).slice(pa.start, pa.end),

      key: pa,
    };
  };
  const resp: PayloadResponse = paToResp(paState);
  return (
    <div>
      <MySelect
        selectedCategory={selectedSport}
        setSelectedCategory={setSelectedSport}
      />
      <InfiniteWrapper
        payloadArgs={paState}
        on_payloadArgs={setPaState}
        payloadResponse={resp}
        operations={[[{ symbol: 'sport' }, { symbol: 'df' }, selectedSport]]}
      />
    </div>
  );
};
