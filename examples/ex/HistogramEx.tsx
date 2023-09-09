import React from 'react';
import { HistogramCell} from '../../js/components/CustomHeader';
//import {tableDf } from '../../js/components/staticData';



export default function Simple() {


  const num_histo =[
    {'name': '-406 - -332', 'population':  0},
    {'name': '-332 - -258', 'population':  0},
    {'name': '-258 - -184', 'population':  2},
    {'name': '-184 - -111', 'population': 10},
    {'name': '-111 - -37',  'population': 22},
    {'name': '-37 - 36',    'population': 30},
    {'name': '36 - 109',    'population': 22},
    {'name': '109 - 183',   'population': 10},
    {'name': '183 - 257',   'population':  3},
    {'name': '257 - 331',   'population':  0}]

  const bool_histo =[
    {'name': 'False', 'false': 50},
    {'name': 'True', 'true': 30},
    {'name': 'NA', 'NA': 20}]

  const NA_Only =[
    {'name': 'NA', 'NA': 100}]

  const categorical_histo =[
    {'name': 'KTM', 'cat_pop': 30},
    {'name': 'Gas Gas', 'cat_pop': 15},
    {'name': 'Yamaha', 'cat_pop': 10},
    {'name': 'unique', 'unique': 25},
    {'name': 'NA', 'NA': 20}
  ]

  const categorical_histo_lt =[
    {'name': 'KTM', 'cat_pop': 25},
    {'name': 'Gas Gas', 'cat_pop': 12},
    {'name': 'Yamaha', 'cat_pop': 8},
    {'name': 'NA', 'NA': 20},
    {'name': 'longtail', 'unique': 15, 'longtail':20},
  ]


  const all_unique =[
    {'name': 'unique', 'unique': 100},
  ]

  const unique_na =[
    {'name': 'unique', 'unique': 80},
    {'name': 'NA', 'NA': 20}
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

  const start_station_categorical =[{'name': 'Pershing Square N', 'cat_pop': 1},
				    {'name': '8 Ave & W 31 St', 'cat_pop': 1},
				    {'name': 'Lafayette St & E 8 St', 'cat_pop': 1},
				    {'name': 'W 21 St & 6 Ave', 'cat_pop': 1},
				    {'name': 'E 17 St & Broadway', 'cat_pop': 1},
				    {'name': '8 Ave & W 33 St', 'cat_pop': 1},
				    {'name': 'E 43 St & Vanderbilt Ave', 'cat_pop': 1},
				    {'name': 'unique', 'cat_pop': 0},
				    {'name': 'long_tail', 'cat_pop': 92},
				    {'name': 'NA', 'cat_pop': 0}]

  return <div className="histogram-ex">
    <div className="histogram-wrap">
      <span> Numeric </span>
    <HistogramCell value={{histogram:num_histo}}/>
    </div>
    <div className="histogram-wrap">
      <span> Boolean with NA  </span>
    <HistogramCell value={{histogram:bool_histo}}/>
    </div>
    <div className="histogram-wrap">
      <span>  NA Only  </span>
    <HistogramCell value={{histogram:NA_Only}}/>
    </div>
    <div className="histogram-wrap">
      <span> Categorical unique NA </span>
    <HistogramCell value={{histogram:categorical_histo}} />
    </div>
    <div className="histogram-wrap">
      <span> Categorical_longtail </span>
    <HistogramCell value={{histogram:categorical_histo_lt}} />
    </div>

    <div className="histogram-wrap">
      <span> Categorical All unique </span>
    <HistogramCell value={{histogram:all_unique}}/>
    </div>

    <div className="histogram-wrap">
      <span> Categorical Unique with NA  </span>
    <HistogramCell value={{histogram:unique_na}}/>
    </div>

    <div className="histogram-wrap">
      <span> Numeric all Unique  </span>
    <HistogramCell value={{histogram:unique_continuous_scaled}}/>
    </div>
    <div className="histogram-wrap">
      <span> Numeric 50% unique  </span>
    <HistogramCell value={{histogram:unique_continuous_scaled_50}}/>
    </div>
    <div className="histogram-wrap">
      <span> start station categorical  </span>
    <HistogramCell value={{histogram:start_station_categorical}}/>
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
