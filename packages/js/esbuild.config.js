import esbuild from 'esbuild';

esbuild.build({
  entryPoints: ['widget.tsx'],
  bundle: true,
  format: 'esm',
  outdir: '../../buckaroo/static/',
  minify: true,
  treeShaking: true,
  sourcemap: false,
  target: 'es2020',
  // Externalize React if available in environment (but keep bundled for now)
  // external: ['react', 'react-dom'],
  // Try to reduce lodash size
  alias: {
    'lodash': 'lodash-es'
  },
  // Optimize for size
  legalComments: 'none',
  drop: ['console', 'debugger'],
}).catch(() => process.exit(1));
