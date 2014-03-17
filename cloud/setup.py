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
          'thrift >= 0.9.1, < 0.10',
          'SQLAlchemy >= 0.8.2, < 0.9',
          'pytz == 2013d',
          'python-ldap >= 2.4, < 2.5',
          'requests == 2.2',
          'rtwo >= 0.1.8, < 0.2',
          'psycopg2 >= 2.5.2, < 2.6',
      ],
      dependency_links=[
          'git+https://github.com/iPlantCollaborativeOpenSource/rtwo.git@master#egg=rtwo-0.1.8',
          'git+https://github.com/jmatt/threepio.git@master#egg=threepio-0.1.2',
      ]
     )
