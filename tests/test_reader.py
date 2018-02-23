# -*- coding: utf-8 -*-

"""
test_reader
----------------------------------

Tests for `ditto` module readers
"""
import os

from ditto.readers.gridlabd.read import reader
from ditto.store import Store
from tests import ditto_dir

gridlabd_models_dir = os.path.join(ditto_dir,'readers','gridlabd')
gridlabd_models = ['13node_simplified.glm',
                   '4node.glm']

def test_gld_reader():
    for modelfile in gridlabd_models:
        m = Store()
        r = reader()
        r.parse(m, os.path.join(gridlabd_models_dir,modelfile))

