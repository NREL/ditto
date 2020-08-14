# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
import os
import sys

from pkg_resources import iter_entry_points
import click

from . import version
from .converter import Converter

try:
    from .metric_computer import MetricComputer
except ImportError:
    MetricComputer = None

registered_readers = {}
registered_writers = {}


def _register():

    for entry_point in iter_entry_points("ditto.readers"):
        name, cls = entry_point.name, entry_point
        registered_readers[name] = cls

    for entry_point in iter_entry_points("ditto.writers"):
        name, cls = entry_point.name, entry_point
        registered_writers[name] = cls


def _load(plugins, name):

    cls = plugins[name].load()
    # TODO: Hack! add format_name to actual reader instead
    cls.format_name = name
    return cls


@click.group()
@click.version_option(version.__version__, "--version")
@click.option("--verbose", "-v", is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.obj = {}
    ctx.obj["verbose"] = verbose
    _register()


@cli.command()
@click.option("--readers", is_flag=True, help="List all available readers")
@click.option("--writers", is_flag=True, help="List all available writers")
@click.pass_context
def list(ctx, readers, writers):
    if not readers and not writers:
        readers = True
        writers = True

    click.echo("List of available plugins:")
    reader_names = []
    if readers is True:
        for name, _ in registered_readers.items():
            reader_names.append(name)
        click.echo("Readers: ", nl=False)
        [click.echo("'{}', ".format(name), nl=False) for name in reader_names[:-1]]
        [click.echo("'{}'".format(name), nl=True) for name in reader_names[-1:]]

    writer_names = []
    if writers is True:
        for name, _ in registered_writers.items():
            writer_names.append(name)
        click.echo("Writers: ", nl=False)
        [click.echo("'{}', ".format(name), nl=False) for name in writer_names[:-1]]
        [click.echo("'{}'".format(name), nl=True) for name in writer_names[-1:]]


@cli.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Path to input file",
)
@click.option("--from", help="Convert from OpenDSS, Cyme, Gridlab-D, Demo, JSON")
@click.option(
    "--output",
    type=click.Path(exists=True),
    required=True,
    help="Metrics output directory",
)
@click.option("--to", help="Format for the metrics output file. xlsx or json")
@click.option(
    "--feeder",
    default=True,
    type=bool,
    help="If True computes metrics per feeder. Otherwise, compute metrics at the system level.",
)
@click.pass_context
def metric(ctx, **kwargs):
    """Compute metrics"""

    verbose = ctx.obj["verbose"]

    if kwargs["from"] not in registered_readers.keys():
        raise click.BadOptionUsage(
            "from",
            "Cannot read from format '{}'".format(kwargs["from"])
        )

    MetricComputer(
        registered_reader_class=_load(registered_readers, kwargs["from"]),
        input_path=kwargs["input"],
        output_format=kwargs["to"],
        output_path=kwargs["output"],
        by_feeder=kwargs["feeder"],
    ).compute()


@cli.command()
@click.option(
    "--input",
    type=click.Path(exists=True),
    required=True,
    help="Path to input file",
)
@click.option(
    "--output",
    type=click.Path(exists=True),
    required=True,
    help="Output directory",
)
@click.option("--from", help="Convert from OpenDSS, Cyme, GridLAB-D, Demo")
@click.option("--to", help="Convert to OpenDSS, Cyme, GridLAB-D, Demo")
@click.option(
    "--jsonize",
    type=click.Path(exists=True),
    help="Serialize the DiTTo representation to the specified path",
)
@click.option("--default_values", help="Provide default values")
@click.option(
    "--remove_opendss_default_values", is_flag=True, help="Remove default values"
)
@click.option(
    "--warehouse", type=click.Path(exists=True), help="Path to synergi warehouse file"
)
@click.pass_context
def convert(ctx, **kwargs):
    """ Convert from one type to another"""

    verbose = ctx.obj["verbose"]

    if kwargs["from"] not in registered_readers.keys():
        raise click.BadOptionUsage(
            "from",
            "Cannot read from format '{}'".format(kwargs["from"])
        )

    if kwargs["to"] not in registered_writers.keys():
        raise click.BadOptionUsage(
            "to",
            "Cannot write to format '{}'".format(kwargs["to"])
        )

    if kwargs["jsonize"] is not None:
        json_path = kwargs["jsonize"]
        registered_json_writer_class = registered_writers["json"].load()
    else:
        json_path = False
        registered_json_writer_class = None

    Converter(
        registered_reader_class=_load(registered_readers, kwargs["from"]),
        registered_writer_class=_load(registered_writers, kwargs["to"]),
        input_path=kwargs["input"],
        output_path=kwargs["output"],
        json_path=json_path,
        registered_json_writer_class=registered_json_writer_class,
        default_values_json=kwargs["default_values"],
        remove_opendss_default_values_flag=kwargs["remove_opendss_default_values"],
        synergi_warehouse_path=kwargs["warehouse"],
    ).convert()


if __name__ == "__main__":
    cli()
