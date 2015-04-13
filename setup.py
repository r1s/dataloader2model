#! /usr/bin/env python
from datetime import datetime

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

install_requires = [
    'Django==1.8',
    'feedparser==5.1.3'
]

version_breads = datetime.now().strftime('%y%m%d%H%M%S')
version = '0.0.1'
release = '1'

setup(name='dataloader2model',
      version='{0}-{1}-{2}'.format(version, release, version_breads),
      description="r1s's data loader to model",
      author='r1s',
      author_email='roman87.r1s@gmail.com',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      install_requires=install_requires,
      )
