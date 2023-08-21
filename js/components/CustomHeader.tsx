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


// interface CellStyle {
//   [cssProperty: string]: string | number;
// }


export const HistogramCell  = ({histogram}: {histogram:any}) => {
  const fData = histogram ? makeData(histogram) : bakedData;
  console.log("fData", fData);
  return (<div> 
        <BarChart  width={50} height={20} data={histogram}>
          <Bar dataKey="population" fill="#8884d8" />
    <Tooltip offset={20} allowEscapeViewBox={{ x: true, y: true }} />
    </BarChart>
    </div>
    );
}

