#!/bin/bash
filename=$1
mode=$2
notebook_name="${filename%.*}"

full_notebook_path="docs/example-notebooks/marimo-wasm/${filename}"
full_output_path="docs/extra-html/example_notebooks/${notebook_name}"
echo "mode $mode"
uv run marimo export html-wasm $full_notebook_path   -o $full_output_path   --mode $mode -f
#uv run marimo export html-wasm docs/example-notebooks/buckaroo_ddd_tour.py  -o docs/extra-html/buckaroo_ddd_tour  --mode run
