import subprocess
import shlex
import six
import os

if six.PY2:
    from backports import tempfile
else:
    import tempfile

def test_opendss_to_gridlabd_cli():

    output_path = tempfile.TemporaryDirectory()
    p = subprocess.Popen(shlex.split(""" ditto convert --from="opendss" --to="gridlabd" --input="./tests/data/small_cases/opendss/ieee_13node/master.dss" --output="{}" """.format(output_path.name).strip()))
    p.wait()
    # with open(os.path.join(output_path.name, "Model.glm")) as f:
        # print(f.read())
    if p.returncode != 0:
        raise Exception("Error with {}".format(p.returncode))

def test_gridlabd_to_opendss_cli():

    output_path = tempfile.TemporaryDirectory()
    p = subprocess.Popen(shlex.split(""" ditto convert --from="gridlabd" --to="opendss" --input="./tests/data/small_cases/gridlabd/4node.glm" --output="{}" """.format(output_path.name).strip()))
    p.wait()
    if p.returncode != 0:
        raise Exception("Error in ditto cli: {}".format(p.returncode))

