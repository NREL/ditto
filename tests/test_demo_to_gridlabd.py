# -*- coding: utf-8 -*-
"""
test_gridlabd_to_ephasor
----------------------------------

Tests for Demo --> Gridlab-D conversion
"""
import six

if six.PY2:
    from backports import tempfile
else:
    import tempfile

import pytest as pt
import os

current_directory = os.path.realpath(os.path.dirname(__file__))
def test_demo_to_gridlabd():
    from ditto.readers.demo.read import Reader
    from ditto.store import Store
    from ditto.writers.gridlabd.write import Writer

    demo_models=[f for f in os.listdir(os.path.join(current_directory,'data/small_cases/demo/')) if not f.startswith('.')]
    for model in demo_models:
        m = Store()
        r = Reader(input_file=os.path.join(current_directory,'data/small_cases/demo',model))
        r.parse(m)
        print('>Demo model {model} read...'.format(model=os.path.join(current_directory,'data/small_cases/demo',model)))
        output_path = tempfile.TemporaryDirectory()
        w = Writer(output_path=output_path.name, log_path=output_path)
        w.write(m)
        print('>...and written to Gridlab-D.\n')
