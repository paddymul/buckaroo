import{j as v}from"./jsx-runtime-DiklIkkE.js";import{R as n}from"./index-DRjF_FHU.js";import{s as E,d as M,m as _,g as A,O as W}from"./OperationExamples-DcZ4epzJ.js";const b=({operations:j})=>{const[t,K]=n.useState(j),[L,R]=n.useState(A(t,1));return v.jsx(W,{operations:t,setOperations:K,activeKey:L,setActiveKey:R})},w={title:"Components/OperationsList",component:b,parameters:{layout:"centered"},tags:["autodocs"]},a={args:{operations:E}},e={args:{operations:[]}},s={args:{operations:[E[0]]}},r={args:{operations:M}},o={args:{operations:_}};var p,i,c;a.parameters={...a.parameters,docs:{...(p=a.parameters)==null?void 0:p.docs,source:{originalSource:`{
  args: {
    operations: sampleOperations
  }
}`,...(c=(i=a.parameters)==null?void 0:i.docs)==null?void 0:c.source}}};var m,g,u;e.parameters={...e.parameters,docs:{...(m=e.parameters)==null?void 0:m.docs,source:{originalSource:`{
  args: {
    operations: []
  }
}`,...(u=(g=e.parameters)==null?void 0:g.docs)==null?void 0:u.source}}};var d,l,O;s.parameters={...s.parameters,docs:{...(d=s.parameters)==null?void 0:d.docs,source:{originalSource:`{
  args: {
    operations: [sampleOperations[0]]
  }
}`,...(O=(l=s.parameters)==null?void 0:l.docs)==null?void 0:O.source}}};var y,S,f;r.parameters={...r.parameters,docs:{...(y=r.parameters)==null?void 0:y.docs,source:{originalSource:`{
  args: {
    operations: dataCleaningOps
  }
}`,...(f=(S=r.parameters)==null?void 0:S.docs)==null?void 0:f.source}}};var x,C,D;o.parameters={...o.parameters,docs:{...(x=o.parameters)==null?void 0:x.docs,source:{originalSource:`{
  args: {
    operations: manyOperations
  }
}`,...(D=(C=o.parameters)==null?void 0:C.docs)==null?void 0:D.source}}};const z=["Default","Empty","SingleOperation","DataCleaning","ManyOperations"];export{r as DataCleaning,a as Default,e as Empty,o as ManyOperations,s as SingleOperation,z as __namedExportsOrder,w as default};
