#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

__version__ = '0.1'

setup(
    name='lloyds-scrapper',
    version=__version__,
    description='Scrapper API for Lloyds bank transactions',
    long_description=open('README.md').read(),
    license=open('LICENSE').read(),
    url='https://github.com/izidormatusov/lloyds-scrapper',
    author='Izidor Matušov',
    author_email='izidor.matusov@gmail.com',
    py_modules = ['lloyds'],
    install_requires=['mechanize'],
)
