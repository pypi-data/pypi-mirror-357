from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension

ext_modules = [
    Pybind11Extension(
        'pycmox',
        sources=['src/pycmox.cpp', 'src/infras/exchange.cpp'],
        cxx_std=11,
        include_dirs=['src/infras'],
        define_macros=[('NO_RS485_LEGACY', None)]
    )
]

setup(ext_modules=ext_modules)
