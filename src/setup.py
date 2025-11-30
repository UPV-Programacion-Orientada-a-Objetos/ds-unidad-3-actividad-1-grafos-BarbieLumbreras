from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "grafo",
        ["grafo.pyx", "GrafoDisperso.cpp"],
        language="c++",
    )
]

setup(
    name="grafo",
    ext_modules=cythonize(extensions),
)
