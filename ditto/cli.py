# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
import click
import os
from . import version
from .readers.readers import registered_readers


@click.group()
@click.version_option(version.__version__, '--version')
def cli():
    pass


@cli.command()
@click.option("--input", type=click.Path(exists=True), help="Path to input file")
@click.option("--output", type=click.Path(), help="Path to output file")
@click.option("--from", help="Convert from OpenDSS, Cyme, GridLAB-D")
@click.option("--to", help="Convert to OpenDSS, Cyme, GridLAB-D")
def convert(**kwargs):
    """ Convert from one type to another"""
    print(kwargs)
    if not kwargs["from"] in registered_readers.keys():
        raise NotImplementedError("Cannot read from format '{}'".format(kwargs["from"]))




if __name__ == "__main__":
    cli()
