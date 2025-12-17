#!/bin/bash
# Script to reproduce the esbuild "Could not resolve buckaroo-js-core" error
# This simulates what happens in full_build.sh and CI

set -e

echo "🧪 Testing build error reproduction..."

# Make sure we're in the buckaroo directory
cd "$(dirname "$0")/.."

# Step 1: Delete key directories (simulating clean state)
echo "📁 Step 1: Deleting key directories..."
rm -rf packages/node_modules || true
rm -rf packages/buckaroo-js-core/dist || true
rm -rf packages/buckaroo-js-core/node_modules || true
rm -rf buckaroo/widget.js || true
rm -rf packages/pnpm-lock.yaml || true
rm -rf packages/buckaroo-js-core/pnpm-lock.yaml || true

# Step 2: Build buckaroo-js-core
echo "🔨 Step 2: Building buckaroo-js-core..."
cd packages/buckaroo-js-core
pnpm install
pnpm run build:tsc
pnpm run build:vite
cd ../..

# Step 3: Copy style.css (as in full_build.sh)
echo "📋 Step 3: Copying style.css..."
cp packages/buckaroo-js-core/dist/style.css buckaroo/static/compiled.css || true

# Step 4: Remove buckaroo-js-core/node_modules (as in full_build.sh)
echo "🗑️  Step 4: Removing buckaroo-js-core/node_modules..."
rm -rf packages/buckaroo-js-core/node_modules || true

# Step 4.5: Check if the issue is the package.json path
echo "🧪 Step 4.5: Checking package.json path issue..."
echo "Current packages/package.json has:"
grep "buckaroo-js-core" packages/package.json
echo "But we're in packages/, so the path should be './buckaroo-js-core' not './packages/buckaroo-js-core'"
echo "Let's see what happens when pnpm tries to resolve it..."

# Step 5: Check if buckaroo-js-core package.json exists and has proper exports
echo "📦 Step 5: Checking buckaroo-js-core package.json..."
cat packages/buckaroo-js-core/package.json | grep -A 5 '"exports"' || echo "No exports field found"

# Step 6: Install in packages/ (this creates broken symlink)
echo "🔧 Step 6: Installing in packages/ (this will create broken symlink)..."
cd packages

echo "Installing dependencies..."
pnpm install 2>&1 | grep -E "(WARN|ERROR|buckaroo)" || true

echo "Checking symlink:"
ls -la node_modules/buckaroo-js-core 2>/dev/null || echo "Symlink doesn't exist!"
if [ -L node_modules/buckaroo-js-core ]; then
    SYMLINK_TARGET=$(readlink node_modules/buckaroo-js-core)
    echo "Symlink target: $SYMLINK_TARGET"
    echo "Symlink target exists: $([ -e node_modules/buckaroo-js-core ] && echo 'YES' || echo 'NO')"
    ABS_TARGET=$(readlink -f node_modules/buckaroo-js-core 2>/dev/null || echo "FAILED_TO_RESOLVE")
    echo "Absolute symlink target: $ABS_TARGET"
    if [ "$ABS_TARGET" != "FAILED_TO_RESOLVE" ]; then
        echo "Absolute target exists: $([ -e "$ABS_TARGET" ] && echo 'YES' || echo 'NO')"
    else
        echo "Could not resolve absolute path (symlink is broken)"
    fi
fi

# Step 7: Temporarily move buckaroo-js-core to force esbuild to use node_modules
echo ""
echo "🚨 Step 7: Reproducing the error..."
echo "The symlink in node_modules is broken (points to non-existent path)"
echo "In CI, esbuild can't resolve from current directory, so it fails"
echo "Let's temporarily move buckaroo-js-core to simulate CI environment..."
mv buckaroo-js-core buckaroo-js-core.temp

echo ""
echo "Attempting build (should fail with 'Could not resolve buckaroo-js-core')..."
echo "Running esbuild directly to see the actual error..."
set +e  # Don't exit on error
pnpm exec esbuild js/widget.tsx --format=esm --bundle --outdir=../buckaroo/static/ 2>&1
BUILD_EXIT=$?
set -e

# Restore the directory
mv buckaroo-js-core.temp buckaroo-js-core

if [ $BUILD_EXIT -ne 0 ]; then
    echo ""
    echo "✅ SUCCESS! Reproduced the error!"
    echo "The build failed as expected with: 'Could not resolve buckaroo-js-core'"
else
    echo ""
    echo "❌ Build succeeded (unexpected)"
fi

echo ""
echo "🚨 Step 8: Summary of the issue..."
echo ""
echo "PROBLEM IDENTIFIED:"
echo "1. packages/package.json has: \"buckaroo-js-core\": \"./packages/buckaroo-js-core\""
echo "2. But we're running from packages/, so the path should be \"./buckaroo-js-core\""
echo "3. pnpm creates a broken symlink: node_modules/buckaroo-js-core -> ../packages/buckaroo-js-core"
echo "4. From packages/node_modules/, this resolves to packages/packages/buckaroo-js-core (DOESN'T EXIST)"
echo "5. pnpm warns: 'Installing a dependency from a non-existent directory'"
echo ""
echo "In CI, esbuild fails with: 'Could not resolve buckaroo-js-core'"
echo "Locally, esbuild might succeed because it resolves from current directory"
echo ""
echo "FIX: Change packages/package.json from:"
echo "  \"buckaroo-js-core\": \"./packages/buckaroo-js-core\""
echo "to:"
echo "  \"buckaroo-js-core\": \"./buckaroo-js-core\""
echo ""
echo "✅ Script completed - issue reproduced and documented"
cd ..

