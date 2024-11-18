#!/bin/bash
cd packages/buckaroo-js-core
npm install
npm run build
cd ../bundled-staging
npm install
npm run bundle


# set -e
# #rm -rf node_modules 
# rm -rf dist
# pip install build polars
# python -m build

# twine check dist/*
#python -m twine upload --repository testpypi dist/*
#rm -f dist/index.js dist/index.js.LICENSE.txt
#python -m twine upload --repository pypi dist/*.whl
#npm publish
