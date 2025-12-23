/// <reference types="vitest" />
//import { defineConfig } from 'vitest/config'
import { defineConfig } from "vite";
import dts from "vite-plugin-dts";
import { peerDependencies } from "./package.json";


export default defineConfig({
    resolve: {
        alias: {
            // Use lodash-es for better tree-shaking
            'lodash': 'lodash-es'
        }
    },
    build: {
        lib: {
            entry: "./src/index.ts", // Specifies the entry point for building the library.
            name: "vite-react-ts-button", // Sets the name of the generated library.
            fileName: (format) => `index.${format}.js`, // Generates the output file name based on the format.
            formats: ["cjs", "es", "esm"], // Specifies the output formats (CommonJS and ES modules).
        },
        rollupOptions: {
            external: ["react", "react-dom", 'react/jsx-runtime'],
            output: {
                // Enable tree-shaking
                manualChunks: undefined,
            },
        },
        sourcemap: true, // Generates source maps for debugging.
        emptyOutDir: true, // Clears the output directory before building.
        minify: true
    },

    transform: {
	"^.+\\.tsx?$": "ts-jest",
    },
    plugins: [dts()], // Uses the 'vite-plugin-dts' plugin for generating TypeScript declaration files (d.ts).
    test: {
        globals: true,
        environment: "jsdom",
        setupFiles: "./setupTests.ts",
    },
});
