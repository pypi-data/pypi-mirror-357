#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages, setup

setup(
    name='jupyterlog',
    version='1.0.0',
    description='Setup Logging for Jupyter Notebook',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Zhiqing Xiao',
    author_email='xzq.xiaozhiqing@gmail.com',
    url='http://github.com/jupyterlog/jupyterlog',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python',
    ],
)
