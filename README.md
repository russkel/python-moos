python-moos
===========
Python (2.7 and 3) bindings for [MOOS](https://github.com/themoos/core-moos).

|      CI              | status |
|----------------------|--------|
| conda.recipe         | [![Conda Actions Status][actions-conda-badge]][actions-conda-link] |
| pip builds           | [![Pip Actions Status][actions-pip-badge]][actions-pip-link] |
| [`cibuildwheel`][]   | [![Wheels Actions Status][actions-wheels-badge]][actions-wheels-link] |

[actions-badge]:           https://github.com/russkel/python-moos/workflows/Tests/badge.svg
[actions-conda-link]:      https://github.com/russkel/python-moos/actions?query=workflow%3A%22Conda
[actions-conda-badge]:     https://github.com/russkel/python-moos/workflows/Conda/badge.svg
[actions-pip-link]:        https://github.com/russkel/python-moos/actions?query=workflow%3A%22Pip
[actions-pip-badge]:       https://github.com/russkel/python-moos/workflows/Pip/badge.svg
[actions-wheels-link]:     https://github.com/russkel/python-moos/actions?query=workflow%3AWheels
[actions-wheels-badge]:    https://github.com/russkel/python-moos/workflows/Wheels/badge.svg
[`cibuildwheel`]:          https://cibuildwheel.readthedocs.io

# Install from PyPI

```
python -m pip install pymoos
```

# Build Instructions
Clone the repository:

```
git clone https://github.com/russkel/python-moos.git python-moos
```

Build and install python-moos:

```
cd python-moos
python setup.py build
python setup.py install
```
