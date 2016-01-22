#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

setup(name='pymustache',
      version='0.1',
      description='Mustache template engine in python',
      url='https://github.com/lotabout/write-a-mustache-template-engine',
      download_url = 'https://github.com/lotabout/write-a-mustache-template-engine/archive/v0.1.tar.gz',
      author='Mark Wallace',
      author_email='lotabout@gmail.com',
      license='MIT',
      packages=['pymustache'],
      keywords = ['mustache', 'template engine'],
      zip_safe=False,
      include_package_data = True,
      test_suite='nose.collector',
      tests_require=['nose'],
      )
