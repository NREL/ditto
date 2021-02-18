#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
from codecs import open
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from subprocess import check_call
import shlex

logger = logging.getLogger(__name__)

try:
    from pypandoc import convert_text
except ImportError:
    convert_text = lambda string, *args, **kwargs: string

here = os.path.abspath(os.path.dirname(__file__))

with open("README.md", encoding="utf-8") as readme_file:
    readme = convert_text(readme_file.read(), "rst", format="md")

with open(os.path.join(here, "ditto", "version.py"), encoding="utf-8") as f:
    version = f.read()

version = version.splitlines()[1].split()[2].strip('"').strip("'")

test_requires = [
    "backports.tempfile",
    "pytest",
    "pytest-cov",
    "sphinx-rtd-theme",
    "nbsphinx",
    "sphinxcontrib-napoleon",
    "ghp-import",
]

numpy_dependency = "numpy>=1.13.0"

extras_requires = ["lxml", "pandas", "scipy", numpy_dependency, "XlsxWriter"]

opendss_requires = ["OpenDSSDirect.py>=0.3.3", "pandas", numpy_dependency]
dew_requires = [numpy_dependency, "xlrd"]
gridlabd_requires = ["croniter", numpy_dependency]
cyme_requires = [numpy_dependency]
ephasor_requires = [numpy_dependency, "pandas"]
synergi_requires = [
    numpy_dependency,
    "pandas_access",
]  # Need pandas_access to convert the MDB tables to Pandas DataFrame


class PostDevelopCommand(develop):
    def run(self):
        try:
            check_call(shlex.split("pre-commit install"))
        except Exception as e:
            logger.warning("Unable to run 'pre-commit install'")
        develop.run(self)


setup(
    name="ditto.py",
    version=version,
    description="Distribution Feeder Conversion Tool",
    long_description=readme,
    author="Tarek Elgindy",
    author_email="tarek.elgindy@nrel.gov",
    url="https://github.com/NREL/ditto",
    packages=find_packages(),
    package_dir={"ditto": "ditto"},
    entry_points={
        "console_scripts": ["ditto=ditto.cli:cli", "ditto-cli=ditto.cli:cli"],
        "ditto.readers": [
            "gridlabd=ditto.readers.gridlabd:GridLABDReader",
            "opendss=ditto.readers.opendss:OpenDSSReader",
            "cyme=ditto.readers.cyme:CymeReader",
            "demo=ditto.readers.demo:DemoReader",
            "json=ditto.readers.json:JsonReader",
            "synergi=ditto.readers.synergi:SynergiReader",
        ],
        "ditto.writers": [
            "gridlabd=ditto.writers.gridlabd:GridLABDWriter",
            "opendss=ditto.writers.opendss:OpenDSSWriter",
            "cyme=ditto.writers.cyme:CymeWriter",
            "demo=ditto.writers.demo:DemoWriter",
            "json=ditto.writers.json:JsonWriter",
            "ephasor=ditto.writers.ephasor:EphasorWriter",
        ],
    },
    include_package_data=True,
    package_data={
        "ditto": [
            "default_values/opendss_default_values.json",
            "formats/gridlabd/schema.json",
        ]
    },
    license="BSD license",
    zip_safe=False,
    keywords="ditto",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",  # TODO: Change development status
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    install_requires=["click", "future", "networkx", "six", "traitlets>=4.1", "json_tricks"],
    extras_require={
        "all": extras_requires
        + opendss_requires
        + dew_requires
        + gridlabd_requires
        + ephasor_requires
        + cyme_requires
        + synergi_requires,
        "extras": extras_requires,
        "cyme": cyme_requires,
        "dew": dew_requires,
        "ephasor": ephasor_requires,
        "synergi": synergi_requires,
        "gridlabd": gridlabd_requires,
        "opendss": opendss_requires,
        "test": test_requires,
        "dev": test_requires + ["pypandoc", "black", "pre-commit"],
    },
    cmdclass={"develop": PostDevelopCommand},
)
