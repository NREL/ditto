#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

try:
    from pypandoc import convert_text
except ImportError:
    convert_text = lambda string, *args, **kwargs: string

here = os.path.abspath(os.path.dirname(__file__))

with open('README.md') as readme_file:
    readme = convert_text(readme_file.read(), 'rst', format='md')

with open('HISTORY.md') as history_file:
    history = convert_text(history_file.read(), 'rst', format='md')

setup(
    name='ditto',
    version='0.1.0',
    description="Distribution Feeder Conversion Tool",
    long_description=readme + '\n\n' + history,
    author="Tarek Elgindy",
    author_email='tarek.elgindy@nrel.gov',
    url='https://github.com/NREL/ditto',
    packages=find_packages(),
    package_dir={'ditto': 'ditto'},
    entry_points={'console_scripts': ['ditto=ditto.cli:cli']},
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
        "fuzzywuzzy",
        "jinja2",
        "lxml",
        "networkx",
        "OpenDSSDirect.py",
        "pandas",
        "pytest",
        "six",
        "xlrd"
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "sphinx-rtd-theme",
            "nbsphinx",
            "sphinxcontrib-napoleon",
            "ghp-import",
        ]
    },
)
