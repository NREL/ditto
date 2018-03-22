# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
import os

from pkg_resources import iter_entry_points
import click

from . import version
from .converter import Converter


registered_readers = {}
registered_writers = {}

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

    for entry_point in iter_entry_points("ditto.readers"):
        name, cls = entry_point.name, entry_point.load()
        cls.register(registered_readers)
        registered_readers[name] = cls
        # TODO: Hack! add format_name to actual reader instead
        cls.format_name = name

    for entry_point in iter_entry_points("ditto.writers"):
        name, cls = entry_point.name, entry_point.load()
        cls.register(registered_writers)
        registered_writers[name] = cls
        # TODO: Hack! add format_name to actual writer instead
        cls.format_name = name

    if kwargs["from"] not in registered_readers.keys():
        raise click.BadOptionUsage("Cannot read from format '{}'".format(kwargs["from"]))

    if kwargs["to"] not in registered_writers.keys():
        raise click.BadOptionUsage("Cannot write to format '{}'".format(kwargs["to"]))

    from_reader_name = kwargs["from"]
    to_writer_name = kwargs["to"]
    Converter(
        registered_reader_class=registered_readers[from_reader_name],
        registered_writer_class=registered_writers[to_writer_name],
        input_path=kwargs["input"],
        output_path=kwargs["output"],
    ).convert()



if __name__ == "__main__":
    cli()
