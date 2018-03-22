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
@click.option('--verbose', '-v', is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.obj = {}
    ctx.obj['verbose'] = verbose


@cli.command()
@click.option("--input", type=click.Path(exists=True), help="Path to input file")
@click.option("--output", type=click.Path(exists=True), help="Path to output file")
@click.option("--from", help="Convert from OpenDSS, Cyme, GridLAB-D")
@click.option("--to", help="Convert to OpenDSS, Cyme, GridLAB-D")
@click.pass_context
def convert(ctx, **kwargs):
    """ Convert from one type to another"""

    verbose = ctx.obj["verbose"]

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

    if kwargs["input"] is None or kwargs["output"] is None:
        raise click.BadOptionUsage("Both --input and --output must be provided.")

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
