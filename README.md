# ipydatagrid

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/bloomberg/ipydatagrid/HEAD?urlpath=lab%2Ftree%2Fexamples%2FDataGrid.ipynb)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![tested with jest](https://img.shields.io/badge/tested_with-jest-99424f.svg)](https://github.com/facebook/jest)

Fast Datagrid widget for the Jupyter Notebook and JupyterLab

## Menu

- [Usage and Examples](#Usage-and-Examples)
- [Installation](#Installation)
- [Development installation](#Development-installation)
- [Contributions](#Contributions)
- [License](#License)
- [Code of Conduct](#Code-of-Conduct)
- [Security Vulnerability reporting](#Security-Vulnerability-reporting)

## Usage and Examples

A fully-featured DataGrid interface
[![DataGrid](./static/ipydatagrid_1.gif)](https://github.com/bloomberg/ipydatagrid/blob/main/examples/DataGrid.ipynb)

Highly performant and fully integrated with ipywidgets
[![DataGrid](./static/ipydatagrid_2.gif)](https://github.com/bloomberg/ipydatagrid/blob/main/examples/DataGrid.ipynb)

Customize the way data is represented in your grid using a variety of renderers
[![DataGrid](./static/ipydatagrid_3.gif)](https://github.com/bloomberg/ipydatagrid/blob/main/examples/DataGrid.ipynb)

Enjoy a sophisticated selections model with two-way data binding
[![DataGrid](./static/ipydatagrid_4.gif)](https://github.com/bloomberg/ipydatagrid/blob/main/examples/Selections.ipynb)

Conditional formatting powered by Vega Expressions
[![DataGrid](./static/ipydatagrid_5.gif)](https://github.com/bloomberg/ipydatagrid/blob/main/examples/ConditionalFormatting.ipynb)

Tutorial and example notebooks can be found in the `/examples` directory.

## Installation

If using JupyterLab, `ipydatagrid` requires JupyterLab version 3 or higher.

You can install `ipydatagrid` using `pip` or `conda`:

Using `pip`:

```bash
pip install ipydatagrid
```

Using `conda`:

```bash
conda install -c conda-forge ipydatagrid
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:

```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] ipydatagrid
```

NOTE: For examples using Scales from bqplot to work as intended, the bqplot notebook and lab extensions must be installed as well. See the [bqplot repo](https://github.com/bloomberg/bqplot) for installation instructions:

## Development installation

For a development installation:

```bash
git clone https://github.com/Bloomberg/ipydatagrid.git
cd ipydatagrid
conda install ipywidgets=8 jupyterlab
pip install -ve .
```

Enabling development install for Jupyter notebook:

```bash
jupyter nbextension install --py --symlink --sys-prefix ipydatagrid
jupyter nbextension enable --py --sys-prefix ipydatagrid
```

Enabling development install for JupyterLab:

```bash
jupyter labextension develop . --overwrite
```

Note for developers: the `--symlink` argument on Linux or OS X allows one to modify the JavaScript code in-place. This feature is not available with Windows.
`

## Contributions

We :heart: contributions.

Have you had a good experience with this project? Why not share some love and contribute code, or just let us know about any issues you had with it?

We welcome issue reports [here](../../issues); be sure to choose the proper issue template for your issue, so that we can be sure you're providing the necessary information.

Before sending a [Pull Request](../../pulls), please make sure you read our
[Contribution Guidelines](https://github.com/bloomberg/.github/blob/master/CONTRIBUTING.md).

## License

Please read the [LICENSE](LICENSE.txt) file.

## Code of Conduct

This project has adopted a [Code of Conduct](https://github.com/bloomberg/.github/blob/master/CODE_OF_CONDUCT.md).
If you have any concerns about the Code, or behavior which you have experienced in the project, please
contact us at opensource@bloomberg.net.

## Security Vulnerability Reporting

If you believe you have identified a security vulnerability in this project, please send email to the project
team at opensource@bloomberg.net, detailing the suspected issue and any methods you've found to reproduce it.

Please do NOT open an issue in the GitHub repository, as we'd prefer to keep vulnerability reports private until
we've had an opportunity to review and address them.
