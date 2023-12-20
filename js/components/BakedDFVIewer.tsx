import React from 'react';
import { DFViewer } from "./DFViewer";
import { DFWhole } from "./DFWhole";
import { ITooltipParams } from "ag-grid-community";

export function getBakedDFViewer(seriesDf:DFWhole) {
 
    const retFunc = (props: ITooltipParams ) => {
     return (<div> 
            <h1> series_summary </h1>
                <DFViewer df={seriesDf} summaryStatsDf={[]}></DFViewer>
             </div>);
    }
    return retFunc
   }
   