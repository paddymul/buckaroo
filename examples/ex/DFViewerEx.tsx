import {DFViewer} from '../../js/components/DFViewer';
import {summaryDfForTableDf, tableDf } from '../../js/components/staticData';
import React, { useState} from 'react';


export default function Simple() {
    const [activeCol, setActiveCol] = useState('tripduration');
    return <DFViewer df={tableDf} 
            summaryStatsDf={summaryDfForTableDf}
    activeCol={activeCol} setActiveCol={setActiveCol} />;
}
