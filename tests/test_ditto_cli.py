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


def test_opendss_to_gridlabd_cli():

    output_path = tempfile.TemporaryDirectory()
    print(output_path.name)
    p = subprocess.Popen(
        shlex.split(
            """ ditto-cli convert --from="opendss" --to="gridlabd" --input="./tests/data/small_cases/opendss/ieee_13node/master.dss" --output="{}" """.format(
                output_path.name
            ).strip()
        )
    )
    p.wait()
    with open(os.path.join(output_path.name, "Model.glm")) as f:
        output = f.read().strip()
    with open(
        os.path.join(
            current_directory, "data", "ditto-validation", "opendss2gridlabd-13node.glm"
        )
    ) as f:
        compare = f.read().strip()
    if p.returncode != 0:
        raise Exception("Error with {}".format(p.returncode))
    # for l in output.splitlines():
    # assert l in compare, "Output from OpenDSS 2 GridLAB-D conversion does not match previous output. Please update test case or contact developers."
    # for l in compare.splitlines():
    # assert l in output, "Output from OpenDSS 2 GridLAB-D conversion does not match previous output. Please update test case or contact developers."
    # assert(output.strip() == compare.strip())


def test_gridlabd_to_opendss_cli():

    output_path = tempfile.TemporaryDirectory()
    p = subprocess.Popen(
        shlex.split(
            """ ditto-cli convert --from="gridlabd" --to="opendss" --input="./tests/data/small_cases/gridlabd/4node.glm" --output="{}" """.format(
                output_path.name
            ).strip()
        )
    )
    p.wait()
    if p.returncode != 0:
        raise Exception("Error in ditto cli: {}".format(p.returncode))


def test_opendss_to_ephasor_cli():
    output_path = tempfile.TemporaryDirectory()
    p = subprocess.Popen(
        shlex.split(
            """ditto-cli convert --from="opendss" --to="ephasor" --input="./tests/data/small_cases/opendss/ieee_13node/master.dss" --output="{}" """.format(
                output_path.name
            ).strip()
        )
    )
    p.wait()
    if p.returncode != 0:
        raise Exception("Error in ditto cli: {}".format(p.returncode))


@pt.mark.skip()  # currently not running...
def test_metric_computation_cli():
    """Tests metric computation from command line interface
    TODO: Add better tests that check the metric values and compare them with ground truth.
    """
    output_path = tempfile.TemporaryDirectory()
    p = subprocess.Popen(
        shlex.split(
            """ ditto-cli metric --from="opendss" --to="xlsx" --input="./tests/read_dss_13node.json" --feeder=False --output="{}" """.format(
                output_path.name
            ).strip()
        )
    )
    p.wait()
    if p.returncode != 0:
        raise Exception("Error in ditto cli: {}".format(p.returncode))
