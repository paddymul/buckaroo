# Buckaroo - The Data Table for Jupyter

Buckaroo is a modern data table for Jupyter that expedites the most common exploratory data analysis tasks. The most basic data analysis task - looking at the raw data, is cumbersome with the existing pandas tooling.  Buckaroo starts with a modern performant data table that displays up to 10k rows, is sortable, has value formatting, and scrolls.  On top of the core table experience extra features like summary stats, histograms, smart sampling, auto-cleaning, and a low code UI are added.  All of the functionality has sensible defaults that can be overridden to customize the experience for your workflow.

<img width="1002" alt="Polars-Buckaroo" src="https://github.com/paddymul/buckaroo/assets/40453/f48b701b-dfc4-4470-8588-05b6a9f33eec">


## Try it with Jupyterlite
Play with Buckaroo without any installation.
[Full Tour](https://paddymul.github.io/buckaroo-examples/lab/index.html?path=Full-tour.ipynb)
[![lite-badge](https://jupyterlite.rtfd.io/en/latest/_static/badge.svg)](https://paddymul.github.io/buckaroo-examples/lab/index.html?path=Full-tour.ipynb)

## Quick start

run `pip install buckaroo` then restart your jupyter server

The following code shows Buckaroo on a simple dataframe

```
import pandas as pd
import buckaroo
pd.DataFrame({'a':[1, 2, 10, 30, 50, 60, 50], 'b': ['foo', 'foo', 'bar', pd.NA, pd.NA, pd.NA, pd. NA]})

```

When you run `import buckaroo` in a Jupyter notebook, Buckaroo becomes the default display method for Pandas and Polars DataFrames


## Compatibility

Buckaroo works in the following notebook environments

- `jupyter lab` (version >=3.6.0)
- `jupyter notebook` (version >=7.0) 
- `VS Code notebooks` (with extra install)
- [Jupyter Lite](https://paddymul.github.io/buckaroo-examples/lab/index.html)
- `Google colab`  (with special initiation code, currently broken)


Buckaroo works with the following DataFrame libraries
- `pandas` (version >=1.3.5)
- `polars` optional
- `geopandas` optional


# Learn More

Buckaroo has extensive docs and tests, the best way to learn about the system is from feature example videos on youtube

## Interactive Styling Gallery

The interactive [styling gallery](https://py.cafe/app/paddymul/buckaroo-gallery) lets you see different styling configurations.  You can live edit code and play with different configs.

## Videos 
- [Extending Buckaroo](https://www.youtube.com/watch?v=GPl6_9n31NE)
- [Styling Buckaroo](https://www.youtube.com/watch?v=cbwJyo_PzKY)
- [GeoPandas Support](https://youtu.be/8WBhoNjDJsA)

## Example Notebooks

The following examples are loaded into a jupyter lite environment with Buckaroo installed.
- [Full Tour](https://paddymul.github.io/buckaroo-examples/lab/index.html?path=Full-tour.ipynb) Start here. This gives a broad overview of Buckaroo's features.
- [Histogram Demo](https://paddymul.github.io/buckaroo-examples/lab/index.html?path=Histograms-demo.ipynb) Explantion of the embedded histograms of Buckaroo.
- [Styling Gallery](https://paddymul.github.io/buckaroo-examples/lab/index.html?path=styling-gallery.ipynb) Examples of all of the different formatters and styling available for the table
- [Extending Buckaroo](https://paddymul.github.io/buckaroo-examples/lab/index.html?path=Extending.ipynb) Broad overview of how to add post processing methods and custom styling methods to Buckaroo
- [Styling Howto](https://paddymul.github.io/buckaroo-examples/lab/index.html?path=styling-howto.ipynb) In depth explanation of how to write custom styling methods
- [Pluggable Analysis Framework](https://paddymul.github.io/buckaroo-examples/lab/index.html?path=Pluggable-Analysis-Framework.ipynb) How to add new summary stats to Buckaroo
- [Solara Buckaroo](https://github.com/paddymul/buckaroo/blob/main/example-notebooks/Solara-Buckaroo.ipynb) Using Buckaroo with Solara
- [GeoPandas with Bucakroo](https://github.com/paddymul/buckaroo/blob/main/example-notebooks/GeoPandas.ipynb)

# Features

## High performance table
The core data grid of buckaroo is based on [AG-Grid](https://www.ag-grid.com/). This loads 1000s of cells in less than a second, with highly customizable display, formatting and scrolling.  You no longer have to use `df.head()` to poke at portions of your data.

## Fixed width formatting by default

By default numeric columns are formatted to use a fixed width font and commas are added.  This allows quick visual confirmation of magnitudes in a column.

## Histograms

[Histograms](https://buckaroo-data.readthedocs.io/en/latest/articles/histograms.html) for every column give you a very quick overview of the distribution of values, including uniques and N/A.

## Summary stats
The summary stats view can be toggled by clicking on the `0` below the `Σ` icon.  Summary stats are similar to `df.describe` and extensible.

## Inteligent sampling

Buckaroo will display entire DataFrames up to 10k rows.  Displaying more than that would run into performance problems that would make display too slow.  When a DataFrame has more than 10k rows, Buckaroo samples a random set of 10k rows, and also adds in the rwos with the 5 most extreme values for each column.

## Sorting

All of the data visible in the table (rows shown), is sortable by clicking on a column name, further clicks change sort direction then disable sort for that column.  Because extreme values are included with sample rows, you can see outlier values too.

## Extensibility at the core

Buckaroo summary stats are built on the [Pluggable Analysis Framework](https://buckaroo-data.readthedocs.io/en/latest/articles/pluggable.html) that allows individual summary stats to be overridden, and new summary stats to be built in terms of existing summary stats.  Care is taken to prevent errors in summary stats from preventing display of a dataframe.

## Lowcode UI (beta)

Buckaroo has a simple low code UI with python code gen. This view can be toggled by clicking on the `0` below the ` λ ` icon.

## Auto cleaning (beta)

Buckaroo can [automatically clean](https://buckaroo-data.readthedocs.io/en/latest/articles/auto_clean.html) dataframes to remove common data errors (a single string in a column of ints, recognizing date times...).  This feature is in beta.  You can access it by invoking buckaroo as `BuckarooWidget(df, auto_clean=True)`

## Development installation

For a development installation:

```bash
git clone https://github.com/paddymul/buckaroo.git
cd buckaroo
#we need to build against 3.6.5, jupyterlab 4.0 has different JS typing that conflicts
# the installable still works in JL4
pip install build twine pytest sphinx polars mypy jupyterlab==3.6.5 pandas-stubs geopolars pyarrow
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


### UV Instuctions
```sh
cd buckaroo
uv venv
source ~/buckaroo/.venv/bin/activate
uv sync -q

```

### adding a package
```sh
cd ~/buckaroo
uv add $PACKAGE_NAME
```

#### adding a package to a subgroup 
```sh
cd ~/buckaroo
uv add --group $GROUP_NAME --quiet $PACKAGE_NAME
```

### Release instructions
[github release instructions](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)

```bash
update CHANGELOG.md
git commit -m "updated changelog for release $VERSION_NUMBER"
git tag $VERSION_NUMBER # no leading v in the version number
git push origin tag $VERSION_NUMBER
```
navigate to [create new buckaroo release](https://github.com/paddymul/buckaroo/releases/new)
Follow instructions




## Contributions

We :heart: contributions.

Have you had a good experience with this project? Why not share some love and contribute code, or just let us know about any issues you had with it?

We welcome issue reports [here](../../issues); be sure to choose the proper issue template for your issue, so that we can be sure you're providing the necessary information.


