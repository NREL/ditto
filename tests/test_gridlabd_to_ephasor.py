# -*- coding: utf-8 -*-
"""
test_gridlabd_to_ephasor
----------------------------------

Tests for GridlabD --> Ephasor conversion
"""
import six

if six.PY2:
    from backports import tempfile
else:
    import tempfile

import pytest as pt
import os

current_directory = os.path.realpath(os.path.dirname(__file__))

@pt.mark.skip() #currently not running...
def test_gridlabd_to_ephasor():
    from ditto.readers.gridlabd.read import Reader
    from ditto.store import Store
    from ditto.writers.ephasor.write import Writer

    gridlabd_models=[f for f in os.listdir(os.path.join(current_directory,'data/small_cases/gridlabd/')) if not f.startswith('.')]
    for model in gridlabd_models:
        m = Store()
        r = Reader()
        r.parse(m)
        #TODO: Log properly
        print('>Gridlab-D model {model} read...'.format(model=model))
        output_path = tempfile.TemporaryDirectory()
        w = Writer(output_path=output_path.name, log_path=output_path)
        w.write(m)
        #TODO: Log properly
        print('>...and written to Ephasorsim.\n')
