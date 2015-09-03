# encoding: utf-8
from __future__ import print_function


from setuptools import setup

setup(name="pyprophet-brutus-drive-eth",
      version="0.0.1",
      author="Uwe Schmitt",
      author_email="uwe.schmitt@id.ethz.ch",
      license="BSD",
      install_requires=["pyprophet-cli"],
      entry_points={'pyprophet_cli_plugin': ['config=main:config']},
      include_package_data=True,
      packages=["."],
      )
