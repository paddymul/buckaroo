import{j as a}from"./jsx-runtime-DiklIkkE.js";import{a as Q}from"./DFViewerInfinite-CH5RP8Q2.js";import{S as X,a as Z}from"./StoryUtils-BKZ5T2yq.js";import{d as H,H as U,a as W,N as B,c as $}from"./DFViewerDataHelper-BZ4H-prw.js";import{r as t}from"./index-DRjF_FHU.js";import"./lodash-CGIzQN7T.js";import"./main.esm-B4lyadPg.js";import"./index-DHHUZ-3A.js";import"./HistogramCell-DpbV8qWt.js";import"./ChartCell-lxLhA7NV.js";import"./tiny-invariant-CopsF_GD.js";import"./client-DTWAFNtf.js";const n=r=>({col_name:r,displayer_args:{displayer:"obj"}}),s=(r,e,o)=>({col_name:r,displayer_args:{displayer:"float",min_fraction_digits:e,max_fraction_digits:o}}),u=(r,e,o)=>({col_name:r,displayer_args:{displayer:"integer",min_digits:e,max_digits:o}}),aa=({data:r,df_viewer_config:e,secondary_df_viewer_config:o,summary_stats_data:l,outside_df_params:p})=>a.jsx(X,{children:a.jsx(ra,{data:r,df_viewer_config:e,secondary_df_viewer_config:o,summary_stats_data:l,outside_df_params:p})}),ra=({data:r,df_viewer_config:e,secondary_df_viewer_config:o,summary_stats_data:l,outside_df_params:p})=>{const[f,T]=t.useState(!1),[y,A]=t.useState(!1),[b,Y]=t.useState("none"),v={none:void 0,"500ms":500,"1.5 s":1500,"5s":5e3},q=$(r,v[b]),z=f&&o||e,G=y?"some error":void 0,[J,K]=t.useState("b");return a.jsxs("div",{style:{height:500,width:800},children:[a.jsxs("div",{style:{marginBottom:"10px",display:"flex",alignItems:"center",gap:"10px"},children:[a.jsx("button",{onClick:()=>T(!f),children:"Toggle Config"}),a.jsx(Z,{label:"dsDelay",options:Object.keys(v),value:b,onChange:Y}),a.jsxs("span",{children:["Current Config: ",f?"Secondary":"Primary"]}),a.jsx("button",{onClick:()=>A(!y),children:"Toggle Error"}),a.jsxs("span",{children:["Error State: ",y?"Error":"No Error"]})]}),a.jsx(Q,{data_wrapper:q,df_viewer_config:z,summary_stats_data:l,activeCol:J,setActiveCol:K,outside_df_params:p,error_info:G})]})},wa={title:"Buckaroo/DFViewer/DFViewerInfiniteShadow",component:aa,parameters:{layout:"centered"},tags:["autodocs"],argTypes:{}},ea=[{a:20,b:"foo"},{a:30,b:"bar"},{a:NaN,b:NaN},{a:null,b:null},{a:void 0,b:void 0}],oa={column_config:[s("a",2,8),u("a",2,3),n("b"),{col_name:"b",displayer_args:{displayer:"string"}}],pinned_rows:[]},na={column_config:[s("a",2,8),u("a",2,3),n("b")],pinned_rows:[]},w={column_config:[n("a"),n("b"),n("c"),n("d")],pinned_rows:[{primary_key_val:"histogram",displayer_args:{displayer:"histogram"}}]},g={column_config:[s("a",2,8),u("a",2,3),n("b")],pinned_rows:[{primary_key_val:"histogram",displayer_args:{displayer:"histogram"}}]},i={args:{data:ea,df_viewer_config:oa,secondary_df_viewer_config:g}},C=5e3,c={args:{data:H({a:B(C,3,50),b:W(C)}),df_viewer_config:na,secondary_df_viewer_config:w}},d={args:{data:[],df_viewer_config:w,secondary_df_viewer_config:g,summary_stats_data:U}},sa={column_config:[{col_name:"a",displayer_args:{displayer:"obj"},color_map_config:{color_rule:"color_map",map_name:"BLUE_TO_YELLOW",val_column:"b"}},{col_name:"b",displayer_args:{displayer:"obj"},color_map_config:{color_rule:"color_map",map_name:"BLUE_TO_YELLOW",val_column:"c"}},s("c",1,4),s("d",1,4)],pinned_rows:[{primary_key_val:"histogram",displayer_args:{displayer:"histogram"}}]},m={args:{data:[{a:50,b:5,c:8},{a:70,b:10,c:3},{a:300,b:3,c:42},{a:200,b:19,c:20}],df_viewer_config:sa,secondary_df_viewer_config:g,summary_stats_data:U}},h=300,_={args:{data:H({a:B(h,3,50),b:W(h)}),df_viewer_config:g,secondary_df_viewer_config:w}};var D,S,x;i.parameters={...i.parameters,docs:{...(D=i.parameters)==null?void 0:D.docs,source:{originalSource:`{
  args: {
    //@ts-ignore
    // the undefineds aren't allowed in the type but do happen in the wild
    data: data,
    df_viewer_config: primaryConfigPrimary,
    secondary_df_viewer_config: IntFloatConfig
  }
}`,...(x=(S=i.parameters)==null?void 0:S.docs)==null?void 0:x.source}}};var E,j,F;c.parameters={...c.parameters,docs:{...(E=c.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    data: dictOfArraystoDFData({
      'a': NRandom(N, 3, 50),
      'b': arange(N)
    }),
    df_viewer_config: LargeConfig,
    secondary_df_viewer_config: PinnedRowConfig
  }
}`,...(F=(j=c.parameters)==null?void 0:j.docs)==null?void 0:F.source}}};var I,M,N;d.parameters={...d.parameters,docs:{...(I=d.parameters)==null?void 0:I.docs,source:{originalSource:`{
  args: {
    data: [],
    df_viewer_config: PinnedRowConfig,
    secondary_df_viewer_config: IntFloatConfig,
    summary_stats_data: HistogramSummaryStats
  }
}`,...(N=(M=d.parameters)==null?void 0:M.docs)==null?void 0:N.source}}};var P,L,O;m.parameters={...m.parameters,docs:{...(P=m.parameters)==null?void 0:P.docs,source:{originalSource:`{
  args: {
    data: [{
      a: 50,
      b: 5,
      c: 8
    }, {
      a: 70,
      b: 10,
      c: 3
    }, {
      a: 300,
      b: 3,
      c: 42
    }, {
      a: 200,
      b: 19,
      c: 20
    }],
    df_viewer_config: ColorMapDFViewerConfig,
    secondary_df_viewer_config: IntFloatConfig,
    summary_stats_data: HistogramSummaryStats
  }
}`,...(O=(L=m.parameters)==null?void 0:L.docs)==null?void 0:O.source}}};var R,V,k;_.parameters={..._.parameters,docs:{...(R=_.parameters)==null?void 0:R.docs,source:{originalSource:`{
  args: {
    data: dictOfArraystoDFData({
      'a': NRandom(MEDIUM, 3, 50),
      'b': arange(MEDIUM)
    }),
    df_viewer_config: IntFloatConfig,
    secondary_df_viewer_config: PinnedRowConfig
  }
}`,...(k=(V=_.parameters)==null?void 0:V.docs)==null?void 0:k.source}}};const ba=["Primary","Large","PinnedRows","ColorMapExample","MedDFVHeight"];export{m as ColorMapExample,c as Large,_ as MedDFVHeight,d as PinnedRows,i as Primary,ba as __namedExportsOrder,wa as default};
