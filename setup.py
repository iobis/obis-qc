from setuptools import setup, find_packages

setup(name="obisqc",
      version="0.0.3",
      url="https://github.com/iobis/obis-qc",
      license="MIT",
      author="Pieter Provoost",
      author_email="p.provoost@unesco.org",
      description="OBIS QC checks",
      packages=find_packages(),
      zip_safe=False)