"""
test_lines_write.py
----------------------------------

Tests for writing Line objects from DiTTo to OpenDSS.
"""

import os
import pytest
import tempfile
import json

from ditto.store import Store
from ditto.writers.opendss.write import Writer
from ditto.readers.opendss.read import Reader
from ditto.writers.json.write import Writer as Json_Writer

current_directory = os.path.realpath(os.path.dirname(__file__))


def test_lines_write():
    m = Store()

    r = Reader(
        master_file=os.path.join(
            current_directory, "../../../readers/opendss/Lines/test_linegeometries.dss"
        )
    )
    r.parse(m)
    m.set_names()

    output_path = tempfile.gettempdir()
    jw = Json_Writer(output_path=output_path)
    jw.write(m)

    w = Writer(output_path=output_path)
    w.write(m)

    # Check that the OpenDSS writer created a Master file
    assert os.path.exists(os.path.join(output_path, "Master.dss"))

    r_w = Reader(master_file=os.path.join(output_path, "Master.dss"))
    r_w.parse(m)
    m.set_names()

    jw = Json_Writer(output_path="./")
    jw.write(m)

    with open(os.path.join(output_path, "Model.json"), "r") as f1:
        reader_json = json.load(f1)
    with open("./Model.json", "r") as f2:
        writer_json = json.load(f2)

    assert reader_json["model"] == writer_json["model"]
