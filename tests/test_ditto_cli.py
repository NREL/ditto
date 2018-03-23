import subprocess
import shlex

def test_cli():

    p = subprocess.Popen(shlex.split(""" ditto convert --from="opendss" --to="opendss" --input="./tests/data/opendss/ieee_13node/master.dss" --output="./" """.strip()))
    p.wait()
