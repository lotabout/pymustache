#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='pymustache',
      version='0.1',
      description='Mustache template engine in python',
      url='https://github.com/lotabout/write-a-mustache-template-engine',
      author='Mark Wallace',
      author_email='lotabout@gmail.com',
      license='MIT',
      packages=['pymustache'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      )
