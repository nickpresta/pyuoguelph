#!/usr/bin/env python
#-*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name="pyuoguelph",
    license="BSD",
    version="0.0.3",
    description="Python bindings to University of Guelph services",
    author="Nick Presta",
    maintainer="Nick Presta",
    maintainer_email="nick@nickpresta.ca",
    url="https://github.com/NickPresta/pyuoguelph",
    packages=['pyuoguelph', 'pyuoguelph.tests'],
    install_requires=['bs4', 'requests'],
    )
