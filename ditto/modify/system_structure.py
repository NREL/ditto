# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import logging

import copy
import time
import random

import networkx as nx

import numpy as np


from ditto.models.powertransformer import PowerTransformer
from ditto.models.load import Load
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.position import Position
from ditto.models.power_source import PowerSource
from ditto.models.phase_winding import PhaseWinding

from ditto.models.feeder_metadata import Feeder_metadata

from ditto.modify.modify import Modifier
from ditto.network.network import Network

logger = logging.getLogger(__name__)


class system_structure_modifier(Modifier):
    """This class implements all methods modifying the topology of a DiTTo model.
    The class inherits from the Modifier class and uses the DiTTo Network module.

    What it does:

        - feeder_preprocessing: Performs automatic recognition of feeders in the system. All elements of a given feeder have the same feeder_name and substation_name attributes.
        - center_tap_load_preprocessing: Re-organize all phases and objects downstream of center-tap transformers such that the system is coherent.

    Author: Nicolas Gensollen. December 2017.
    """

    def __init__(self, model, *args):
        """Class CONSTRUCTOR.

        :param model: DiTTo model on which to perform modifications
        :type model: DiTTo model
        :param source: Name of the source node. (The network will be built from this node)
        :type source: String (name of object is used)

        .. warning:: source cannot be the name of a line or a transformer since these objects are not nodes but edges in the Network representation.
        """
        # Store the model as attribute
        self.model = model

        if len(args) == 1:
            source = args[0]
        else:
            srcs = []
            for obj in self.model.models:
                if isinstance(obj, PowerSource) and obj.is_sourcebus == 1:
                    srcs.append(obj.name)
            srcs = np.unique(srcs)
            if len(srcs) == 0:
                raise ValueError("No PowerSource object found in the model.")
            elif len(srcs) > 1:
                raise ValueError("Mupltiple sourcebus found: {srcs}".format(srcs=srcs))
            else:
                source = srcs[0]

        # Store the source name as attribute
        self.source = source

        # TODO: Get the source voltage properly...
        #
        for x in self.model.models:
            if (
                isinstance(x, PowerSource)
                and hasattr(x, "nominal_voltage")
                and x.nominal_voltage is not None
                and x.is_sourcebus
            ):
                self.source_voltage = x.nominal_voltage

        # Build the graph...
        # Note: This takes a while...
        #
        # TODO: Improve the graph build in the Network module. Tarek, any idea?
        #
        # TODO: Combine with network_analyzer such that the network is not built multiple times.
        #
        self.G = Network()
        self.G.build(self.model, source=self.source)

        self.model.set_names()
        # Set the attributes in the graph
        self.G.set_attributes(self.model)

        self.model.set_names()

        # Equipment types and names on the edges
        self.edge_equipment = nx.get_edge_attributes(self.G.graph, "equipment")
        self.edge_equipment_name = nx.get_edge_attributes(
            self.G.graph, "equipment_name"
        )

    def set_missing_coords_recur(self):
        """ Identify nodes that don't have coordinates set and set them to be the average of the existing position values of the neighboring nodes.
        If no adjacent nodes have positional values continue to compute recursively (via while loop)
        """
        recur_nodes = []
        for i in self.model.models:
            if (
                hasattr(i, "positions")
                and (
                    i.positions is None
                    or len(i.positions) == 0
                    or i.positions[0].lat == 0
                    or i.positions[0].long == 0
                )
                and (hasattr(i, "name") and i.name is not None)
            ):
                if (
                    i.name in self.G.graph.nodes()
                ):  # Only find coords of missing nodes - not edges
                    recur_nodes.append(
                        i.name
                    )  # Should be passing the reference to the node

        while len(recur_nodes) > 0:
            next_recur = []
            for i in recur_nodes:
                adj_lats_longs = []
                for j_name in self.G.graph.neighbors(i):
                    j = self.model[j_name]
                    if (
                        hasattr(j, "positions")
                        and j.positions is not None
                        and len(j.positions) != 0
                        and j.positions[0].lat != 0
                        and j.positions[0].long != 0
                    ):
                        adj_lats_longs.append((j.positions[0].lat, j.positions[0].long))

                if len(adj_lats_longs) == 0:
                    next_recur.append(i)
                else:
                    av_lat = 0
                    av_long = 0
                    num = 0
                    for element in adj_lats_longs:
                        av_lat += element[0]
                        av_long += element[1]
                        num += 1
                    av_lat = av_lat / float(num)
                    av_long = av_long / float(num)
                    computed_pos = Position(self.model)
                    computed_pos.lat = av_lat
                    computed_pos.long = av_long
                    self.model[i].positions = [computed_pos]
            if len(next_recur) == len(recur_nodes):
                for i in recur_nodes:
                    logger.warning("Unable to compute coordinates for {}".format(i))
                    print("Unable to compute coordinates for {}".format(i))
                return
            recur_nodes = next_recur

    def set_feeder_metadata(self, feeder_name=None, substation=None, transformer=None):
        """This function sets the feeder metada and adds it to the model
        This can be used when parsing a file with feeder information to add feeder data to the model
        """
        feeder_metadata = Feeder_metadata(self.model)
        feeder_metadata.name = feeder_name
        feeder_metadata.transformer = transformer
        feeder_metadata.substation = substation

    def set_feeder_headnodes(self):
        """This function sets the headnode for the feeder_metadata.
        The headnode cannot simply be the name of the feeder because that would create a name conflict.
        For some reason, in the RNM output, the name of the feeder if something like "a->b", and the headnodes are something like "b->a_S" or "b->a_S_S" or "b->a_S_S_S".
        So the goal of this function is to loop over the feeder_metadata, find the buses directly downstream of the substation (i.e. the headnodes), and put a value for the headnode attribute.
        If this convention changes, this function might need to be updated...
        """
        for obj in self.model.models:
            if isinstance(obj, Feeder_metadata):
                name_cleaned = obj.name.replace(".", "").lower().replace("_src", "")
                headnodes = list(self.G.digraph.successors(obj.substation))

                if name_cleaned in headnodes:
                    obj.headnode = name_cleaned  # This should not be the case because of name conflicts
                else:
                    cleaned_headnodes = [h.strip("x") for h in headnodes]

                    if name_cleaned in cleaned_headnodes:
                        obj.headnode = headnodes[cleaned_headnodes.index(name_cleaned)]
                    else:
                        reverse_headnodes = []
                        for headnode in cleaned_headnodes:
                            if ">" in headnode:
                                a, b = headnode.split(">")
                                reverse_headnodes.append(b + "->" + a)
                            else:
                                reverse_headnodes.append(headnode)
                        if name_cleaned in reverse_headnodes:
                            obj.headnode = headnodes[
                                reverse_headnodes.index(name_cleaned)
                            ]
                            obj.nominal_voltage = self.model[
                                obj.headnode
                            ].nominal_voltage
                            obj.operating_voltage = obj.nominal_voltage

    def set_nominal_voltages_recur(self, *args):
        """This function sets the nominal voltage of the elements in the network.
        This is currently the fastest implementation available as of early January 2018.
        It uses a kind os message passing algorithm. A node passes its nominal voltage to its succesors but modify this value if there is a voltage transformation.

        .. note:: This implementation is MUCH faster than looping over objects and looking for the secondary voltage of the upstream transformer.
        """
        if not args:
            node = self.source
            voltage = self.source_voltage
            previous = self.source
        else:
            node, voltage, previous = args
        if (previous, node) in self.edge_equipment and self.edge_equipment[
            (previous, node)
        ] == "PowerTransformer":
            trans_name = self.edge_equipment_name[(previous, node)]
            new_value = min(
                [
                    w.nominal_voltage
                    for w in self.model[trans_name].windings
                    if w.nominal_voltage is not None
                ]
            )
        elif (node, previous) in self.edge_equipment and self.edge_equipment[
            (node, previous)
        ] == "PowerTransformer":
            trans_name = self.edge_equipment_name[(node, previous)]
            new_value = min(
                [
                    w.nominal_voltage
                    for w in self.model[trans_name].windings
                    if w.nominal_voltage is not None
                ]
            )
        else:
            new_value = voltage
        if hasattr(self.model[node], "nominal_voltage"):
            self.model[node].nominal_voltage = new_value
        for child in self.G.digraph.successors(node):
            self.set_nominal_voltages_recur(child, new_value, node)

    def set_nominal_voltages_recur_line(self):
        """This function should be called after set_nominal_voltages_recur to set the nominal voltage of the lines, because set_nominal_voltages_recur only acts on the nodes.

        .. warning:: Have to be called after set_nominal_voltages_recur.
        """
        for obj in self.model.models:
            # If we get a line
            if isinstance(obj, Line) and obj.nominal_voltage is None:
                # Get the from node
                if hasattr(obj, "from_element") and obj.from_element is not None:
                    node_from_object = self.model[obj.from_element]

                    # If the from node has a known nominal voltage, then use this value
                    if (
                        hasattr(node_from_object, "nominal_voltage")
                        and node_from_object.nominal_voltage is not None
                    ):
                        obj.nominal_voltage = node_from_object.nominal_voltage

    def set_load_coordinates(self, **kwargs):
        """Tries to give a position to load objects where position is not known.
        This can happen when reading from OpenDSS for example since loads are connected to buses but are not included in the buscoordinate file.

        We position the load with the following very simple heuristic

            - load elevation=connecting element elevation + delta_elevation
            - load longitude=connecting element longitude + delta_longitude
            - load latitude =connecting element latitude + delta_latitude

        The user can specify what values he/she wants to use:

            >>> modifier.set_load_coordinates(delta_longitude=.35, delta_latitude=0, delta_elevation=0.1)

        Default values are:

            - delta_longitude=0.1
            - delta_latitude=0.1
            - delta_elevation=0
        """
        if "delta_longitude" in kwargs and isinstance(
            kwargs["delta_longitude"], (int, float)
        ):
            delta_longitude = kwargs["delta_longitude"]
        else:
            delta_longitude = 0.1

        if "delta_latitude" in kwargs and isinstance(
            kwargs["delta_latitude"], (int, float)
        ):
            delta_latitude = kwargs["delta_latitude"]
        else:
            delta_latitude = 0.1

        if "delta_elevation" in kwargs and isinstance(
            kwargs["delta_elevation"], (int, float)
        ):
            delta_elevation = kwargs["delta_elevation"]
        else:
            delta_elevation = 0

        for obj in self.model.models:
            if isinstance(obj, Load) and obj.positions is None:
                if (
                    hasattr(obj, "connecting_element")
                    and obj.connecting_element is not None
                ):
                    try:
                        if (
                            hasattr(self.model[obj.connecting_element], "position")
                            and self.model[obj.connecting_element].position is not None
                        ):
                            position_obj = self.model[obj.connecting_element].positions
                            obj.positions = []
                            for po in position_obj:
                                _long = po.long
                                _lat = po.lat
                                _elev = po.elevation

                                load_position = Position()
                                load_position.long = _long + delta_longitude
                                load_position.lat = _lat + delta_latitude
                                load_position.elevation = _elev + delta_elevation

                                obj.positions.append(load_position)
                    except:
                        pass

    def feeder_preprocessing(self):
        """Performs the feeder cut pre-processing step.
        The function basically loops over all the transformers, looking for those used as substations (attribute is_substation=1).
        Once the substations are identified, we look for all the objects downstream of each substation.
        These elements are identified as a feeder for this substation.
        Each object has an attribute 'substation_name' which is then set to the name of the substation transformer.

        .. warning:: It might be the case that we have substations downstream of substations. In this case, only the elements dowstream of the most downstream substations will be considered as feeders.

        .. TODO:: Clarify how we define feeders when we have multiple susbstation levels.

        .. TODO:: Make sure everything behaves well when using Tarek's substation layer... (No clue on what is going to happen here...)

        .. note::

            - A transformer is not a node in the network representation, but an edge.
            - This means that we have to use the secondary bus to perform the dfs.
            - If a substation has multiple feeders attached to it, it should still be possible to easily use this function.
        """
        # Store the list of objects per feeder.
        # This is useful to run some tests (count, intersection...)
        self._list_of_feeder_objects = []

        # First step: Find all the transformer objects in the models
        for elt in self.model.models:
            if isinstance(elt, PowerTransformer):

                # If we have a substation...
                if (
                    hasattr(elt, "is_substation")
                    and elt.is_substation == 1
                    and hasattr(elt, "name")
                ):

                    # Step 2: Find all elements downstream of this substation
                    downstream_elts = self.G.get_all_elements_downstream(
                        self.model, elt.to_element
                    )

                    # Now, we might have substations in these elements.
                    # In this case we simply do nothing since these lower substations will be consider later in the outer loop.
                    #
                    # TODO:: Find a more clever way to do that without looping for nothing...
                    #
                    skip = False
                    for down_elt in downstream_elts:
                        if (
                            hasattr(down_elt, "is_substation")
                            and down_elt.is_substation == 1
                        ):
                            logger.debug(
                                "Info: substation {a} found downstream of substation {b}".format(
                                    b=elt.name, a=down_elt.name
                                )
                            )
                            skip = True
                            break
                    # If no substation was found downstream, then set the substation_name and feeder_name attributes of the objects
                    if not skip:
                        self._list_of_feeder_objects.append(downstream_elts)

                        for down_elt in downstream_elts:
                            if (
                                down_elt.substation_name is not None
                                and len(down_elt.substation_name) != 0
                            ):
                                raise ValueError(
                                    "Substation name for element {name} was already set at {_previous}. Trying to overwrite with {_next}".format(
                                        name=down_elt.name,
                                        _previous=down_elt.substation_name,
                                        _next=elt.name,
                                    )
                                )
                            else:
                                down_elt.substation_name = elt.name

                            if (
                                down_elt.feeder_name is not None
                                and len(down_elt.feeder_name) != 0
                            ):
                                raise ValueError(
                                    "Feeder name for element {name} was already set at {_previous}. Trying to overwrite with {_next}".format(
                                        name=down_elt.name,
                                        _previous=down_elt.feeder_name,
                                        _next="Feeder_" + elt.name,
                                    )
                                )
                            else:
                                down_elt.feeder_name = (
                                    "Feeder_" + elt.name
                                )  # Change the feeder naming convention here...

    def replace_kth_switch_with_recloser(self):
        """
        For every feeder, replace a switch downstream of the feeder head with a recloser. The depth of the switch is chosen at random with the distribution [0.7,0.25, 0.05]
        """
        np.random.seed(0)
        # Loop over the objects
        for elt in self.model.models:
            # If we get a substation connection
            if (
                hasattr(elt, "is_substation_connection")
                and elt.is_substation_connection
            ):

                switch_cnt = 0
                target_depth = np.random.choice([1, 2, 3], p=[0.7, 0.25, 0.05])
                if (
                    hasattr(elt, "nominal_voltage") and elt.nominal_voltage < 69000
                ):  # To avoid the high connection of the substations

                    should_continue = True

                    # Get the downstream node
                    from_node = elt.name

                    while should_continue:
                        # Get sucessor node
                        try:
                            end_node = next(self.G.digraph.successors(from_node))
                        except:
                            break

                        # Get the name of the object making the connection between from_node and to_node
                        if (from_node, end_node) in self.edge_equipment_name:
                            _name = self.edge_equipment_name[(from_node, end_node)]
                        elif (end_node, from_node) in self.edge_equipment_name:
                            _name = self.edge_equipment_name[(end_node, from_node)]

                        # Get the corresponding object
                        try:
                            _obj = self.model[_name]
                        except:
                            break

                        if (
                            hasattr(_obj, "is_switch")
                            and _obj.is_switch == 1
                            and hasattr(_obj, "wires")
                            and len(_obj.wires) > 0
                            and not _obj.wires[0].is_open
                        ):
                            switch_cnt += 1
                            if switch_cnt == target_depth:
                                _obj.is_recloser = 1
                                _obj.is_switch = 0
                                should_continue = False

                        # Go downstream...
                        from_node = end_node

    def test_feeder_cut(self):
        """This function tests the feeder cut obtained with feeder_preprocessing().
        It prints some basic statistics on the feeders and look at the intersections.
        If the cut was done properly, we shouldn't have elements in multiple feeders.

        .. TODO:: Change the code to make real tests instead of print statements.
        """
        # Number of feeders
        N_feeder = len(self._list_of_feeder_objects)
        logger.debug("Number of feeders defined = {}".format(N_feeder))

        # Size distribution
        feeder_sizes = list(map(len, self._list_of_feeder_objects))
        logger.debug("Sizes of the feeders = {}".format(feeder_sizes))

        # Intersections (should be empty...)
        for i, f1 in enumerate(self._list_of_feeder_objects):
            for j, f2 in enumerate(self._list_of_feeder_objects):
                if j > i:
                    f1_set = set(f1)
                    f2_set = set(f2)
                    intersection = f1_set.intersection(f2_set)
                    if len(intersection) != 0:
                        logger.debug("=" * 40)
                        logger.debug(
                            "Feeder {n} and feeder {m} intersect:".format(n=i, m=j)
                        )
                        logger.debug(intersection)

    def set_nominal_voltages(self):
        """This function does the exact same thing as _set_nominal_voltages.
        The implementation is less obvious but should be much faster.

        **Algorithm:**

            - Find all edges modeling transformers in the network
            - Disconnect these edges (which should disconnect the network)
            - Compute the connected components
            - Group the nodes according to these connected components
            - Re-connect the network by adding back the removed edges
            - For every group of nodes:
                - Find the nominal voltage of one node (look at secondary voltage of the upstream transformer)
                - All nodes in this group get the same nominal voltage
            - For every line:
                - Set nominal voltage as the nominal voltage of one of the end-points (that we have thanks to the previous loop...)

        .. note:: This should be faster than _set_nominal_voltages since we only look upstream once for every group instead of doing it once for every node.

        .. warning:: Use set_nominal_voltages_recur instead.

        .. TODO:: Find out why the results of this and set_nominal_voltages_recur don't match...
        """
        self.model.set_names()

        # We will remove all edges representing transformers
        edges_to_remove = [
            edge
            for edge in self.G.graph.edges(data=True)
            if "equipment" in edge[2] and edge[2]["equipment"] == "PowerTransformer"
        ]

        # Do it!!
        self.G.graph.remove_edges_from(edges_to_remove)

        # Get the connected components
        cc = nx.connected_components(self.G.graph)

        # Extract the groups of nodes with same nominal voltage
        node_mapping = [component for component in cc]

        # Restaure the network by addind back the edges previously removed
        self.G.graph.add_edges_from(edges_to_remove)

        # Graph should be connected, otherwise we broke it...
        assert nx.is_connected(self.G.graph)

        # Instanciate the list of nominal voltages (one value for each group)
        nominal_voltage_group = [None for _ in node_mapping]
        upstream_transformer_name_group = [None for _ in node_mapping]

        # For every group...
        for idx, group in enumerate(node_mapping):

            # ...first node is volonteered to be searched
            volonteer = group.pop()
            while not isinstance(self.model[volonteer], Node):
                volonteer = group.pop()

            # Get the name of the upstream transformer
            upstream_transformer_name = self.G.get_upstream_transformer(
                self.model, volonteer
            )

            # If we got None, there is nothing we can do. Otherwise...
            if upstream_transformer_name is not None:

                # ...get the transformer object
                upstream_transformer_object = self.model[upstream_transformer_name]
                upstream_transformer_name_group[idx] = upstream_transformer_name

                # Get the nominal voltage of the secondary
                if (
                    hasattr(upstream_transformer_object, "windings")
                    and upstream_transformer_object.windings is not None
                ):

                    volts = []
                    for winding in upstream_transformer_object.windings:
                        if (
                            hasattr(winding, "nominal_voltage")
                            and winding.nominal_voltage is not None
                        ):
                            volts.append(winding.nominal_voltage)

                    secondary_voltage = min(volts)
                    # And assign this value as the nominal voltage for the group of nodes
                    nominal_voltage_group[idx] = secondary_voltage

        # Now, we simply loop over all the groups
        for idx, group in enumerate(node_mapping):

            # And all the nodes inside of the groups
            for n in group:

                # And set the nominal voltage as the group value
                self.model[n].nominal_voltage = nominal_voltage_group[idx]
                if isinstance(self.model[n], Load):
                    self.model[
                        n
                    ].upstream_transformer_name = upstream_transformer_name_group[idx]

        # Now we take care of the Lines.
        # Since we should have the nominal voltage for every node (in a perfect world),
        # We just have to grab the nominal voltage of one of the end-points.
        for obj in self.model.models:
            # If we get a line
            if isinstance(obj, Line) and obj.nominal_voltage is None:
                # Get the from node
                if hasattr(obj, "from_element") and obj.from_element is not None:
                    node_from_object = self.model[obj.from_element]

                    # If the from node has a known nominal voltage, then use this value
                    if (
                        hasattr(node_from_object, "nominal_voltage")
                        and node_from_object.nominal_voltage is not None
                    ):
                        obj.nominal_voltage = node_from_object.nominal_voltage

    def _set_nominal_voltages(self):
        """This function looks for all nodes and lines which have empty nominal_voltage fields.
        The function goes upstream in the network representation to find a transformer.
        The nominal voltage of the secondary of this transformer is then used to fill the empty nominal_voltage fields.

        .. warning:: DO NOT USE. Use set_nominal_voltages instead

        .. TODO:: Remove this once everything is stable.
        """
        self.model.set_names()
        # Loop over the objects
        for obj in self.model.models:

            # If we get a Node with an empty nominal_voltage field
            if isinstance(obj, Node) and obj.nominal_voltage is None:
                # Get the upstream transformer name
                try:
                    upstream_transformer_name = self.G.get_upstream_transformer(
                        self.model, obj.name
                    )
                except:
                    continue
                if upstream_transformer_name is not None:
                    # Get the corresponding object
                    upstream_transformer_object = self.model[upstream_transformer_name]
                    # If possible, get all the winding voltages and select the minimum as the secondary voltage
                    if (
                        hasattr(upstream_transformer_object, "windings")
                        and upstream_transformer_object.windings is not None
                    ):
                        volts = []
                        for winding in upstream_transformer_object.windings:
                            if (
                                hasattr(winding, "nominal_voltage")
                                and winding.nominal_voltage is not None
                            ):
                                volts.append(winding.nominal_voltage)
                        secondary_voltage = min(volts)
                        # Finally, assign this value to the object's nominal voltage
                        obj.nominal_voltage = secondary_voltage

            # If we get a line
            if isinstance(obj, Line) and obj.nominal_voltage is None:
                # Get the from node
                if hasattr(obj, "from_element") and obj.from_element is not None:
                    node_from_object = self.model[obj.from_element]

                    # If the from node has a known nominal voltage, then use this value
                    if (
                        hasattr(node_from_object, "nominal_voltage")
                        and node_from_object.nominal_voltage is not None
                    ):
                        obj.nominal_voltage = node_from_object.nominal_voltage

                    # Otherwise, do as before with the from node
                    #
                    # TODO: Put the following code into a function
                    #
                    else:
                        upstream_transformer_name = self.G.get_upstream_transformer(
                            self.model, node_from_object.name
                        )
                        if upstream_transformer_name is not None:
                            upstream_transformer_object = self.model[
                                upstream_transformer_name
                            ]
                            if (
                                hasattr(upstream_transformer_object, "windings")
                                and upstream_transformer_object.windings is not None
                            ):
                                volts = []
                                for winding in upstream_transformer_object.windings:
                                    if (
                                        hasattr(winding, "nominal_voltage")
                                        and winding.nominal_voltage is not None
                                    ):
                                        volts.append(winding.nominal_voltage)
                                secondary_voltage = min(volts)
                                obj.nominal_voltage = secondary_voltage

    def center_tap_load_preprocessing(self):
        """Performs the center tap load pre-processing step.
        This function is responsible for setting the correct phase of center-tap loads.
        In OpenDSS, we will have these loads as two phase AB loads even if the upstream center tap transformer is one phase.
        The purpose of this function is to find this transformer as well as all the lines in between, grab the phase of the center tap transformer, and then apply the required modifications to the DiTTo objects.

        .. note::

            - This function is using the network module to find upstream elements in an efficient way.
            - If we need to delete elments like phase loads or wires, we set the drop flag of the corresponding element to 1 such that they won't be outputed in the writer.
            This is much faster than deleting the elements for now (delete is looping which is time consumming).
        """
        # Set the names in the model.
        # Required if we wish to access objects by names directly instead of looping
        self.model.set_names()

        # Build a list of all the loads in the DiTTo model
        #
        # TODO: More clever way to do this???
        #
        load_list = []
        for _obj in self.model.models:
            if isinstance(_obj, Load):
                load_list.append(_obj)

        # Get the connecting elements of the loads.
        # These will be the starting points of the upstream walks in the graph
        connecting_elements = [load.connecting_element for load in load_list]

        # List of lists where we store the names of the lines between the loads and the upstream transformer.
        # We need to keep track of these to remove/add wires once we have the phase of the transformer
        line_names = []

        # List where we store the names of the upstream transformers for every load
        transformer_names = []

        # For each connecting element...
        for idx, end_node in enumerate(connecting_elements):

            continu = True
            line_names.append([])

            # Find the upstream transformer by walking the graph upstream
            while continu:

                # Get predecessor node of current node in the DAG
                from_node = next(self.G.digraph.predecessors(end_node))

                # Look for the type of equipment that makes the connection between from_node and to_node
                _type = None
                if (from_node, end_node) in self.edge_equipment:
                    _type = self.edge_equipment[(from_node, end_node)]
                elif (end_node, from_node) in self.edge_equipment:
                    _type = self.edge_equipment[(end_node, from_node)]

                # It could be a Line, a Transformer...
                # If it is a transformer, then we have found the upstream transformer...
                if _type == "PowerTransformer":

                    # ...we can then stop the loop...
                    continu = False

                    # ...and grab the transformer name to retrieve the data from the DiTTo object
                    if (from_node, end_node) in self.edge_equipment_name:
                        transformer_names.append(
                            self.edge_equipment_name[(from_node, end_node)]
                        )
                        self.model[
                            load_list[idx].name
                        ].upstream_transformer_name = self.edge_equipment_name[
                            (from_node, end_node)
                        ]
                    elif (end_node, from_node) in self.edge_equipment_name:
                        transformer_names.append(
                            self.edge_equipment_name[(end_node, from_node)]
                        )
                        self.model[
                            load_list[idx].name
                        ].upstream_transformer_name = self.edge_equipment_name[
                            (end_node, from_node)
                        ]
                    # If we cannot find the object, raise an error because it sould not be the case...
                    else:
                        raise ValueError(
                            "Unable to find equipment between {_from} and {_to}".format(
                                _from=from_node, _to=end_node
                            )
                        )

                # ...if it is a Line, store the name to modify the wires later, once the upstream transformer will be found
                elif _type == "Line":
                    if (from_node, end_node) in self.edge_equipment_name:
                        line_names[-1].append(
                            self.edge_equipment_name[(from_node, end_node)]
                        )
                    elif (end_node, from_node) in self.edge_equipment_name:
                        line_names[-1].append(
                            self.edge_equipment_name[(end_node, from_node)]
                        )
                    # Again, if we cannot find the object, raise an error because it sould not be the case...
                    else:
                        raise ValueError(
                            "Unable to find equipment between {_from} and {_to}".format(
                                _from=from_node, _to=end_node
                            )
                        )

                # Go upstream...
                end_node = from_node

        # At this point, we exited the loop, so we have found the transformers for all the load objects
        # Cast the list to a Numpy array first
        transformer_names = np.array(transformer_names)

        # Now, we need to get the phases of all these transformers
        phases = []
        # For every transformer name...
        for t_name in transformer_names:
            # Try to get the corresponding DiTTo object by name
            # Note: This should work if set_names() has been called before...
            # If it fails, raise an error...
            try:
                t_obj = self.model[t_name]
                # Get the phases and clean
                _phases = np.array(
                    [
                        [
                            phase_winding.phase
                            for phase_winding in winding.phase_windings
                        ]
                        for winding in t_obj.windings
                    ]
                )
                _phases = np.unique(_phases.flatten())
                phases.append(_phases)
            except:
                raise ValueError(
                    "Unable to retrieve DiTTo object with name {}".format(t_name)
                )

        # Now, we have all the transformers and their phases
        # The next step is to loop over the loads, modify their phases according to the upstream transformer phase
        # And do the same things for all the lines in between the load and the upstream transformer
        #
        # The implementation choice is to keep all the objects and create new ones if needed. Nothing is deleted here.
        # The objects that need to be deleted are flaged with obj.drop=1
        # When the DiTTo model will be outputed, these objects will not be written
        #
        # TODO: Discuss this choice and change the implementation if needed
        #
        for idx, load, lines, phase in zip(
            range(len(load_list)), load_list, line_names, phases
        ):

            # If the transformer upstream is a center tap transformer,
            # then tag this load as a center tap load
            #
            if self.model[transformer_names[idx]].is_center_tap == 1:
                # Tag the load as a center tap load
                load.is_center_tap = True

                # Set the percentage to distribute the load between the actives and the neutral
                # Here we place 50% of the load between active 1 and neutral, and 50% between
                # neutral and active 2
                load.center_tap_perct_1_N = 0.5
                load.center_tap_perct_N_2 = 0.5
                load.center_tap_perct_1_2 = 0

            total_P = sum([pl.p for pl in load.phase_loads])
            total_Q = sum([pl.q for pl in load.phase_loads])
            # Take care of the loads first....
            for phase_load in load.phase_loads:
                # If the load has phase loads with phases that do not match the
                # phase of the upstream transformer, then flag them...
                if phase_load.phase not in phase:
                    phase_load.drop = 1

            # Then, take care of the lines...
            # Loop over all the lines in between the current load and transformer...
            for line in lines:
                try:
                    line_obj = self.model[line]
                except:
                    raise ValueError(
                        "Unable to retrieve DiTTo object with name {}".format(line)
                    )
                # Loop over the wires...
                for wire in line_obj.wires:
                    # Same story here, flag the wires with phases that do not match.
                    if (
                        hasattr(wire, "phase")
                        and wire.phase not in ["N", "N1", "N2"]
                        and wire.phase not in phase
                    ):
                        wire.drop = 1

            # It might be the case that we need to create new objects.
            # For example, we might have had a AB load and the upstream transformer turned out to be phase C
            # In this case, we flag the phase loads A and B with drop=1, but we need to create a new
            # phase load with phase C and drop=0
            # And same story with lines and wires...
            #
            for p in phase:

                # Work on the load...
                if p not in [phase_load.phase for phase_load in load.phase_loads]:
                    # Create new phase load using the copy method of the mother class Modifier
                    # Note: Tried this using copy.deepcopy and was taking forever...
                    # Is there an even faster way???
                    new_phase_load = self.copy(self.model, load.phase_loads[0])
                    new_phase_load.phase = p
                    new_phase_load.drop = 0
                    load.phase_loads.append(new_phase_load)

                # Work on the lines...
                for line in lines:
                    try:
                        line_obj = self.model[line]
                    except:
                        raise ValueError(
                            "Unable to retrieve DiTTo object with name {}".format(line)
                        )
                    if p not in [wire.phase for wire in line_obj.wires]:
                        new_wire = self.copy(self.model, line_obj.wires[0])
                        new_wire.phase = p
                        new_wire.drop = 0
                        line_obj.wires.append(new_wire)

            n_real_phase_loads = sum([1 for pl in load.phase_loads if pl.drop != 1])
            for phase_load in load.phase_loads:
                phase_load.p = total_P / float(n_real_phase_loads)
                phase_load.q = total_Q / float(n_real_phase_loads)

        # for load,lines,phase in zip(load_list,line_names,phases):
        #     #Take care of the loads first....
        #     for phase_load in load.phase_loads:
        #         #If the load has phase loads with phases that do not match the
        #         #phase of the upstream transformer, then flag them...
        #         if phase_load.drop==1:
        #             self.delete_element(self.model,phase_load)
        #
        #     for line in lines:
        #         try:
        #             line_obj=self.model[line]
        #         except:
        #             raise ValueError('Unable to retrieve DiTTo object with name {}'.format(line))
        #         #Loop over the wires...
        #         for wire in line_obj.wires:
        #             #Same story here, flag the wires with phases that do not match.
        #             if wire.drop==1:
        #                 self.delete_element(self.model,wire)

    def terminals_to_phases(self):
        """
        This function is responsible for matching the phases of the loads to transformers.
        In OpenDSS, for a transformer, the secondary winding has the bus representation as terminals and
        for writers like ephasor, the terminal representation has to be retained.
        Hence, the purpose of this function is to find the transformer associated with a load, capture the phases of the load and
        apply it to the phases of secondary winding of the transformer.

        .. note::

            - This function is using the network module to find upstream elements in an efficient way.
        """
        # Set the names in the model.
        # Required if we wish to access objects by names directly instead of looping
        self.model.set_names()

        for _obj in self.model.models:
            if isinstance(_obj, Load):
                connecting_element = _obj.connecting_element
                load_name = _obj.name
                load_phases = []
                # Get the phases of the load
                try:
                    l_obj = self.model[load_name]
                    for phase_load in l_obj.phase_loads:
                        load_phases.append(phase_load.phase)
                except:
                    raise ValueError(
                        "Unable to retrieve DiTTo object with name {}".format(load_name)
                    )

                continu = True
                # Find the upstream transformer by walking the graph upstream
                end_node = connecting_element
                transformer_name = None
                while continu:
                    # Get predecessor node of current node in the DAG
                    try:
                        from_node = next(self.G.digraph.predecessors(end_node))
                    except:
                        break
                    # Look for the type of equipment that makes the connection between from_node and to_node
                    _type = None
                    if (from_node, end_node) in self.edge_equipment:
                        _type = self.edge_equipment[(from_node, end_node)]
                    elif (end_node, from_node) in self.edge_equipment:
                        _type = self.edge_equipment[(end_node, from_node)]

                    # It could be a Line, a Transformer...
                    # If it is a transformer, then we have found the upstream transformer...
                    if _type == "PowerTransformer":

                        # ...we can then stop the loop...
                        continu = False

                        # ...and grab the transformer name to retrieve the data from the DiTTo object
                        if (from_node, end_node) in self.edge_equipment_name:
                            transformer_name = self.edge_equipment_name[
                                (from_node, end_node)
                            ]
                            self.model[
                                load_name
                            ].upstream_transformer_name = self.edge_equipment_name[
                                (from_node, end_node)
                            ]
                        elif (end_node, from_node) in self.edge_equipment_name:
                            transformer_name = self.edge_equipment_name[
                                (end_node, from_node)
                            ]
                            self.model[
                                load_name
                            ].upstream_transformer_name = self.edge_equipment_name[
                                (end_node, from_node)
                            ]
                        # If we cannot find the object, raise an error because it sould not be the case...
                        else:
                            raise ValueError(
                                "Unable to find equipment between {_from} and {_to}".format(
                                    _from=from_node, _to=end_node
                                )
                            )
                    # Go upstream...
                    end_node = from_node

                # Number of windings is 1; we ignore it as it will have the phase of the primary transformer
                # Number of windings is 2; we will make sure the phases of the secondary winding of a transformer are the same as the phases of loads
                # Number of windings is 3; we add a new phase winding to the secondary winding of the transformer and match the phases of the loads to transformer
                if transformer_name is not None:
                    t_obj = self.model[transformer_name]
                    N_windings = len(t_obj.windings)
                    if N_windings == 1:
                        continue
                    if N_windings == 2:
                        for phase_winding, l_phase in zip(
                            t_obj.windings[1].phase_windings, load_phases
                        ):
                            phase_winding.phase = l_phase
                    if N_windings == 3:
                        t_obj.windings[1].phase_windings.append(
                            PhaseWinding(self.model)
                        )
                        for phase_winding, l_phase in zip(
                            t_obj.windings[1].phase_windings, load_phases
                        ):
                            phase_winding.phase = l_phase

    def open_close_switches(self, path_to_dss_file):
        """Since there is not way to indicate wether a switch is open or closed in OpenDSS, RNM use the following convention:
            - If the switch has attribute R1 equals to 1e11, then the switch is open
            - Otherwise it is closed.
        """
        self.model.set_names()
        with open(path_to_dss_file, "r") as f:
            lines = f.readlines()

        for line in lines:
            raw = line.split(" ")
            name = raw[1].split(".")[1].strip().lower()
            data_line = {
                k.strip().lower(): v.strip()
                for k, v in zip(
                    [x.split("=")[0] for x in raw[2:]],
                    [x.split("=")[1] for x in raw[2:]],
                )
            }
            if "switch" in data_line and (
                data_line["switch"] == "y"
                or data_line["switch"] == "yes"
                or data_line["switch"] == "true"
            ):
                if "r1" in data_line and data_line["r1"] == "1e11":
                    try:
                        for wire in self.model[name].wires:
                            wire.is_open = 1
                    except:
                        pass
                else:
                    try:
                        for wire in self.model[name].wires:
                            wire.is_open = 0
                    except:
                        pass

    def set_switching_devices_ampacity(self):
        """Loop over all switching devices without valid ampacity values.
        Look at the neighboring lines and use their ampacity as value.
        """
        # Loop over the ditto objects and find the switches, breakers, sectionalizers, fuses, and reclosers
        for obj in self.model.models:
            if isinstance(obj, Line):
                if (
                    obj.is_switch is True
                    or obj.is_breaker is True
                    or obj.is_sectionalizer is True
                    or obj.is_fuse is True
                    or obj.is_recloser is True
                ):

                    # Store the ampacities of the device's wires
                    amps = np.array([wire.ampacity for wire in obj.wires])

                    # and check if there are some nan values
                    if np.any(np.isnan(amps)):

                        # 2 possibilities here:
                        # case 1: Not all ampacity ratings are nans
                        if not np.all(np.isnan(amps)):

                            # This means that at least one of the device wires has a valid rating
                            valid_amps = amps[np.logical_not(np.isnan(amps))]

                            # Find it and use it for the other wires
                            if len(valid_amps) == 1:
                                amps_value = valid_amps[0]
                            else:
                                amps_value = np.max(
                                    valid_amps
                                )  # we have different ratings accross wires. Heuristic: use the maximum.

                            for wire in obj.wires:
                                wire.ampacity = amps_value

                        # Case 2: All ampacity ratings are nans
                        else:
                            # Here we look for a neighboring line object with a valid ampacity rating
                            if (
                                obj.from_element is not None
                                and obj.to_element is not None
                            ):

                                should_continue = True
                                from_node = obj.from_element
                                to_node = obj.to_element

                                while should_continue:
                                    if self.G.graph.has_node(
                                        from_node
                                    ) and self.G.graph.has_node(to_node):

                                        # Get the neighbors on the from side
                                        neighbors_from = [
                                            n
                                            for n in nx.neighbors(
                                                self.G.graph, from_node
                                            )
                                            if n != to_node
                                        ]

                                        # Get the neighbors on the to side
                                        neighbors_to = [
                                            n
                                            for n in nx.neighbors(self.G.graph, to_node)
                                            if n != from_node
                                        ]

                                        amps_value = None
                                        if len(neighbors_from) > 0:

                                            # To avoid infinite loops where we always consider the same objects, select neighbors randomly
                                            idx = random.randint(
                                                0,
                                                min(
                                                    len(neighbors_from),
                                                    len(neighbors_to),
                                                )
                                                - 1,
                                            )

                                            # we only have the from and to nodes. We need to find the name of the corresponding ditto object
                                            if (
                                                neighbors_from[idx],
                                                obj.from_element,
                                            ) in self.edge_equipment_name:

                                                try:
                                                    # Try to get the object with its name
                                                    neighboring_line_obj = self.model[
                                                        self.edge_equipment_name[
                                                            (
                                                                neighbors_from[idx],
                                                                from_node,
                                                            )
                                                        ]
                                                    ]

                                                    # If we have a valid ampacity rating, then use this value and exit the loop
                                                    if neighboring_line_obj.wires[
                                                        0
                                                    ].ampacity is not None and not np.isnan(
                                                        neighboring_line_obj.wires[
                                                            0
                                                        ].ampacity
                                                    ):
                                                        amps_value = neighboring_line_obj.wires[
                                                            0
                                                        ].ampacity
                                                        should_continue = False

                                                # If we failed for some reason, try on the to side
                                                except:
                                                    amps_value = None

                                        # If we still haven't found a value and we have sone neighbors on the to side
                                        if amps_value is None and len(neighbors_to) > 0:

                                            # Try to find the name of the object
                                            if (
                                                to_node,
                                                neighbors_to[idx],
                                            ) in self.edge_equipment_name:

                                                try:
                                                    neighboring_line_obj = self.model[
                                                        self.edge_equipment_name[
                                                            (to_node, neighbors_to[idx])
                                                        ]
                                                    ]
                                                    if neighboring_line_obj.wires[
                                                        0
                                                    ].ampacity is not None and not np.isnan(
                                                        neighboring_line_obj.wires[
                                                            0
                                                        ].ampacity
                                                    ):
                                                        amps_value = neighboring_line_obj.wires[
                                                            0
                                                        ].ampacity
                                                        should_continue = False
                                                except:
                                                    amps_value = None

                                        # At this point, if we still haven't found a value, update the from and to node to
                                        # continue the search further away from the initial object
                                        if should_continue:
                                            to_node = neighbors_to[idx]
                                            from_node = to_node

                                    else:
                                        raise ValueError(
                                            "Missing nodes {n1} and/or {n2} in network".format(
                                                n1=from_node, n2=to_node
                                            )
                                        )

                                if amps_value is not None:
                                    for wire in obj.wires:
                                        wire.ampacity = amps_value
