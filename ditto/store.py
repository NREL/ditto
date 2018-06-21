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
from .utils import reject_outliers
from .models.position import Position
import numpy as np

logger = logging.getLogger(__name__)


class Store(object):
    """The Store class holds all functions supported in the transformation.

    The Store stores all the instances of objects of different classes in a list

    Examples
    --------

    >>> M = ditto.Store()

    >>> M
    <ditto.Store(elements=0, models=0)>

    """

    __store_factory = dict

    def __init__(self):

        self._cim_store = self.__store_factory()
        self._model_store = list()
        self._model_names = {}
        self._network = Network()

    def __repr__(self):
        return "<%s.%s(elements=%s, models=%s) object at %s>" % (
            self.__class__.__module__,
            self.__class__.__name__,
            len(self.elements),
            len(self.models),
            hex(id(self)),
        )

    def __getitem__(self, k):
        return self._model_names[k]

    def __setitem__(self, k, v):
        self._model_names[k] = v

    def iter_elements(self, type=None):

        type = DiTToBase

        if not issubclass(type, DiTToBase):
            raise AttributeError("Unable to find {} in ditto.environment".format(type))

        for e in self.elements:
            if isinstance(e, type):
                yield e

    def compute_network_attributes_positions(self):
        """
        This function loops over the objects and update the coordinates of the NetworkAttributes objects.
        """
        #Set the names
        self.set_names()

        L = {}

        #Loop over the objects stored
        for obj in self.models:

            #If we find a Node
            if isinstance(obj,Node):

                #And we have a Network information
                if obj.network_name is not None:

                    if obj.network_name not in L:
                        L[obj.network_name] = []

                    #Find the NetworkAttributes object
                    try:
                        net_obj = self.__getitem__(obj.network_name)
                    except:
                        raise ValueError("Unknown Network {name} for Node {n}.".format(name=obj.network_name, n=obj.name))

                    #If we have some positions for the Node
                    if obj.positions is not None and len(obj.positions)>0:

                        #Then duplicate them and add them to the NetworkAttributes position list
                        for position in obj.positions:
                            if position.long is not None and position.lat is not None:
                                dup = Position(self)
                                dup.long = position.long
                                dup.lat = position.lat
                                dup.elevation = position.elevation
                                net_obj.positions.append(dup)
                                L[obj.network_name].append([position.long,position.lat])

        #At this point, we should have a list with all Nodes' positions
        #If some Nodes have strange positions like (0,0), this might cause plotting issues
        #Here, we removed outliers positions from the list
        for network_name,LL in L.items():
            print("Network {net} has initially {n} positions.".format(net=network_name, n=len(LL)))
            temp = np.array(LL)
            _,_,idx_1 = reject_outliers(temp[:,0])
            _,_,idx_2 = reject_outliers(temp[:,1])
            idx = list(set(idx_1).union(set(idx_2)))
            idx_tokeep = np.array([i for i in range(len(LL)) if i not in idx])

            avg_pos_ = np.mean(temp[idx_tokeep], axis=0)
            print(avg_pos_)
            avg_pos = Position(self)
            avg_pos.long = avg_pos_[0]
            avg_pos.lat = avg_pos_[1]
            
            #Find the NetworkAttributes object
            try:
                net_obj = self.__getitem__(network_name)
            except:
                raise ValueError("Unknown Network {name}.".format(name=network_name))

            new_position_list = []
            for k,pos in enumerate(net_obj.positions):
                if k in idx_tokeep:
                    new_position_list.append(pos)
            net_obj.positions = new_position_list
            net_obj.average_position.append(avg_pos)
            print("After removing outliers, network {net} has {n} positions.".format(net=network_name, n=len(new_position_list)))
            print(net_obj.average_position[0].__dict__)



    @property
    def elements(self):
        return list(self.cim_store[k] for k in self.cim_store)

    @property
    def models(self):
        return tuple(m for m in self.model_store)

    def remove_element(self, element):
        self._model_store.remove(element)

    def add_element(self, element):
        if not isinstance(element, DiTToBase):
            raise DiTToTypeError(
                "element must be of type DiTToBase. Please check the documentation"
            )
        else:
            element.link_model = self
            self.cim_store[element.UUID] = element

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

    def direct_from_source(self):
        ordered_nodes = self._network.bfs_order()
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
    def cim_store(self):
        return self._cim_store

    @property
    def model_store(self):
        return self._model_store

    @property
    def model_names(self):
        return self._model_names


class EnvAttributeIntercepter(object):

    def __init__(self, model):
        self.model = model
        self.generate_attributes()

    def generate_attributes(self):

        for function_name, klass in self.model._env.get_clsmembers().items():

            f = partial(model_builder, klass=klass, model=self.model)
            f.__doc__ = klass.__doc__
            f.__name__ = klass.__name__

            setattr(
                self, function_name, types.MethodType(f, self, EnvAttributeIntercepter)
            )


def model_builder(self, klass, model, *args, **kwargs):

    ic = partial(init_callback, model=model)
    ic.__name__ = init_callback.__name__

    cim_object = klass(
        init_callback=ic,
        get_callback=get_callback,
        set_callback=set_callback,
        del_callback=del_callback,
        **kwargs
    )

    return cim_object


def init_callback(self, model, **kwargs):

    self.link_model = model
    if self.UUID is None:
        self.UUID = uuid.uuid4()
    self.link_model.cim_store[self.UUID] = self


def get_callback(self, name, val):
    assert (
        self.UUID in self.link_model.cim_store
    ), "UUID {} not found in Store {}. {} attributes value is {}".format(
        self.UUID, self.link_model, name, val
    )


def set_callback(self, name, value):
    assert self.UUID in self.link_model.cim_store, "{} not found in Store {}".format(
        self.UUID, self.link_model
    )
    if isinstance(value, tuple):
        for v in value:
            assert (
                v.UUID in self.link_model.cim_store
            ), "{} not found in Store {}".format(
                self.UUID, self.link_model
            )
    else:
        assert (
            value.UUID in self.link_model.cim_store
        ), "{} not found in Store {}".format(
            self.UUID, self.link_model
        )


def del_callback(self, name, obj):
    pass
