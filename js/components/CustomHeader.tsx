import React from 'react';
import { IHeaderParams } from './BaseHeader';

import { BarChart, Bar, Tooltip,
	 //Legend,
	 //Cell, XAxis, YAxis, CartesianGrid, , ResponsiveContainer,
	   } from 'recharts';


//import { ICellRendererParams } from 'ag-grid-community';

export interface ICustomHeaderParams extends IHeaderParams {
  menuIcon: string;
  histogram?: number[]
}



export const bakedData = [
  {
    name: 'Page A',    population: 4000,
  },
  {
    name: 'Page B',
    population: 3000,
  },
  {
    name: 'Page C',
    population: 2000,
  },
  {
    name: 'Page D',
    population: 2780,
  },
  {
    name: 'Page E',
    population: 1890,
  },
];

const makeData = (histogram: number[]) => {
  const accum = [];
  for (let i = 0; i < histogram.length; i++) {
    accum.push({
      name:`${i+1}/${histogram.length}`,
      population: histogram[i]
    })
  }
  console.log("accum", accum)
  return accum;

}



const formatter = (value:any, name:any, props:any) => {
  console.log("formatter", value, name, props)
  return [value, props.payload.name + " asdfa"]
}

export const HistogramCell  = ({histogram}: {histogram:any}) => {
  const fData = histogram ? makeData(histogram) : bakedData;
  console.log("fData", fData);
  return (<div> 
    <BarChart  width={100} height={30} barGap={1} data={histogram} >
         <defs>
            <pattern id="star" width="10" height="10" patternUnits="userSpaceOnUse">
              <polygon points="0,0 2,5 0,10 5,8 10,10 8,5 10,0 5,2" />
            </pattern>
            <pattern id="stripe" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width="2" height="4" fill="red" />
            </pattern>
    <pattern id="checkers" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">
       <rect  x="0" width="2" height="2" y="0"></rect>
       <rect  x="2" width="2" height="2" y="2"></rect>
    </pattern>
          </defs>
    <Bar dataKey="population" 
                    stroke="#000000"  fill="url(#checkers)" />
    <Tooltip offset={20} formatter={formatter}   labelStyle={{"color":"green"}} allowEscapeViewBox={{ x: true, y: true }} />
    </BarChart>
    </div>
    );
}

export const CategoricalHistogramCell  = ({histogram}: {histogram:any}) => {
  const fData = histogram ? makeData(histogram) : bakedData;
  console.log("fData", fData);
  return (<div> 
    <BarChart  width={100} height={30} barGap={1} data={histogram} >
         <defs>
            <pattern id="star" width="10" height="10" patternUnits="userSpaceOnUse">
              <polygon points="0,0 2,5 0,10 5,8 10,10 8,5 10,0 5,2" />
            </pattern>
            <pattern id="stripe" width="4" height="4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
              <rect width="2" height="4" fill="red" />

            </pattern>
    <pattern id="circles" width="4" height="4" patternUnits="userSpaceOnUse" >
    <circle
	  data-color="outline"  stroke="#FFF"   cx=".5" cy=".5" r="1.5">
    </circle>
    </pattern>


    <pattern id="checkers" x="0" y="0" width="4" height="4" patternUnits="userSpaceOnUse">
       <rect  x="0" width="2" height="2" y="0" ></rect>
       <rect  x="2" width="2" height="2" y="2"></rect>
    </pattern>
          </defs>
    <Bar dataKey="true"  stroke="#000000"  fill="#000" stackId="stack" />
    <Bar dataKey="false" stroke="#000000"  fill="#fff" stackId="stack" />
    <Bar dataKey="cat_pop" stroke="gray"  fill="url(#circles)" stackId="stack" />
    <Bar dataKey="unique"                  fill="url(#stripe)" stackId="stack"/>
    <Bar dataKey="NA"                      fill="url(#checkers)" stackId="stack"/>
    
    <Tooltip offset={20} formatter={formatter} labelStyle={{"color":"green"}}
                         contentStyle={{"color":"red"}}
   allowEscapeViewBox={{ x: true, y: true }} />
    </BarChart>
    </div>
    );
}

