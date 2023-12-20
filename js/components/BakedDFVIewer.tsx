import React from 'react';
import { DFViewer } from "./DFViewer";
import { EmptyDf } from "./DFWhole";
import { ITooltipParams } from "ag-grid-community";

export function getBakedDFViewer() {
    const retFunc = (props: ITooltipParams ) => {
     return (<div> 
            <h1>paddy asdf</h1>
                <DFViewer df={EmptyDf} summaryStatsDf={[]}></DFViewer>
             </div>);
    }
    return retFunc
   }
   
