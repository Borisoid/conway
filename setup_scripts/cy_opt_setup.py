from setuptools import setup
from Cython.Build import cythonize


setup(
    ext_modules=cythonize(["cython_source/cy_opt_cellular.pyx"], build_dir="build/cython", annotate=True)
)
