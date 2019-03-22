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
@click.option("--input", type=click.Path(exists=True), help="Path to input file")
@click.option("--from", help="Convert from OpenDSS, Cyme, Gridlab-D, Demo, JSON")
@click.option(
    "--output", type=click.Path(exists=True), help="Path to the metrics output file"
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
            "Cannot read from format '{}'".format(kwargs["from"])
        )

    if kwargs["input"] is None:
        raise click.BadOptionUsage("--input must be provided.")

    from_reader_name = kwargs["from"]

    try:
        MetricComputer(
            registered_reader_class=_load(registered_readers, from_reader_name),
            input_path=kwargs["input"],
            output_format=kwargs["to"],
            output_path=kwargs["output"],
            by_feeder=kwargs["feeder"],
        ).compute()
    except Exception as e:
        # TODO: discuss whether we should raise exception here?
        sys.exit(1)  # TODO: Set error code based on exception
    else:
        sys.exit(0)


@cli.command()
@click.option("--input", type=click.Path(exists=True), help="Path to input file")
@click.option("--output", type=click.Path(exists=True), help="Path to output file")
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
@click.pass_context
def convert(ctx, **kwargs):
    """ Convert from one type to another"""

    verbose = ctx.obj["verbose"]

    if kwargs["from"] not in registered_readers.keys():
        raise click.BadOptionUsage(
            "Cannot read from format '{}'".format(kwargs["from"])
        )

    if kwargs["to"] not in registered_writers.keys():
        raise click.BadOptionUsage("Cannot write to format '{}'".format(kwargs["to"]))

    if kwargs["input"] is None or kwargs["output"] is None:
        raise click.BadOptionUsage("Both --input and --output must be provided.")

    from_reader_name = kwargs["from"]
    to_writer_name = kwargs["to"]

    if kwargs["jsonize"] is not None:
        json_path = kwargs["jsonize"]
        registered_json_writer_class = registered_writers["json"].load()
    else:
        json_path = False
        registered_json_writer_class = None

    if kwargs["default_values"] is not None:
        default_values_json = kwargs["default_values"]
    else:
        default_values_json = None

    if kwargs["remove_opendss_default_values"] is True:
        remove_opendss_default_values_flag = True
    else:
        remove_opendss_default_values_flag = False

    Converter(
        registered_reader_class=_load(registered_readers, from_reader_name),
        registered_writer_class=_load(registered_writers, to_writer_name),
        input_path=kwargs["input"],
        output_path=kwargs["output"],
        json_path=json_path,
        registered_json_writer_class=registered_json_writer_class,
        default_values_json=default_values_json,
        remove_opendss_default_values_flag=remove_opendss_default_values_flag,
    ).convert()

    sys.exit(0)


if __name__ == "__main__":
    cli()
