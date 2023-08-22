import React from 'react';
import {CategoricalHistogramCell, HistogramCell} from '../../js/components/CustomHeader';
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

  const bool_histo =[
    {'name': 'False', 'false': 0.5},
    {'name': 'True', 'true': 0.3},
    {'name': 'NA', 'NA': 0.2}]

  const categorical_histo =[
    {'name': 'KTM', 'cat_pop': 0.3},
    {'name': 'Gas Gas', 'cat_pop': 0.15},
    {'name': 'Yamaha', 'cat_pop': 0.1},
    {'name': 'unique', 'unique': 0.25},
    {'name': 'NA', 'NA': 0.2}
  ]


  return <div>
    <div className={"pt1 small-bar"}></div>

    <div className={"pt4 small-bar"}></div>
    <div className={"pt5 small-bar"}></div>
    <div className={"pt6 small-bar"}></div>
    <div className={"pt7 small-bar"}></div>
    <div style={{"border":"1px solid green"}}>
      <span> base</span>
      <HistogramCell histogram={hist1}/>
    </div>
    <div style={{"border":"1px solid green"}}>
      <span> num_histo </span>
      <HistogramCell histogram={num_histo}/>
    </div>
    <div style={{"border":"1px solid green"}}>
      <span> bool_histo </span>
      <CategoricalHistogramCell histogram={bool_histo}/>
    </div>
    <div style={{"border":"1px solid green"}}>
      <span> categorical_histo </span>
      <CategoricalHistogramCell histogram={categorical_histo}/>
    </div>

  </div>
}
