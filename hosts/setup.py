#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(name='wb_hosts',
      version='0.1',
      description='Atmosphere Monitoring Host Managment Service',
      author='Chris LaRose',
      author_email='cjlarose@iplantcollaborative.org',
      packages=find_packages(),
      install_requires=[
          "thrift >= 0.9.1, < 0.10",
          "pynag >= 0.8.1, < 0.9",
          "requests >= 2.2.1, < 2.3",
      ]
     )
