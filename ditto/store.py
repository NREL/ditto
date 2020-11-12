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
import warnings
from collections import defaultdict, namedtuple
from functools import partial
from .network.network import Network

from .core import DiTToBase, DiTToTypeError
from .modify.modify import Modifier
from .models.base import DiTToHasTraits
from .models.node import Node

logger = logging.getLogger(__name__)


class Store(object):

    """The Store class holds all functions supported in the transformation.

    The Store stores all the instances of objects of different classes in a list

    Examples
    --------

    >>> M = ditto.Store()

    >>> M
    <ditto.Store(elements=0)>

    """
    def __init__(self):

        # Two-level dictionary where each elements of the same type are stored
        # together.
        # Names within each element type must be unique.
        # {element_type: {name: element}}
        self._elements = defaultdict(dict)

        self._duplicate_element_names = set()
        self._network = Network()

    def __repr__(self):
        return "<{}.{}(elements={}) object at {}>".format(
            self.__class__.__module__,
            self.__class__.__name__,
            len(self._elements),
            hex(id(self)),
        )

    def __getitem__(self, name):
        warnings.warn(
            "Store[name] is deprecated. Use Store.get_element(element_type, name) instead",
            DeprecationWarning
        )
        element = None
        for element_type, elements in self._elements.items():
            if name in elements:
                if element is not None:
                    raise DuplicateNameError(
                        f"Store[name] is not supported when the name is duplicate across element types"
                    )
                element = elements[name]

        if element is None:
            raise ElementNotFoundError

        return element

    def __setitem__(self, k, v):
        warnings.warn(
            "Store[name] = element is deprecated. Use Store.add_element(element) instead",
            DeprecationWarning
        )

        if v.name != k:
            raise Exception(f"key={k} must be the element name")

        self.add_element(v)

    def _raise_if_not_found(self, element_type, name):
        if element_type not in self._elements:
            raise ElementNotFoundError(f"{element_type} is not stored")

        if name not in self._elements[element_type]:
            raise ElementNotFoundError(f"{element_type}.{name} is not stored")

    def add_element(self, element):
        """Add an element to the store.

        Raises
        ------
        DuplicateNameError
            Raised if the element name is already stored.

        """
        if not isinstance(element, DiTToHasTraits):
            raise InvalidElementType(f"type={type(element)} cannot be added")
        if not hasattr(element, "name"):
            raise InvalidElementType(
                f"type={type(element)} cannot be added. Must define 'name' attribute."
            )

        element_type = type(element)
        elements_by_type = self._elements[element_type]
        if element.name in elements_by_type:
            raise DuplicateNameError(f"{element.name} is already stored")

        elements_by_type[element.name] = element
        element.build(self)
        logger.debug("Added %s.%s to store", element_type, element.name)

    def clear_elements(self):
        """Clear all stored elements."""
        self._elements.clear()
        logger.debug("Cleared all elements")

    def get_element(self, element_type, name):
        """Return the model.

        Parameters
        ----------
        element_type : class
            class for the requested model, such as Load
        name : str
            element name

        Returns
        -------
        DiTToHasTraits

        Raises
        ------
        ElementNotFoundError
            Raised if the element_type is not stored.

        """
        self._raise_if_not_found(element_type, name)
        return self._elements[element_type][name]

    def iter_elements(self, element_type=None, filter_func=None):
        """Iterate over all elements.

        Parameters
        ----------
        element_type : class
            If None, iterate over all elements. Otherwise, iterate over that
            type.
        filter_func : callable
            If specified, call on element and only return elements that return
            true.

        Yields
        ------
        DiTToHasTraits

        Raises
        ------
        ElementNotFoundError
            Raised if the element_type is not stored.

        """
        if element_type is not None:
            if element_type not in self._elements:
                raise ElementNotFoundError(f"{element_type} is not stored")
            elements_containers = [self._elements[element_type]]
        else:
            elements_containers = self._elements.values()

        for elements in elements_containers:
            for element in elements.values():
                if filter_func is not None and not filter_func(element):
                    logger.debug("skip %s.%s", type(element), element.name)
                    continue
                yield element

    def list_elements(self, element_type=None, filter_func=None):
        """Return a list of elements.

        Parameters
        ----------
        element_type : class
            If None, return all elements. Otherwise, return only that type.
        filter_func : callable
            If specified, call on element and only return elements that return
            true.

        Returns
        -------
        list
            list of DiTToHasTraits

        Raises
        ------
        ElementNotFoundError
            Raised if the element_type is not stored.

        """
        return list(self.iter_elements(element_type=element_type, filter_func=filter_func))

    def remove_element(self, element):
        """Remove the element from the store.

        Parameters
        ----------
        element : DiTToHasTraits

        Raises
        ------
        ElementNotFoundError
            Raised if the element is not stored.

        """
        element_type = type(element)
        self._raise_if_not_found(element_type, element.name)
        self._elements[element_type].pop(element.name)
        logger.debug("Removed %s.%s from store", element_type, element.name)

        if not self._elements[element_type]:
            self._elements.pop(element_type)
            logger.debug("Removed %s from store", element_type)

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
            ), "{} not found in Store {}".format(self.UUID, self.link_model)
    else:
        assert (
            value.UUID in self.link_model.cim_store
        ), "{} not found in Store {}".format(self.UUID, self.link_model)


def del_callback(self, name, obj):
    pass


class DuplicateNameError(Exception):
    """Raised when a duplicate name is detected."""


class ElementNotFoundError(Exception):
    """Raised when an element is not stored."""


class InvalidElementType(Exception):
    """Raised when an invalid type is used."""
