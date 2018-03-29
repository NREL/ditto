import subprocess
import shlex
import six

if six.PY2:
    from backports import tempfile
else:
    import tempfile

def test_cli():

    output_path = tempfile.TemporaryDirectory()
    p = subprocess.Popen(shlex.split(""" ditto convert --from="opendss" --to="opendss" --input="./tests/data/small_cases/opendss/ieee_13node/master.dss" --output="{}" """.format(output_path.name).strip()))
    p.wait()
