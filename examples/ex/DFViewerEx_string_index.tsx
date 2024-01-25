import {DFViewer} from '../../js/components/DFViewerParts/DFViewer';
import { stringIndexDf } from '../../js/baked_data/staticData';
import React, { useState} from 'react';

export default function DFViewerExString() {
    const [activeCol, setActiveCol] = useState('tripduration');
    return <DFViewer df={stringIndexDf.data}
    df_viewer_config={stringIndexDf.dfviewer_config}

    activeCol={activeCol} setActiveCol={setActiveCol} />;
  }
  