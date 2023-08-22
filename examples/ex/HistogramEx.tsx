import React from 'react';
import { HistogramCell} from '../../js/components/CustomHeader';
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

  const all_unique =[
    {'name': 'unique', 'unique': 1},
  ]

  const unique_na =[
    {'name': 'unique', 'unique': 0.8},
    {'name': 'NA', 'NA': 0.2}
  ]

  const unique_continuous =[
    {'name': '-406   -332', 'population': 0.0006},
    {'name': '-332   -258', 'population': 0.0034},
    {'name': '-258   -184', 'population': 0.0248},
    {'name': '-184   -111', 'population': 0.1002},
    {'name': '-111   -37', 'population': 0.2158},
    {'name': '-37   36', 'population': 0.2966},
    {'name': '36   109', 'population': 0.2246},
    {'name': '109   183', 'population': 0.0994},
    {'name': '183   257', 'population': 0.0312},
    {'name': '257   331', 'population': 0.0034},
    {'name': 'unique', 'unique': 1},
]



  return <div>
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
      <HistogramCell histogram={bool_histo}/>
    </div>
    <div style={{"border":"1px solid green"}}>
      <span> categorical_histo </span>
      <HistogramCell histogram={categorical_histo}/>
    </div>

    <div style={{"border":"1px solid green"}}>
      <span> all_unique </span>
      <HistogramCell histogram={all_unique}/>
    </div>

    <div style={{"border":"1px solid green"}}>
      <span> unique_na </span>
      <HistogramCell histogram={unique_na}/>
    </div>

    <div style={{"border":"1px solid green"}}>
      <span> unique_continuous </span>
      <HistogramCell histogram={unique_continuous}/>
    </div>



  </div>
}
