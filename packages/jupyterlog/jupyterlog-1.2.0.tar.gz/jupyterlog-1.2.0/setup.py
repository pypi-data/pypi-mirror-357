#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
import jupyterlog  # noqa: F401

setup(
    name='jupyterlog',
    version='1.2.0',
    description='Setup Logging for Jupyter Notebook',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Zhiqing Xiao',
    author_email='xzq.xiaozhiqing@gmail.com',
    url='http://github.com/jupyterlog/jupyterlog',
    py_modules=["jupyterlog"],
    include_package_data=True,
    license="MIT",
    classifiers=[
        'Programming Language :: Python',
    ],
)
