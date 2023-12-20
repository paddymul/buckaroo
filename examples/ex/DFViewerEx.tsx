import {DFViewer} from '../../js/components/DFViewerParts/DFViewer';
import {summaryDfForTableDf, tableDf } from '../../js/baked_data/staticData';
import React, { useState} from 'react';


export default function Simple() {
    const [activeCol, setActiveCol] = useState('tripduration');
    return <DFViewer df={tableDf} 
            summaryStatsDf={summaryDfForTableDf}
    activeCol={activeCol} setActiveCol={setActiveCol} />;
}
