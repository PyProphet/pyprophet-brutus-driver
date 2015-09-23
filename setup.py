# encoding: utf-8
from __future__ import print_function


from setuptools import setup

setup(name="pyprophet-brutus-driver",
      version="0.0.8",
      author="Uwe Schmitt",
      author_email="uwe.schmitt@id.ethz.ch",
      license="BSD",
      install_requires=["pyprophet-cli"],
      entry_points={'pyprophet_cli_plugin': ['config=pyprophet_brutus.main:config']},
      include_package_data=True,
      package_dir = {'pyprophet_brutus': 'pyprophet_brutus'}
      )
