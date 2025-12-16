#!/bin/bash
set -e

cd "$(dirname "$0")/../.."

# Create minimal venv if needed
if [ ! -d ".test_venv" ]; then
    echo "Creating test venv..."
    python3 -m venv .test_venv
    .test_venv/bin/pip install --quiet --upgrade pip
    .test_venv/bin/pip install --quiet jupyterlab polars buckaroo
fi

# Start JupyterLab in background
echo "Starting JupyterLab..."
.test_venv/bin/python -m jupyter lab --no-browser --port=8889 --ServerApp.token=test-token-12345 > /tmp/jupyter.log 2>&1 &
JUPYTER_PID=$!
echo "JupyterLab PID: $JUPYTER_PID"

# Wait for JupyterLab to be ready
echo "Waiting for JupyterLab..."
for i in {1..30}; do
    if curl -s -f http://localhost:8889/lab?token=test-token-12345 > /dev/null 2>&1; then
        echo "JupyterLab is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "JupyterLab failed to start"
        kill $JUPYTER_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Create test notebook if it doesn't exist
if [ ! -f test_polars_widget.ipynb ]; then
    echo "Creating test notebook..."
    cat > test_polars_widget.ipynb << 'EOF'
{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import polars as pl\n",
    "from buckaroo.polars_buckaroo import PolarsBuckarooWidget\n",
    "\n",
    "df = pl.DataFrame({\n",
    "    'name': ['Alice', 'Bob', 'Charlie'],\n",
    "    'age': [25, 30, 35],\n",
    "    'score': [85.5, 92.0, 78.3]\n",
    "})\n",
    "\n",
    "PolarsBuckarooWidget(df)"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
EOF
fi

# Run Playwright test
echo "Running Playwright test..."
cd packages/buckaroo-js-core
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    pnpm install --silent
fi
pnpm test:integration
TEST_RESULT=$?

# Cleanup
echo "Cleaning up..."
kill $JUPYTER_PID 2>/dev/null || true
rm -f ../../test_polars_widget.ipynb

exit $TEST_RESULT

