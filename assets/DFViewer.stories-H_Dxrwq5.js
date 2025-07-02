import{j as t}from"./jsx-runtime-DiklIkkE.js";import{r as w}from"./index-DRjF_FHU.js";/* empty css                */import{D as j}from"./gridUtils-D7KU2uMb.js";import"./lodash-CGIzQN7T.js";import"./HistogramCell-CBujXJtL.js";import"./index-Bx0Ph3cE.js";import"./ChartCell-CdGzSEf4.js";import"./tiny-invariant-CopsF_GD.js";import"./main.esm-CraDeAap.js";const C=({df_data:b,df_viewer_config:u,summary_stats_data:v,activeCol:N,setActiveCol:d})=>{if(d===void 0){let[R,S]=w.useState("b")}return t.jsx("div",{style:{height:500,width:800},children:t.jsx(j,{df_data:b,df_viewer_config:u,summary_stats_data:v,activeCol:N,setActiveCol:d})})},G={title:"Buckaroo/DFViewer/DFViewer",component:C,parameters:{layout:"centered"},tags:["autodocs"],argTypes:{}},F={col_name:"index",header_name:"index",displayer_args:{displayer:"string"}},o=[F],e={args:{df_data:[{a:20,b:"foo"},{a:30,b:"bar"}],df_viewer_config:{column_config:[{col_name:"a",header_name:"a1",displayer_args:{displayer:"float",min_fraction_digits:2,max_fraction_digits:8}},{col_name:"a",header_name:"a2",displayer_args:{displayer:"integer",min_digits:2,max_digits:3}},{col_name:"b",header_name:"b",displayer_args:{displayer:"obj"}}],pinned_rows:[],left_col_configs:o}}},a={args:{df_data:[{index:0,date:"06/11/2021",date2:"06/11/2021",tt:"foo"},{index:1,date:"Nov, 22nd 2021",date2:"22/11/2021",tt:"bar"},{index:2,date:"24th of November, 2021",date2:"24/11/2021",tt:"baz"},{index:3,date:"24th of November, 2021",date2:"24/11/2021"},{index:4,date:"24th of November, 2021",date2:"24/11/2021",tt:9999},{index:5,date:"24th of November, 2021",date2:"24/11/2021",tt:"baz"}],df_viewer_config:{column_config:[{col_name:"index",header_name:"index",displayer_args:{displayer:"obj"}},{col_name:"date",header_name:"date",displayer_args:{displayer:"string"},tooltip_config:{tooltip_type:"simple",val_column:"tt"}},{col_name:"date2",header_name:"date2",displayer_args:{displayer:"string"}}],pinned_rows:[],left_col_configs:o}}},n={args:{df_data:[{index:0,date:"06/11/2021",color:"red"},{index:1,date:"Nov, 22nd 2021",color:"#f8f8a1"},{index:2,date:"24th of November, 2021",color:"teal"},{index:3,date:"24th of November, 2021",color:"#aaa"},{index:4,date:"24th of November, 2021"},{index:5,date:"24th of November, 2021"}],df_viewer_config:{column_config:[{col_name:"index",header_name:"index",displayer_args:{displayer:"obj"}},{col_name:"date",header_name:"date",displayer_args:{displayer:"string"},color_map_config:{color_rule:"color_from_column",val_column:"color"}}],pinned_rows:[],left_col_configs:o}}},D=[{lineRed:33,name:"2000-01-01 00:00:00"},{lineRed:33,name:"2001-01-01 00:00:00"},{lineRed:66,name:"unique"},{lineRed:100,name:"end"}],r={args:{df_data:[{index:0,chart1:D}],df_viewer_config:{column_config:[{col_name:"index",header_name:"index",displayer_args:{displayer:"obj"}},{col_name:"chart1",header_name:"chart1",displayer_args:{displayer:"chart"}}],pinned_rows:[],left_col_configs:o}}};var i,s,_;e.parameters={...e.parameters,docs:{...(i=e.parameters)==null?void 0:i.docs,source:{originalSource:`{
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
        header_name: 'a1',
        displayer_args: {
          displayer: 'float',
          min_fraction_digits: 2,
          max_fraction_digits: 8
        }
        //tooltip_config: { tooltip_type: 'summary_series' },
      }, {
        col_name: 'a',
        header_name: 'a2',
        displayer_args: {
          displayer: 'integer',
          min_digits: 2,
          max_digits: 3
        }
      }, {
        col_name: 'b',
        header_name: 'b',
        displayer_args: {
          displayer: 'obj'
        }
      }],
      pinned_rows: [],
      left_col_configs
    }
  }
}`,...(_=(s=e.parameters)==null?void 0:s.docs)==null?void 0:_.source}}};var l,c,m;a.parameters={...a.parameters,docs:{...(l=a.parameters)==null?void 0:l.docs,source:{originalSource:`{
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
        header_name: 'index',
        displayer_args: {
          'displayer': 'obj'
        }
      }, {
        col_name: 'date',
        header_name: 'date',
        displayer_args: {
          'displayer': 'string'
        },
        tooltip_config: {
          'tooltip_type': 'simple',
          'val_column': 'tt'
        }
      }, {
        col_name: 'date2',
        header_name: 'date2',
        displayer_args: {
          'displayer': 'string'
        }
      }],
      pinned_rows: [],
      left_col_configs
    }
  }
}`,...(m=(c=a.parameters)==null?void 0:c.docs)==null?void 0:m.source}}};var p,f,g;n.parameters={...n.parameters,docs:{...(p=n.parameters)==null?void 0:p.docs,source:{originalSource:`{
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
        header_name: 'index',
        displayer_args: {
          'displayer': 'obj'
        }
      }, {
        col_name: 'date',
        header_name: 'date',
        displayer_args: {
          'displayer': 'string'
        },
        color_map_config: {
          color_rule: "color_from_column",
          val_column: "color"
        }
      }],
      pinned_rows: [],
      left_col_configs
    }
  }
}`,...(g=(f=n.parameters)==null?void 0:f.docs)==null?void 0:g.source}}};var h,x,y;r.parameters={...r.parameters,docs:{...(h=r.parameters)==null?void 0:h.docs,source:{originalSource:`{
  args: {
    df_data: [{
      index: 0,
      chart1: lineChart
    }],
    df_viewer_config: {
      column_config: [{
        col_name: 'index',
        header_name: 'index',
        displayer_args: {
          'displayer': 'obj'
        }
      }, {
        col_name: 'chart1',
        header_name: 'chart1',
        displayer_args: {
          'displayer': 'chart'
        }
      }],
      pinned_rows: [],
      left_col_configs
    }
  }
}`,...(y=(x=r.parameters)==null?void 0:x.docs)==null?void 0:y.source}}};const L=["Primary","Tooltip","ColorFromCol","Chart"];export{r as Chart,n as ColorFromCol,e as Primary,a as Tooltip,L as __namedExportsOrder,G as default};
