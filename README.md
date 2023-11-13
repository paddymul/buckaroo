# Buckaroo - The Data Table for Jupyter

Buckaroo is a modern data table for Jupyter that expedites the most common exploratory data analysis tasks. The most basic data analysis task - looking at the raw data, is cumbersome with the existing pandas tooling.  Buckaroo starts with a modern performant data table that displays up to 10k rows, is sortable, has value formatting, and scrolls.  On top of the core table experience extra features like summary stats, histograms, smart sampling, auto-cleaning, and a low code UI are added.  All of the functionality has sensible defaults that can be overriden to customize the experience for your workflow.

## Try it today

* Buckaroo Full Tour [Buckaroo full tour](https://github.com/paddymul/buckaroo/blob/main/example-notebooks/Full-tour.ipynb)[![Open In Colab](https://camo.githubusercontent.com/52feade06f2fecbf006889a904d221e6a730c194/68747470733a2f2f636f6c61622e72657365617263682e676f6f676c652e636f6d2f6173736574732f636f6c61622d62616467652e737667)](https://colab.research.google.com/github/paddymul/buckaroo/blob/main/example-notebooks/Full-tour.ipynb)

![Buckaroo Screenshot](https://raw.githubusercontent.com/paddymul/buckaroo-assets/main/quick-buckaroo.gif)

## Buckaroo quick start

run `pip install buckaroo`
in a notebook execute the following to see Buckaroo

```
import pandas as pd
import buckaroo
pd.DataFrame({'a':[1, 2, 10, 30, 50, 60, 50], 'b': ['foo', 'foo', 'bar', pd.NA, pd.NA, pd.NA, pd. NA]})

```

When you run `import buckaroo` in a Jupyter notebook, Buckaroo becoes the default display method for Pandas and Polars DataFrames


## Compatability

Buckaroo works in the following notebook environments

- `jupyter lab` (version >=3.6.0)
- `jupyter notebook` (version >=7.0) 
- `VS Code notebooks` (with extra install)
- `Google colab`  (with special initiation code)

Buckaroo works with the following DataFrame libraries
- `pandas` (version >=1.3.5)
- `polars` optional 


# Features

### Histograms

Visible for every column

### Summary stats

### Sorting

### Automatic downsampling




## Development installation

For a development installation:

```bash
git clone https://github.com/paddymul/buckaroo.git
cd buckaroo
#we need to build against 3.6.5, jupyterlab 4.0 has different JS typing that conflicts
# the installable still works in JL4
pip install build twine pytest sphinx-build jupyterlab==3.6.5
pip install -ve .
```

Enabling development install for Jupyter notebook:


Enabling development install for JupyterLab:

```bash
jupyter labextension develop . --overwrite
```

Note for developers: the `--symlink` argument on Linux or OS X allows one to modify the JavaScript code in-place. This feature is not available with Windows.
`
### Developing the JS side

There are a series of examples of the components in [examples/ex](./examples/ex).



Instructions
```bash
npm install
npm run dev
```


## Contributions

We :heart: contributions.

Have you had a good experience with this project? Why not share some love and contribute code, or just let us know about any issues you had with it?

We welcome issue reports [here](../../issues); be sure to choose the proper issue template for your issue, so that we can be sure you're providing the necessary information.

