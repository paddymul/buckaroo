import  style from '../../dist/style.css?raw';
import { useEffect, useRef } from "react";
import React from "react";
import ReactDOM from 'react-dom/client';

//import style2 from "https://cdn.jsdelivr.net/npm/@mdi/font/css/materialdesignicons.css?raw";
import distStyle from '../../dist/style.css?raw';
//const distStyle = "";
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

export const ShadowDomWrapper: React.FC<ShadowDomWrapperProps> = ({ children }) => {
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
       styleTag.innerHTML = distStyle;
       shadowRootRef.current.appendChild(styleTag);            

    //   const styleTag2 = document.createElement('style');
    //   //@ts-ignore
    //   styleTag.innerHTML = style2;
    //   shadowRootRef.current.appendChild(styleTag2);         
      
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
