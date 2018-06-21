from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import os
import json
from collections import OrderedDict
import networkx as nx
from .base import GridLABDBase
from ditto.compat import common_str


def __create():
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(os.path.join(dir_path, "schema.json")) as f:
        string = f.read()

    schema = json.loads(string)
    klasses = OrderedDict()

    G = nx.DiGraph()
    for i in schema["objects"]:
        parent = schema["objects"][i]["parent"]
        if parent is not None:
            G.add_edge(parent, i)
        else:
            G.add_node(i)

    def generate_class(klass, properties, parent=None):
        if parent is None:
            parent = GridLABDBase

        return type(
            common_str(klass), (parent,), dict(_properties=properties["properties"])
        )

    for klass in nx.topological_sort(G):
        properties = schema["objects"][klass]

        if properties["parent"] is not None:
            parent = klasses[properties["parent"]]
        else:
            parent = None

        c = generate_class(klass, properties, parent=parent)
        klasses[klass] = c

    for k, c in klasses.items():
        globals()[k] = c


__create()
