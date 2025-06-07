import{j as a}from"./jsx-runtime-DiklIkkE.js";import{a as na}from"./gridUtils-FdLmYHKG.js";import{S as sa,a as ia}from"./StoryUtils-BBReZMxB.js";import{d as G,H as f,a as J,N as K,c as ta}from"./DFViewerDataHelper-BZ4H-prw.js";import{r as t}from"./index-DRjF_FHU.js";import"./lodash-CGIzQN7T.js";import"./HistogramCell-CR3xZS9E.js";import"./index-Bx0Ph3cE.js";import"./ChartCell-CdGzSEf4.js";import"./tiny-invariant-CopsF_GD.js";import"./main.esm-CraDeAap.js";import"./client-DQginrwT.js";const n=e=>({col_name:e,displayer_args:{displayer:"obj"}}),i=(e,r,o)=>({col_name:e,displayer_args:{displayer:"float",min_fraction_digits:r,max_fraction_digits:o}}),v=(e,r,o)=>({col_name:e,displayer_args:{displayer:"integer",min_digits:r,max_digits:o}}),ca=({data:e,df_viewer_config:r,secondary_df_viewer_config:o,summary_stats_data:y,outside_df_params:u})=>a.jsx(sa,{children:a.jsx(da,{data:e,df_viewer_config:r,secondary_df_viewer_config:o,summary_stats_data:y,outside_df_params:u})}),da=({data:e,df_viewer_config:r,secondary_df_viewer_config:o,summary_stats_data:y,outside_df_params:u})=>{const[b,Q]=t.useState(!1),[w,X]=t.useState(!1),[C,Z]=t.useState("none"),x={none:void 0,"500ms":500,"1.5 s":1500,"5s":5e3},$=ta(e,x[C]),aa=b&&o||r,ea=w?"some error":void 0,[ra,oa]=t.useState("b");return a.jsxs("div",{style:{height:500,width:800},children:[a.jsxs("div",{style:{marginBottom:"10px",display:"flex",alignItems:"center",gap:"10px"},children:[a.jsx("button",{onClick:()=>Q(!b),children:"Toggle Config"}),a.jsx(ia,{label:"dsDelay",options:Object.keys(x),value:C,onChange:Z}),a.jsxs("span",{children:["Current Config: ",b?"Secondary":"Primary"]}),a.jsx("button",{onClick:()=>X(!w),children:"Toggle Error"}),a.jsxs("span",{children:["Error State: ",w?"Error":"No Error"]})]}),a.jsx(na,{data_wrapper:$,df_viewer_config:aa,summary_stats_data:y,activeCol:ra,setActiveCol:oa,outside_df_params:u,error_info:ea})]})},Fa={title:"Buckaroo/DFViewer/DFViewerInfiniteShadow",component:ca,parameters:{layout:"centered"},tags:["autodocs"],argTypes:{}},la=[{a:20,b:"foo"},{a:30,b:"bar"},{a:NaN,b:NaN},{a:null,b:null},{a:void 0,b:void 0}],_a={column_config:[i("a",2,8),v("a",2,3),n("b"),{col_name:"b",field:"b",displayer_args:{displayer:"string"}}],pinned_rows:[]},pa={column_config:[i("a",2,8),v("a",2,3),n("b")],pinned_rows:[]},h={column_config:[n("a"),n("b"),n("c"),n("d")],pinned_rows:[{primary_key_val:"histogram",displayer_args:{displayer:"histogram"}}]},s={column_config:[i("a",2,8),v("a",2,3),n("b")],pinned_rows:[{primary_key_val:"histogram",displayer_args:{displayer:"histogram"}}]},c={args:{data:la,df_viewer_config:_a,secondary_df_viewer_config:s}},S=5e3,d={args:{data:G({a:K(S,3,50),b:J(S)}),df_viewer_config:pa,secondary_df_viewer_config:h}},l={args:{data:[],df_viewer_config:h,secondary_df_viewer_config:s,summary_stats_data:f}},ma={column_config:[{col_name:"a",field:"a",displayer_args:{displayer:"obj"},color_map_config:{color_rule:"color_map",map_name:"BLUE_TO_YELLOW",val_column:"b"}},{col_name:"b",field:"b",displayer_args:{displayer:"obj"},color_map_config:{color_rule:"color_map",map_name:"BLUE_TO_YELLOW",val_column:"c"}},i("c",1,4),i("d",1,4)],pinned_rows:[{primary_key_val:"histogram",displayer_args:{displayer:"histogram"}}]},_={args:{data:[{a:50,b:5,c:8},{a:70,b:10,c:3},{a:300,b:3,c:42},{a:200,b:19,c:20}],df_viewer_config:ma,secondary_df_viewer_config:s,summary_stats_data:f}},ga={column_config:[{col_path:["super","sub_a2"],field:"a",displayer_args:{displayer:"obj"}},{col_name:"a",col_path:["super","sub_a"],field:"a",displayer_args:{displayer:"obj"}},{col_path:["super","sub_a2"],field:"a",displayer_args:{displayer:"obj"}},{col_path:["super","sub_c"],field:"c",displayer_args:{displayer:"obj"}},{col_name:"b",col_path:["super 2","b"],field:"b",displayer_args:{displayer:"obj"}}],pinned_rows:[]},fa={column_config:[{col_path:["super","foo","a"],field:"a",displayer_args:{displayer:"obj"}},{col_name:"a",col_path:["super","foo","b"],field:"a",displayer_args:{displayer:"obj"}},{col_path:["super","bar","a"],field:"a",displayer_args:{displayer:"obj"}},{col_path:["super","bar","b"],field:"c",displayer_args:{displayer:"obj"}},{col_name:"b",col_path:["super 2","b"],field:"b",displayer_args:{displayer:"obj"}}],pinned_rows:[]},p={args:{data:[{a:50,b:5,c:"asdfasdf"},{a:70,b:10,c:"foo bar ba"},{a:300,b:3,c:"stop breaking down"},{a:200,b:19,c:"exile on main"}],df_viewer_config:ga,secondary_df_viewer_config:s,summary_stats_data:f}},m={args:{data:[{a:50,b:5,c:"asdfasdf"},{a:70,b:10,c:"foo bar ba"},{a:300,b:3,c:"stop breaking down"},{a:200,b:19,c:"exile on main"}],df_viewer_config:fa,secondary_df_viewer_config:s,summary_stats_data:f}},j=300,g={args:{data:G({a:K(j,3,50),b:J(j)}),df_viewer_config:s,secondary_df_viewer_config:h}};var D,I,F;c.parameters={...c.parameters,docs:{...(D=c.parameters)==null?void 0:D.docs,source:{originalSource:`{
  args: {
    //@ts-ignore
    // the undefineds aren't allowed in the type but do happen in the wild
    data: data,
    df_viewer_config: primaryConfigPrimary,
    secondary_df_viewer_config: IntFloatConfig
  }
}`,...(F=(I=c.parameters)==null?void 0:I.docs)==null?void 0:F.source}}};var E,M,L;d.parameters={...d.parameters,docs:{...(E=d.parameters)==null?void 0:E.docs,source:{originalSource:`{
  args: {
    data: dictOfArraystoDFData({
      'a': NRandom(N, 3, 50),
      'b': arange(N)
    }),
    df_viewer_config: LargeConfig,
    secondary_df_viewer_config: PinnedRowConfig
  }
}`,...(L=(M=d.parameters)==null?void 0:M.docs)==null?void 0:L.source}}};var N,k,P;l.parameters={...l.parameters,docs:{...(N=l.parameters)==null?void 0:N.docs,source:{originalSource:`{
  args: {
    data: [],
    df_viewer_config: PinnedRowConfig,
    secondary_df_viewer_config: IntFloatConfig,
    summary_stats_data: HistogramSummaryStats
  }
}`,...(P=(k=l.parameters)==null?void 0:k.docs)==null?void 0:P.source}}};var V,O,R;_.parameters={..._.parameters,docs:{...(V=_.parameters)==null?void 0:V.docs,source:{originalSource:`{
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
}`,...(R=(O=_.parameters)==null?void 0:O.docs)==null?void 0:R.source}}};var T,H,U;p.parameters={...p.parameters,docs:{...(T=p.parameters)==null?void 0:T.docs,source:{originalSource:`{
  args: {
    data: [{
      a: 50,
      b: 5,
      c: "asdfasdf"
    }, {
      a: 70,
      b: 10,
      c: "foo bar ba"
    }, {
      a: 300,
      b: 3,
      c: "stop breaking down"
    }, {
      a: 200,
      b: 19,
      c: "exile on main"
    }],
    df_viewer_config: MultiIndexDFViewerConfig,
    secondary_df_viewer_config: IntFloatConfig,
    summary_stats_data: HistogramSummaryStats
  }
}`,...(U=(H=p.parameters)==null?void 0:H.docs)==null?void 0:U.source}}};var W,B,A;m.parameters={...m.parameters,docs:{...(W=m.parameters)==null?void 0:W.docs,source:{originalSource:`{
  args: {
    data: [{
      a: 50,
      b: 5,
      c: "asdfasdf"
    }, {
      a: 70,
      b: 10,
      c: "foo bar ba"
    }, {
      a: 300,
      b: 3,
      c: "stop breaking down"
    }, {
      a: 200,
      b: 19,
      c: "exile on main"
    }],
    df_viewer_config: ThreeLevelIndex,
    secondary_df_viewer_config: IntFloatConfig,
    summary_stats_data: HistogramSummaryStats
  }
}`,...(A=(B=m.parameters)==null?void 0:B.docs)==null?void 0:A.source}}};var Y,q,z;g.parameters={...g.parameters,docs:{...(Y=g.parameters)==null?void 0:Y.docs,source:{originalSource:`{
  args: {
    data: dictOfArraystoDFData({
      'a': NRandom(MEDIUM, 3, 50),
      'b': arange(MEDIUM)
    }),
    df_viewer_config: IntFloatConfig,
    secondary_df_viewer_config: PinnedRowConfig
  }
}`,...(z=(q=g.parameters)==null?void 0:q.docs)==null?void 0:z.source}}};const Ea=["Primary","Large","PinnedRows","ColorMapExample","MultiIndex","ThreeLevelColumnIndex","MedDFVHeight"];export{_ as ColorMapExample,d as Large,g as MedDFVHeight,p as MultiIndex,l as PinnedRows,c as Primary,m as ThreeLevelColumnIndex,Ea as __namedExportsOrder,Fa as default};
