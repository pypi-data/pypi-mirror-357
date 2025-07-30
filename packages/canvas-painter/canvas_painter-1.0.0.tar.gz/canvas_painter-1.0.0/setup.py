from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import os

sfml_include = r"C:\Libraries\SFML-2.5.1\include"
sfml_lib = r"C:\Libraries\SFML-2.5.1\lib"

ext_modules = [
    Pybind11Extension(
        "canvas_painter_windows",
        ["src/bindings.cpp"],
        include_dirs=[sfml_include],
        library_dirs=[sfml_lib],
        libraries=["sfml-graphics", "sfml-window", "sfml-system"],
        language="c++",
    ),
]

setup(
    name="canvas_painter_windows",
    version="0.1.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
)