import {DFViewer} from '../../js/components/DFViewerParts/DFViewer';
import { stringIndexDf } from '../../js/baked_data/staticData';
import React, { useState} from 'react';


export default function Simple() {
    const [activeCol, setActiveCol] = useState('tripduration');
    return <DFViewer df={stringIndexDf} activeCol={activeCol} setActiveCol={setActiveCol} />;
}
