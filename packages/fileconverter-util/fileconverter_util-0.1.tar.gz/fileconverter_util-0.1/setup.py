from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "fileconverter_util",
        ["src/bindings.cpp"],
        cxx_std=20,
    ),
]

setup(
    name="fileconverter_util",
    version="0.1",
    author="Vasu Jayendra",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
