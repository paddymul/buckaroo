import{j as t}from"./jsx-runtime-DiklIkkE.js";import{r as w}from"./index-DRjF_FHU.js";/* empty css                */import{D as N}from"./gridUtils-FdLmYHKG.js";import"./lodash-CGIzQN7T.js";import"./HistogramCell-CR3xZS9E.js";import"./index-Bx0Ph3cE.js";import"./ChartCell-CdGzSEf4.js";import"./tiny-invariant-CopsF_GD.js";import"./main.esm-CraDeAap.js";const j=({df_data:b,df_viewer_config:u,summary_stats_data:v,activeCol:h,setActiveCol:n})=>{if(n===void 0){let[F,D]=w.useState("b")}return t.jsx("div",{style:{height:500,width:800},children:t.jsx(N,{df_data:b,df_viewer_config:u,summary_stats_data:v,activeCol:h,setActiveCol:n})})},O={title:"Buckaroo/DFViewer/DFViewer",component:j,parameters:{layout:"centered"},tags:["autodocs"],argTypes:{}},e={args:{df_data:[{a:20,b:"foo"},{a:30,b:"bar"}],df_viewer_config:{column_config:[{col_name:"a",displayer_args:{displayer:"float",min_fraction_digits:2,max_fraction_digits:8}},{col_name:"a",displayer_args:{displayer:"integer",min_digits:2,max_digits:3}},{col_name:"b",displayer_args:{displayer:"obj"}}],pinned_rows:[]}}},a={args:{df_data:[{index:0,date:"06/11/2021",date2:"06/11/2021",tt:"foo"},{index:1,date:"Nov, 22nd 2021",date2:"22/11/2021",tt:"bar"},{index:2,date:"24th of November, 2021",date2:"24/11/2021",tt:"baz"},{index:3,date:"24th of November, 2021",date2:"24/11/2021"},{index:4,date:"24th of November, 2021",date2:"24/11/2021",tt:9999},{index:5,date:"24th of November, 2021",date2:"24/11/2021",tt:"baz"}],df_viewer_config:{column_config:[{col_name:"index",displayer_args:{displayer:"obj"}},{col_name:"date",displayer_args:{displayer:"string"},tooltip_config:{tooltip_type:"simple",val_column:"tt"}},{col_name:"date2",displayer_args:{displayer:"string"}}],pinned_rows:[]}}},o={args:{df_data:[{index:0,date:"06/11/2021",color:"red"},{index:1,date:"Nov, 22nd 2021",color:"#f8f8a1"},{index:2,date:"24th of November, 2021",color:"teal"},{index:3,date:"24th of November, 2021",color:"#aaa"},{index:4,date:"24th of November, 2021"},{index:5,date:"24th of November, 2021"}],df_viewer_config:{column_config:[{col_name:"index",displayer_args:{displayer:"obj"}},{col_name:"date",displayer_args:{displayer:"string"},color_map_config:{color_rule:"color_from_column",val_column:"color"}}],pinned_rows:[]}}},C=[{lineRed:33,name:"2000-01-01 00:00:00"},{lineRed:33,name:"2001-01-01 00:00:00"},{lineRed:66,name:"unique"},{lineRed:100,name:"end"}],r={args:{df_data:[{index:0,chart1:C}],df_viewer_config:{column_config:[{col_name:"index",displayer_args:{displayer:"obj"}},{col_name:"chart1",displayer_args:{displayer:"chart"}}],pinned_rows:[]}}};var i,d,s;e.parameters={...e.parameters,docs:{...(i=e.parameters)==null?void 0:i.docs,source:{originalSource:`{
  args: {
    df_data: [{
      'a': 20,
      'b': "foo"
    }, {
      'a': 30,
      'b': "bar"
    }],
    df_viewer_config: {
      column_config: [{
        col_name: 'a',
        displayer_args: {
          displayer: 'float',
          min_fraction_digits: 2,
          max_fraction_digits: 8
        }
        //tooltip_config: { tooltip_type: 'summary_series' },
      }, {
        col_name: 'a',
        displayer_args: {
          displayer: 'integer',
          min_digits: 2,
          max_digits: 3
        }
      }, {
        col_name: 'b',
        displayer_args: {
          displayer: 'obj'
        }
      }],
      pinned_rows: []
    }
  }
}`,...(s=(d=e.parameters)==null?void 0:d.docs)==null?void 0:s.source}}};var l,c,_;a.parameters={...a.parameters,docs:{...(l=a.parameters)==null?void 0:l.docs,source:{originalSource:`{
  args: {
    df_data: [{
      index: 0,
      date: '06/11/2021',
      date2: '06/11/2021',
      tt: 'foo'
    }, {
      index: 1,
      date: 'Nov, 22nd 2021',
      date2: '22/11/2021',
      tt: 'bar'
    }, {
      index: 2,
      date: '24th of November, 2021',
      date2: '24/11/2021',
      tt: 'baz'
    }, {
      index: 3,
      date: '24th of November, 2021',
      date2: '24/11/2021'
    }, {
      index: 4,
      date: '24th of November, 2021',
      date2: '24/11/2021',
      tt: 9999
    }, {
      index: 5,
      date: '24th of November, 2021',
      date2: '24/11/2021',
      tt: 'baz'
    }],
    df_viewer_config: {
      column_config: [{
        col_name: 'index',
        displayer_args: {
          'displayer': 'obj'
        }
      }, {
        col_name: 'date',
        displayer_args: {
          'displayer': 'string'
        },
        tooltip_config: {
          'tooltip_type': 'simple',
          'val_column': 'tt'
        }
      }, {
        col_name: 'date2',
        displayer_args: {
          'displayer': 'string'
        }
      }],
      pinned_rows: []
    }
  }
}`,...(_=(c=a.parameters)==null?void 0:c.docs)==null?void 0:_.source}}};var m,p,f;o.parameters={...o.parameters,docs:{...(m=o.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    df_data: [{
      index: 0,
      date: '06/11/2021',
      color: "red"
    }, {
      index: 1,
      date: 'Nov, 22nd 2021',
      color: "#f8f8a1"
    }, {
      index: 2,
      date: '24th of November, 2021',
      color: "teal"
    }, {
      index: 3,
      date: '24th of November, 2021',
      color: "#aaa"
    }, {
      index: 4,
      date: '24th of November, 2021'
    }, {
      index: 5,
      date: '24th of November, 2021'
    }],
    df_viewer_config: {
      column_config: [{
        col_name: 'index',
        displayer_args: {
          'displayer': 'obj'
        }
      }, {
        col_name: 'date',
        displayer_args: {
          'displayer': 'string'
        },
        color_map_config: {
          color_rule: "color_from_column",
          val_column: "color"
        }
      }],
      pinned_rows: []
    }
  }
}`,...(f=(p=o.parameters)==null?void 0:p.docs)==null?void 0:f.source}}};var g,y,x;r.parameters={...r.parameters,docs:{...(g=r.parameters)==null?void 0:g.docs,source:{originalSource:`{
  args: {
    df_data: [{
      index: 0,
      chart1: lineChart
    }],
    df_viewer_config: {
      column_config: [{
        col_name: 'index',
        displayer_args: {
          'displayer': 'obj'
        }
      }, {
        col_name: 'chart1',
        displayer_args: {
          'displayer': 'chart'
        }
      }],
      pinned_rows: []
    }
  }
}`,...(x=(y=r.parameters)==null?void 0:y.docs)==null?void 0:x.source}}};const W=["Primary","Tooltip","ColorFromCol","Chart"];export{r as Chart,o as ColorFromCol,e as Primary,a as Tooltip,W as __namedExportsOrder,O as default};
