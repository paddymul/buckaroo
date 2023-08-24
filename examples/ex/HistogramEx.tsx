import React from 'react';
import { HistogramCell} from '../../js/components/CustomHeader';
//import {tableDf } from '../../js/components/staticData';



export default function Simple() {


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

  const categorical_histo_lt =[
    {'name': 'KTM', 'cat_pop': 0.25},
    {'name': 'Gas Gas', 'cat_pop': 0.12},
    {'name': 'Yamaha', 'cat_pop': 0.08},
    {'name': 'NA', 'NA': 0.2},
    {'name': 'longtail', 'unique': 0.15, 'longtail':.20},


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

  const unique_continuous_scaled =[
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
    {'name': 'unique', 'unique': .296},
]

  const unique_continuous_scaled_50 =[
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
    {'name': 'unique', 'unique': .15},
]

  const start_station_categorical =[{'name': 'Pershing Square N', 'cat_pop': 0.012097203728362184},
 {'name': '8 Ave & W 31 St', 'cat_pop': 0.010968708388814913},
 {'name': 'Lafayette St & E 8 St', 'cat_pop': 0.010579227696404793},
 {'name': 'W 21 St & 6 Ave', 'cat_pop': 0.010213049267643142},
 {'name': 'E 17 St & Broadway', 'cat_pop': 0.009201065246338215},
 {'name': '8 Ave & W 33 St', 'cat_pop': 0.008978029294274301},
 {'name': 'E 43 St & Vanderbilt Ave', 'cat_pop': 0.008385486018641811},
 {'name': 'unique', 'cat_pop': 0.0},
 {'name': 'long_tail', 'cat_pop': 0.9295772303595207},
				    {'name': 'NA', 'cat_pop': 0.0}]

  return <div className="histogram-ex">
    <div className="histogram-wrap">
      <span> Numeric </span>
      <HistogramCell histogram={num_histo}/>
    </div>
    <div className="histogram-wrap">
      <span> Boolean with NA  </span>
      <HistogramCell histogram={bool_histo}/>
    </div>
    <div className="histogram-wrap">
      <span> Categorical unique NA </span>
      <HistogramCell histogram={categorical_histo}/>
    </div>
    <div className="histogram-wrap">
      <span> Categorical_longtail </span>
      <HistogramCell histogram={categorical_histo_lt}/>
    </div>

    <div className="histogram-wrap">
      <span> Categorical All unique </span>
      <HistogramCell histogram={all_unique}/>
    </div>

    <div className="histogram-wrap">
      <span> Categorical Unique with NA  </span>
      <HistogramCell histogram={unique_na}/>
    </div>

    <div className="histogram-wrap">
      <span> Numeric all Unique  </span>
      <HistogramCell histogram={unique_continuous_scaled}/>
    </div>
    <div className="histogram-wrap">
      <span> Numeric 50% unique  </span>
    <HistogramCell histogram={unique_continuous_scaled_50}/>
    </div>
    <div className="histogram-wrap">
      <span> start station categorical  </span>
    <HistogramCell histogram={start_station_categorical}/>
    </div>



  </div>
}
/*

  <!--
    <div className="histogram-wrap">
      <span> unique_continuous </span>
      <HistogramCell histogram={unique_continuous}/>
    </div>
    -->
    */
