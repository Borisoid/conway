from glob import glob
from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension

ext_modules = [
    Pybind11Extension(
        "pybind11_opt_cellular",
        sorted(glob("ccpp_source/pybind11_opt.cpp")),  # Sort source files for reproducibility
    ),
]

setup(ext_modules=ext_modules)
