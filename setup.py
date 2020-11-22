from setuptools import setup

# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from pybind11 import get_cmake_dir

import sys

__version__ = "2020.1"

ext_modules = [
    Pybind11Extension("pymoos",
        ["src/pyMOOS.cpp"],
        # Example: passing in the version to the compiled code
        define_macros = [('VERSION_INFO', __version__)],
        ),
]

setup(
    name="pymoos",
    version=__version__,
    author='Mohamed Saad Ibn Seddik',
    author_email='ms.ibnseddik@gmail.com',
    description='MOOS python wrapper.',
    long_description='',
    url="https://github.com/russkel/python-moos",
    long_description="",
    ext_modules=ext_modules,
    extras_require={"test": "pytest"},
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
