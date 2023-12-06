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
    >>> M.add_element(ditto.Line(name='my_line'))
    >>> M
    <ditto.Store(models=1)>

    """

    def __init__(self):
        """Store constructor.
         self._elements is a two-level dictionary which stores all the elements being represented in a model.
         The first level of the dictionary is keyed by the element types, which map to a dictionary.
         The second level of the dictionary is keyed by the element names, which map to a list of objects.
         The names within each element type should be unique, resulting in lists of length 1.
         {element_type: {element_name: [element_object]}}

         self._network is a Network object which stores the networkx graph representation of the model.
         """ 

        self._elements = defaultdict(dict)
        self._network = Network()

    def __repr__(self):
        """Representation of the Store object. Includes count of the number of elements in the Store.
         self._elements has the form {element_type: {element_name: [element_object]}}
        Elements with duplicate names are considered to be separate elements.
        """
        num_elements = 0
        for k, v in self._elements.items():
            num_elements += len(len(v))
        return "{}.{}(elements={})".format(
            self.__class__.__module__,
            self.__class__.__name__,
            num_elements
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
                if len(elements[name]) > 1:
                    raise DuplicateNameError(
                        f"Store[name] is not supported when the name is duplicate within an element type"
                    )    
                element = elements[name][0]

        if element is None:
            raise ElementNotFoundError

        return element

    def __setitem__(self, name, element):
        warnings.warn(
            "Store[name] = element is deprecated. Use Store.add_element(element) instead",
            DeprecationWarning
        )

        if element.name != name
            raise Exception(f"key={name} must be the element name")

        self.add_element(element)

    def _raise_if_not_found(self, element_type, name):
        if element_type not in self._elements:
            raise ElementNotFoundError(f"{element_type} is not stored")

        if name not in self._elements[element_type]:
            raise ElementNotFoundError(f"{element_type}.{name} is not stored")
        self._model_names[k] = v

    def add_element(self, element):    
        """Add an element to the Store.

        Parameters
        ----------
        element : object
            The element to be added to the Store. Must be a subclass of DiTToHasTraits.

        Returns
        -------
        None

        """
        if not isinstance(element, DiTToHasTraits):
            raise InvalidElementType(f"type={type(element)} cannot be added")
        if not hasattr(element, "name"):
            raise InvalidElementType(f"type={type(element)} cannot be added. Must define 'name' attribute.")

        element_type = type(element)
        elements_by_type = self._elements[element_type]
        element_name_list = []
        if element.name in elements_by_type:
            logger.warning(f"Warning: {element_type}.{element.name} already exists. Adding duplicate.")
            element_name_list = elements_by_type[element.name]

        element_name_list.append(element)
        elements_by_type[element.name] = element_name_list
        element.build(self)
        logger.debug(f"added {element_type}.{element.name}")

    def clear_elements(self):
        """Clear all stored elements."""
        self._elements.clear()
        logger.debug("Cleared all elements")

    def get_elements(self, element_type, name):
        """Return an list of elements from the that match the element_type and name parameters.
        Parameters
        ----------
        element_type : class
            class for the requested model, such as Load
        name : str
            element name
        Returns
        -------
        [DiTToHasTraits,..]
        Raises
        ------
        ElementNotFoundError
            Raised if the element_type is not stored.
        """
        self._raise_if_not_found(element_type, name)
        if len(self._elements[element_type][name]) > 1:
            logger.warning(f"Warning: {element_type}.{name} is duplicated. Returning all.")
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

        for element_names in elements_containers:
            for element_list in element_names.values():
                for element in element_list:
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
        """Remove all elements that match the parameter type and name from the store.
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
        if len(self._elements[element_type][element.name]) > 1:
            logger.warning(f"Warning: {element_type}.{element.name} is duplicated. Removing all.")
        self._elements[element_type].pop(element.name)
        logger.debug(f"Removed all elements with {element_type}.{element.name} from store")

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

class DuplicateNameError(Exception):
    """Raised when a duplicate name is detected."""


class ElementNotFoundError(Exception):
    """Raised when an element is not stored."""


class InvalidElementType(Exception):
    """Raised when an invalid type is used."""
