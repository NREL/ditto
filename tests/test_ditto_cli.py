import subprocess
import shlex
import six
import os
import pytest as pt

if six.PY2:
    from backports import tempfile
else:
    import tempfile

current_directory = os.path.dirname(os.path.realpath(__file__))
IS_DEBUG = True

def run_command(args: list, ignore_errors: bool = False, print_output: bool = True) -> str:
    """ Run a command and print the output after it is finished.
    :param args: list of arguments to pass to the command
    :param ignore_errors: if True, ignore errors and just return the output, if True, raise a RuntimeError containing stdout+stderr if the command fails.
    :param print_output: if True, print the output of the command to stdout
    :return: the output of the command
    :raises RuntimeError: if the command fails and ignore_errors is False
    """
    if IS_DEBUG:
        print(f"\nRunning command> {' '.join(args)}")
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_bytes = result.stdout
    err_bytes = result.stderr
    try:
        output = output_bytes.decode("utf-8", errors="replace")
        error = err_bytes.decode("utf-8", errors="replace")
    except BaseException:
        output = output_bytes.decode("ascii", errors="replace")
        error = err_bytes.decode("ascii", errors="replace")

    if result.returncode != 0 and ignore_errors is False:
        raise RuntimeError(output+"\n"+error)
    elif print_output or IS_DEBUG:
        try:
            print(output+"\n"+error)
        except UnicodeEncodeError:
            pass  # TODO try harder with these exceptions
    return output

def test_opendss_to_gridlabd_cli():

    output_path = tempfile.TemporaryDirectory()
    print(output_path.name)
    run_command(
        shlex.split(
            """ poetry run python ditto/cli.py convert --from="opendss" --to="gridlabd" --input="./tests/data/small_cases/opendss/ieee_13node/master.dss" --output="{}" """.format(
                output_path.name
            ).strip(),
        )
    )

    with open(os.path.join(output_path.name, "Model.glm")) as f:
        output = f.read().strip()
    with open(
        os.path.join(
            current_directory, "data", "ditto-validation", "opendss2gridlabd-13node.glm"
        )
    ) as f:
        compare = f.read().strip()
    # for l in output.splitlines():
    # assert l in compare, "Output from OpenDSS 2 GridLAB-D conversion does not match previous output. Please update test case or contact developers."
    # for l in compare.splitlines():
    # assert l in output, "Output from OpenDSS 2 GridLAB-D conversion does not match previous output. Please update test case or contact developers."
    # assert(output.strip() == compare.strip())


def test_gridlabd_to_opendss_cli():

    output_path = tempfile.TemporaryDirectory()
    run_command(
        shlex.split(
            """ poetry run ditto-cli convert --from="gridlabd" --to="opendss" --input="./tests/data/small_cases/gridlabd/ieee_4node/node.glm" --output="{}" """.format(
                output_path.name
            ).strip()
        )
    )


def test_opendss_to_ephasor_cli():
    output_path = tempfile.TemporaryDirectory()
    run_command(
        shlex.split(
            """poetry run ditto-cli convert --from="opendss" --to="ephasor" --input="./tests/data/small_cases/opendss/ieee_13node/master.dss" --output="{}" """.format(
                output_path.name
            ).strip()
        )
    )


@pt.mark.skip()  # currently not running...
def test_metric_computation_cli():
    """Tests metric computation from command line interface
    TODO: Add better tests that check the metric values and compare them with ground truth.
    """
    output_path = tempfile.TemporaryDirectory()
    run_command(
        shlex.split(
            """ poetry run ditto-cli metric --from="opendss" --to="xlsx" --input="./read_dss_13node.json" --feeder=False --output="{}" """.format(
                output_path.name
            ).strip()
        )
    )
