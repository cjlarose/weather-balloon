#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(name='wb_cloud',
      version='0.1',
      description='Atmosphere Monitoring Cloud Managment Service',
      author='Chris LaRose',
      author_email='cjlarose@iplantcollaborative.org',
      packages=find_packages(),
      install_requires=[
          "thrift >= 0.9.1, < 0.10"
      ]
     )
