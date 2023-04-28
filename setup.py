from setuptools import setup, find_packages

setup(name="obisqc",
      version="0.12.0",
      python_requires=">=3.6",
      url="https://github.com/iobis/obis-qc",
      license="MIT",
      author="Pieter Provoost",
      author_email="p.provoost@unesco.org",
      description="OBIS QC checks",
      packages=find_packages(),
      zip_safe=False)
