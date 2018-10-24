import six
if six.PY2:
    from backports import tempfile
else:
    import tempfile

import pytest as pt
import os
from ditto.readers.opendss.read import Reader as Reader_opendss
from ditto.readers.cyme.read import Reader as Reader_cyme
from ditto.writers.json.write import Writer
from ditto.store import Store
import logging
import json

logger = logging.getLogger(__name__)
test_list = os.walk('data')
for (dirpath, dirname, files) in test_list:
    if files !=[]:
        reader_type = dirpath.split('\\')[2]
        m = Store()
        if reader_type == 'opendss':
            reader = Reader_opendss(master_file = os.path.join('..',dirpath,'master.dss'), buscoordinates_file = os.path.join('..',dirpath,'buscoord.dss'))
        elif reader_type == 'cyme':
            reader = Reader_cyme(data_folder_path=os.path.join('..',dirpath))
        else:
            #Update with other tests if they get added to the persistence tests
            continue
        reader.parse(m)
        m.set_names()
        output_path = tempfile.TemporaryDirectory()
        w = Writer(output_path=output_path.name, log_path=output_path)
        w.write(m)
        original = json.load(open(os.path.join(dirpath,files[0]),'r'))
        update = json.load(open(os.path.join(output_path.name,'Model.json'),'r'))
        try:
            assert update == original
        except AssertionError as e:
            logger.error("Model differs for usecase {loc}".format(loc = dirpath))
            e.args += ("Model differs for usecase {loc}".format(loc = dirpath),)
            raise

