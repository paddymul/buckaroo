import React from 'react';
import {HistogramCell} from '../../js/components/CustomHeader';
//import {tableDf } from '../../js/components/staticData';



export default function Simple() {

 const hist1 = [
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
    population: 189000,
  },
];

  return <div>

    <HistogramCell histogram={hist1}/>

  </div>
}
