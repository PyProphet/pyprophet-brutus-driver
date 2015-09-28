# encoding: utf-8
from __future__ import print_function


from setuptools import setup, find_packages

setup(name="pyprophet-brutus",
      version="0.0.14",
      author="Uwe Schmitt",
      author_email="uwe.schmitt@id.ethz.ch",
      license="BSD",
      install_requires=["pyprophet-cli"],
      entry_points={'pyprophet_cli_plugin': ['config=pyprophet_brutus.main:config']},
      include_package_data=True,
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      )
