#!/usr/bin/env python

from distutils.core import setup

setup(name='tht',
      version='0.1',
      description='Tactus Hypothesis Tracking Module',
      author='Martin "March" Miguel',
      author_email='m2.march@gmail.com',
      packages=['tht'],
      requires=[
          'numpy',
          'more_itertools',
          'py.test'
      ]
      )
