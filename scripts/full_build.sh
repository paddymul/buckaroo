#!/bin/bash
set -e

# Check for --dev flag
DEV_BUILD=false
if [[ "$1" == "--dev" ]]; then
    DEV_BUILD=true
    echo "🔧 Building in DEV mode (no minification, with sourcemaps)"
else
    echo "📦 Building in PRODUCTION mode (minified, tree-shaken)"
fi

# Clean previous builds
rm -rf packages/buckaroo-js-core/dist || true
rm -rf buckaroo/static/*.js buckaroo/static/*.css || true

# Install all workspace dependencies (once)
cd packages
pnpm install

# Build buckaroo-js-core first (tsc + vite)
pnpm --filter buckaroo-js-core run build

# Copy CSS to Python package
cd ..
mkdir -p buckaroo/static
cp packages/buckaroo-js-core/dist/style.css buckaroo/static/compiled.css

# Build anywidget wrapper (esbuild)
cd packages
if [ "$DEV_BUILD" = true ]; then
    pnpm --filter buckaroo-widget run build:dev
else
    pnpm --filter buckaroo-widget run build
fi

# Build Python wheel
cd ..
rm -rf dist || true
uv build --wheel
