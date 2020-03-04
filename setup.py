#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='tht',
      version='0.1',
      description='Tactus Hypothesis Tracking Module',
      author='Martin "March" Miguel',
      author_email='m2.march@gmail.com',
      packages=find_packages(),
      namespace_packages=['m2'],
      install_requires=[
          'addict',
          'pytest-mock',
          'numpy',
          'more_itertools',
          'pytest',
          'filetype',
          'pandas',
          'scipy'
      ]
      )
