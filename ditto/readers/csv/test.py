from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import logging
from read import Reader
from ditto.store import Store

logger = logging.getLogger(__name__)

m = Store()
reader = Reader()
reader.parse(m, "test_input.csv")
for i in m.models:
    logger.debug(i)

for obj_name in m.model_names:
    logger.debug(obj_name)

for i in m.model_names["load1"].traits():
    # logger.debug(i,type(m.model_names['load1'].traits()[i]))
    class_name = (
        str(type(m.model_names["load1"].traits()[i])).strip("<>'").split(".")[-1]
    )
    if class_name == "List":
        logger.debug(m.model_names["load1"].traits()[i]._trait.klass)
