import  style from '../../dist/style.css?raw';
import { useEffect, useRef } from "react";
import React from "react";
import ReactDOM from 'react-dom/client';

import distStyle from '../../dist/style.css?raw';

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
