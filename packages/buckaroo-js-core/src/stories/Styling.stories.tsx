import type { Meta, StoryObj } from "@storybook/react";
import  style from '../../dist/style.css?raw';
import { useEffect, useRef } from "react";
import React from "react";
import ReactDOM from 'react-dom/client';
//import '../style/full.css';
//import _ from "lodash";


//import style from './tmp/mockComponent.css'; 
/*
constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        const { shadowRoot } = this;
        container = document.createElement('div');

        styleTag = document.createElement('style');
        styleTag.innerHTML = style;
        shadowRoot.appendChild(styleTag);            

        shadowRoot.appendChild(container);

import React, { useEffect, useRef } from 'react';
import ReactDOM from 'react-dom/client';
*/
interface ShadowDomWrapperProps {
  children: React.ReactNode;
}

const ShadowDomWrapper: React.FC<ShadowDomWrapperProps> = ({ children }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const shadowRootRef = useRef<ShadowRoot | null>(null);

  useEffect(() => {
    if (containerRef.current && !shadowRootRef.current) {
      // Attach shadow root
      shadowRootRef.current = containerRef.current.attachShadow({ mode: 'open' });
    }
    console.log("style", style)
    if (shadowRootRef.current) {
      const shadowContent = document.createElement('div');

      const styleTag = document.createElement('style');
      //@ts-ignore
      styleTag.innerHTML = style;
      shadowRootRef.current.appendChild(styleTag);            

      shadowRootRef.current.appendChild(shadowContent);

      const reactRoot = ReactDOM.createRoot(shadowContent);
      reactRoot.render(<React.StrictMode>{children}</React.StrictMode>);

      // Cleanup
      return () => {
        reactRoot.unmount();
        shadowRootRef.current?.removeChild(shadowContent);
      };
    }
  }, [children]);

  return <div ref={containerRef}></div>;
};


const CSSPlay = ({a}: {
    a:number}) => {
	console.log("a", a)
  return (<ShadowDomWrapper>
      <div style={{height:500, width:800}} className={"ag-theme-alpine-dark"}>
	  <span className={"ag-sort-indicator-container"} style={{color:"green", height:50, width:50, border:"3px solid orange" }}  data-ref="eSortIndicator">
          <span data-ref="eSortOrder" className={"ag-sort-indicator-icon ag-sort-order ag-hidden"} aria-hidden="true">1</span>
          <span data-ref="eSortAsc" className={"ag-sort-indicator-icon ag-sort-ascending-icon"} aria-hidden="true">
          <span className={"ag-icon ag-icon-asc"} style={{color:"black"}} unselectable="on" role="presentation">
	   </span></span>

	  </span>
	  <span className={"ag-icon ag-icon-asc"} unselectable="on" role="presentation">
	  </span>
     </div>
     </ShadowDomWrapper>);
}

/*
          <span data-ref="eSortDesc" class="ag-sort-indicator-icon ag-sort-descending-icon ag-hidden" aria-hidden="true"><span class="ag-icon ag-icon-desc" unselectable="on" role="presentation"></span></span>
          <span data-ref="eSortMixed" class="ag-sort-indicator-icon ag-sort-mixed-icon ag-hidden" aria-hidden="true"><span class="ag-icon ag-icon-none" unselectable="on" role="presentation"></span></span>
          <span data-ref="eSortNone" class="ag-sort-indicator-icon ag-sort-none-icon ag-hidden" aria-hidden="true"><span class="ag-icon ag-icon-none" unselectable="on" role="presentation"></span></span>

  */

// More on how to set up stories at: https://storybook.js.org/docs/writing-stories#default-export
const meta = {
  title: "CSSPlay",
    component:CSSPlay,
  parameters: {
    // Optional parameter to center the component in the Canvas. More
    // info: https://storybook.js.org/docs/configure/story-layout
    layout: "centered",
      
  },
  // This component will have an automatically generated Autodocs
  // entry: https://storybook.js.org/docs/writing-docs/autodocs
  tags: ["autodocs"],
  // More on argTypes: https://storybook.js.org/docs/api/argtypes
  argTypes: {
      //backgroundColor: { control: "color" },
      //operations: 
  },
  // Use `fn` to spy on the onClick arg, which will appear in the
  // actions panel once invoked:
  // https://storybook.js.org/docs/essentials/actions#action-args
  //args: { onClick: fn() },
} satisfies Meta<typeof CSSPlay>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
    args: { a: 5}}
