# -*- coding: utf-8 -*-
"""This is the module that defines a Store class

This module details all supported functions on the Store, as described in the specification.
This Store will behave as the interface between the core and the plugin interface

Example
-------

    >>> from ditto.model import Store


Notes
-----

Store stores all the instances of objects required for a transformation

"""

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import uuid
import logging
import types
from functools import partial
from .network.network import Network

from .core import DiTToBase, DiTToTypeError
from .modify.modify import Modifier
from .models.node import Node

logger = logging.getLogger(__name__)


class Store(object):
    """The Store class holds all functions supported in the transformation.

    The Store stores all the instances of objects of different classes in a list

    Examples
    --------

    >>> M = ditto.Store()

    >>> M
    <ditto.Store(models=0)>

    """

    def __init__(self):

        self._model_store = list()
        self._model_names = {}
        self._network = Network()

    def __repr__(self):
        return "<%s.%s(models=%s) object at %s>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            len(self.models),
            hex(id(self)),
        )

    def __getitem__(self, k):
        return self._model_names[k]

    def __setitem__(self, k, v):
        self._model_names[k] = v

    def iter_models(self, type=None):

        if type == None:
            type = object

        for m in self.models:
            if isinstance(m, type):
                yield m

    @property
    def models(self):
        return tuple(m for m in self.model_store)

    def remove_element(self, element):
        self._model_store.remove(element)

    def set_names(self):
        """ All objects with a name field included in a dictionary which maps the name to the object. Set in set_name() on the object itself if the object has a name. The dictionary is reset to empty first"""
        self._model_names = {}
        for m in self.models:
            m.set_name(self)

    def build_networkx(self, source=None):
        if source is not None:
            self._network.build(self, source)
        else:
            self._network.build(self)
        self._network.set_attributes(self)

    def print_networkx(self):
        logger.debug("Printing Nodes...")
        self._network.print_nodes()
        logger.debug("Printing Edges...")
        self._network.print_edges()
        # logger.debug('Printing Attributes...')
        # self._network.print_attrs()

    def delete_cycles(self):
        """ First convert graph to directed graph (doubles the edges hence creating length 2 cycles)
        Then find cycles of length greater than 2
        Use heuristic of removing edge in the middle of the longest single phase section of the loop
        If no single phase sections, remove edge the furthest from the source
        """
        for i in self._network.find_cycles():
            if len(i) > 2:
                logger.debug("Detected cycle {cycle}".format(cycle=i))
                edge = self._network.middle_single_phase(i)
                for j in self.models:
                    if hasattr(j, "name") and j.name == edge:
                        logger.debug("deleting " + edge)
                        modifier = Modifier()
                        modifier.delete_element(self, j)
        self.build_networkx()

    def direct_from_source(self, source="sourcebus"):
        ordered_nodes = self._network.bfs_order(source)
        # logger.debug(ordered_nodes)
        for i in self.models:
            if (
                hasattr(i, "from_element")
                and i.from_element is not None
                and hasattr(i, "to_element")
                and i.to_element is not None
            ):
                original = (i.from_element, i.to_element)
                flipped = (i.to_element, i.from_element)
                if flipped in ordered_nodes and (
                    not original in ordered_nodes
                ):  # i.e. to cover the case where lines go both ways
                    tmp = i.from_element
                    i.from_element = i.to_element
                    i.to_element = tmp

    def delete_disconnected_nodes(self):
        for i in self.models:
            if isinstance(i, Node) and hasattr(i, "name") and i.name is not None:
                connected_nodes = self._network.get_nodes()
                if not i.name in connected_nodes:
                    logger.debug("deleting " + i.name)
                    modifier = Modifier()
                    modifier.delete_element(self, i)

            if isinstance(i, Node) and hasattr(i, "name") and i.name is None:
                self.remove_element(i)
        self.build_networkx()  # Should be redundant since the networkx graph is only build on connected elements

    def set_node_voltages(self):
        self.set_names()
        for i in self.models:
            if isinstance(i, Node) and hasattr(i, "name") and i.name is not None:
                upstream_transformer = self._network.get_upstream_transformer(
                    self, i.name
                )
                try:
                    upstream_voltage = (
                        self[upstream_transformer].windings[-1].nominal_voltage
                    )
                    i.nominal_voltage = upstream_voltage
                except KeyError:
                    pass

    def get_internal_edges(self, nodeset):
        return self._network.find_internal_edges(nodeset)

    @property
    def model_store(self):
        return self._model_store

    @property
    def model_names(self):
        return self._model_names
