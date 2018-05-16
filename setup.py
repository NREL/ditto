#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from codecs import open
from setuptools import setup, find_packages

try:
    from pypandoc import convert_text
except ImportError:
    convert_text = lambda string, *args, **kwargs: string

here = os.path.abspath(os.path.dirname(__file__))

with open('README.md') as readme_file:
    readme = convert_text(readme_file.read(), 'rst', format='md')

with open(os.path.join(here, 'ditto', 'version.py'), encoding='utf-8') as f:
    version = f.read()

version = version.split()[2].strip('"').strip("'")

setup(
    name='ditto',
    version=version,
    description="Distribution Feeder Conversion Tool",
    long_description=readme,
    author="Tarek Elgindy",
    author_email='tarek.elgindy@nrel.gov',
    url='https://github.com/NREL/ditto',
    packages=find_packages(),
    package_dir={'ditto': 'ditto'},
    entry_points={
        "console_scripts": [
            "ditto=ditto.cli:cli",
            "ditto-cli=ditto.cli:cli"
        ],
        "ditto.readers": [
            "gridlabd=ditto.readers.gridlabd:GridLABDReader",
            "opendss=ditto.readers.opendss:OpenDSSReader",
            "cyme=ditto.readers.cyme:CymeReader",
            "demo=ditto.readers.demo:DemoReader"
        ],
        "ditto.writers": [
            "gridlabd=ditto.writers.gridlabd:GridLABDWriter",
            "opendss=ditto.writers.opendss:OpenDSSWriter",
            "cyme=ditto.writers.cyme:CymeWriter",
            "demo=ditto.writers.demo:DemoWriter"
        ],
    },
    include_package_data=True,
    license="BSD license",
    zip_safe=False,
    keywords='ditto',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha', # TODO: Change development status
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    install_requires=[
        "aenum",
        "click",
        "croniter",
        "funcsigs",
        "future",
        "jinja2",
        "lxml",
        "networkx",
        "pandas",
        "pytest",
        "six",
        "xlrd",
        "OpenDSSDirect.py",
        "XlsxWriter",
        "json_tricks",
        "scipy",
    ],
    extras_require={
        "dev": [
            "backports.tempfile",
            "pytest",
            "pytest-cov",
            "sphinx-rtd-theme",
            "nbsphinx",
            "sphinxcontrib-napoleon",
            "ghp-import",
        ]
    },
)
