import React from 'react';
import {HistogramCell} from '../../js/components/CustomHeader';
//import {tableDf } from '../../js/components/staticData';



export default function Simple() {

 const hist1 = [
   { name: '1-10',    population: 5},
   { name: '11-20', population: 3000, },
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

  const num_histo =[
    {'name': '-406   -332', 'population': 0.0006},
    {'name': '-332   -258', 'population': 0.0034},
    {'name': '-258   -184', 'population': 0.0248},
    {'name': '-184   -111', 'population': 0.1002},
    {'name': '-111   -37', 'population': 0.2158},
    {'name': '-37   36', 'population': 0.2966},
    {'name': '36   109', 'population': 0.2246},
    {'name': '109   183', 'population': 0.0994},
    {'name': '183   257', 'population': 0.0312},
    {'name': '257   331', 'population': 0.0034}]
  return <div>
    <div className={"pt1 small-bar"}></div>

    <div className={"pt4 small-bar"}></div>
    <div className={"pt5 small-bar"}></div>
    <div className={"pt6 small-bar"}></div>
    <div style={{"border":"1px solid green"}}>
      <span> base</span>
      <HistogramCell histogram={hist1}/>
    </div>
    <div style={{"border":"1px solid green"}}>
      <span> num_histo </span>
      <HistogramCell histogram={num_histo}/>
    </div>

  </div>
}
