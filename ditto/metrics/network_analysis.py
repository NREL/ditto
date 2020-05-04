# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import logging
import math
import time
import logging
import json
import json_tricks
from six import string_types

import networkx as nx

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull

from ditto.network.network import Network
from ditto.models.regulator import Regulator
from ditto.models.line import Line
from ditto.models.capacitor import Capacitor
from ditto.models.load import Load
from ditto.models.powertransformer import PowerTransformer
from ditto.models.node import Node
from ditto.models.power_source import PowerSource
from ditto.modify.system_structure import system_structure_modifier

from ..readers.abstract_reader import AbstractReader

logger = logging.getLogger(__name__)


class NetworkAnalyzer(object):
    """
    This class is used to compute validation metrics from the DiTTo representation itself.


    **Initialization:**

        >>> analyst=network_analyzer(model, source)

        Where model is the DiTTo model under consideration, and source is the source node.


    **Usage:**

        There are different ways to use this class:

            - Compute metrics for the whole network.

                - Compute a specific metric:

                    >>> n_regulator=analyst.number_of_regulators()

                    This will compute the number of regulators in the whole network.

                - Compute all metrics:

                    >>> results=analyst.compute_all_metrics()

                    This will compute all the available metrics in the whole network.

                    .. warning:: Some metrics have N^2 complexity...

            - Compute metrics for individual feeders.

                - Compute a specific metric:

                    >>> n_regulator=analyst.number_of_regulators(feeder_1)

                    This will compute the number of regulators for a feeder named 'feeder_1'.

                    .. warning:: Currently not implemented.

                - Compute all metrics for all feeders:

                    >>> results=analyst.compute_all_metrics_per_feeder()

                    This will compute all available metrics for all feeders.

                    .. warning:: This requires having done the feeder split of the network. (See section 'feeder split')


    **Feeder split:**

        To compute the metrics at the feeder level, you have to provide the following:

            - feeder_names: A list of the feeder names.
            - feeder_nodes: A list of lists which contains the nodes in each feeder. (indexing should be consistent with feeder_names)

        Give this information to the network_analyzer is straightforward:

            >>> analyst.add_feeder_information(feeder_names, feeder_nodes)

        The actual feeder split is done through:

            >>> analyst.split_network_into_feeders()

    .. note::

        - Using compute_all_metrics or compute_all_metrics_per_feeder only loops over the objects once in order to improve performance.
          It is NOT a wrapper that calls the metric functions one by one.
          Therefore, it is strongly recommanded to use one of these two methods when more than a few metrics are needed.
        - The class constructor is building the network (using the DiTTo Network module) which can take some time...

    Author: Nicolas Gensollen. December 2017
    """

    def __init__(self, model, compute_network=True, *args):
        """Class CONSTRUCTOR."""
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
                raise ValueError("Multiple sourcebus found: {srcs}".format(srcs=srcs))
            else:
                source = srcs[0]

        # Store the source name as attribute
        self.source = source

        # Dirty way to access the abstract reader methods
        # TODO: Better way?
        self.abs_reader = AbstractReader()

        # Build the Network if required
        #
        # WARNING: Time consuming...
        #
        if compute_network:
            self.G = Network()
            self.G.build(self.model, source=self.source)

            # Set the attributes in the graph
            self.G.set_attributes(self.model)

            # Equipment types and names on the edges
            self.edge_equipment = nx.get_edge_attributes(self.G.graph, "equipment")
            self.edge_equipment_name = nx.get_edge_attributes(
                self.G.graph, "equipment_name"
            )
        else:
            self.G = None
            self.edge_equipment = None
            self.edge_equipment_name = None

        modifier = system_structure_modifier(self.model, source)
        modifier.set_nominal_voltages()
        # IMPORTANT: the following two parameters define what is LV and what is MV.
        # - Object is LV if object.nominal_voltage<=LV_threshold
        # - Object is MV if MV_threshold>=object.nominal_voltage>LV_threshold
        # Metrics are obviously extremely sensitive to these two parameters...
        #
        self.LV_threshold = 1000  # In volts. Default=1kV
        self.MV_threshold = 69000  # In volts. Default=69kV

        self.feeder_names = None
        self.feeder_nodes = None

        self.feeder_networks = {}
        self.node_feeder_mapping = {}
        self.points = {}

        # This flag indicates whether we should compute the kva density metric using transformer objects
        # Default is True. If set to False, the `transformer_connected_kva` attribute of load objects will
        # be used. This enables fair comparison between networks where LV data is missing.
        self.compute_kva_density_with_transformers = True

        self.__substations = [
            obj
            for obj in self.model.models
            if isinstance(obj, PowerTransformer) and obj.is_substation == 1
        ]

    def provide_network(self, network):
        """TODO"""
        if not isinstance(network, Network):
            raise TypeError(
                "provide_network expects a Network instance. A {t} was provided.".format(
                    t=type(network)
                )
            )
        self.G = network
        self.G.set_attributes(self.model)
        self.edge_equipment = nx.get_edge_attributes(self.G.graph, "equipment")
        self.edge_equipment_name = nx.get_edge_attributes(
            self.G.graph, "equipment_name"
        )

    def add_feeder_information(
        self, feeder_names, feeder_nodes, substations, feeder_types
    ):
        """
        Use this function to add the feeder information if available.

        :param feeder_names: List of the feeder names
        :type feeder_names: List(str)
        :param feeder_nodes: List of lists containing feeder nodes
        :type feeder_nodes: List of Lists of strings
        :param feeder_types: List of feeder types.
        :type feeder_types: List or string if all feeders have the same type
        """
        if len(feeder_names) != len(feeder_nodes):
            raise ValueError(
                "Number of feeder names {a} does not match number of feeder lists of nodes {b}".format(
                    a=len(feeder_names), b=len(feeder_nodes)
                )
            )
        if isinstance(feeder_types, string_types):
            self.feeder_types = {k: feeder_types for k in feeder_names}
        elif isinstance(feeder_types, list):
            if len(feeder_names) != len(feeder_types):
                raise ValueError(
                    "Number of feeder names {a} does not match number of feeder types of nodes {b}".format(
                        a=len(feeder_names), b=len(feeder_types)
                    )
                )
            else:
                self.feeder_types = {k: v for k, v in zip(feeder_names, feeder_types)}
        self.feeder_names = feeder_names
        self.feeder_nodes = feeder_nodes
        self.substations = substations

    def split_network_into_feeders(self):
        """
        This function splits the network into subnetworks corresponding to the feeders.

        .. note:: add_feeder_information should be called first
        """
        if self.feeder_names is None or self.feeder_nodes is None:
            raise ValueError(
                "Cannot split the network into feeders because feeders are unknown. Call add_feeder_information first."
            )

        for cpt, feeder_name in enumerate(self.feeder_names):
            feeder_node_list = self.feeder_nodes[cpt]
            self.feeder_networks[feeder_name] = self.G.graph.subgraph(feeder_node_list)

            # If the feeder information is perfect, that is the end of the story.
            # But, most of the time, some nodes are missing from the feeder information.
            # This means that we get disconnected feeder networks which will cause some
            # issues later (when computing the diameter for example)
            # For this reason, the following code is trying to infer the missing nodes
            # and edges such that the feeder networks are all connected in the end.
            while not nx.is_connected(self.feeder_networks[feeder_name]):
                self.connect_disconnected_components(feeder_name)
                feeder_node_list = self.feeder_nodes[cpt]
                self.feeder_networks[feeder_name] = self.G.graph.subgraph(
                    feeder_node_list
                )

            # Build the node_feeder_mapping
            # for node in self.feeder_nodes[cpt]:
            for node in self.feeder_networks[feeder_name].nodes():
                self.node_feeder_mapping[node] = feeder_name

    def export_json(self, *args):
        """
        Export the raw metrics in JSON format.

        :param export_path: Relative path to the output file
        :type export_path: str
        """
        try:
            if len(args) > 0:
                export_path = args[0]
            else:
                export_path = "./output.json"
            with open(export_path, "w") as f:
                f.write(json.dumps(self.results))
        except TypeError:
            self.export_json_tricks(*args)

    def export_json_tricks(self, *args):
        """
        Export the raw metrics in JSON format using the json-tricks library: http://json-tricks.readthedocs.io/en/latest/#dump.

        :param export_path: Relative path to the output file
        :type export_path: str
        """
        if args:
            export_path = args[0]
        else:
            export_path = "./output.json"
        with open(export_path, "w") as fp:
            fp.write(json_tricks.dumps(self.results, allow_nan=True))

    def export(self, *args):
        """
        Export the metrics to excel report card.

        :param export_path: Relative path to the output file
        :type export_path: str
        """
        # TODO: Add some safety checks here...
        if args:
            export_path = args[0]
        else:
            export_path = "./output.csv"

        # TODO: More maintainable way for this...
        cols = [
            "feeder_name",
            "feeder_type",
            # Realistic electrical design and equipment parameters (MV)
            "mv_len_mi",
            "mv_3ph_len_mi",
            "mv_oh_3ph_len_mi",
            "mv_2ph_len_mi",
            "mv_oh_2ph_len_mi",
            "mv_1ph_len_mi",
            "mv_oh_1ph_len_mi",
            "perct_mv_oh_len",
            "ratio_mv_len_to_num_cust",
            "max_sub_node_distance_mi",
            "nominal_medium_voltage_class",
            # Realistic electrical design and equipment parameters (LV)
            "lv_len_mi",
            "lv_3ph_len_mi",
            "lv_oh_3ph_len_mi",
            "lv_1ph_len_mi",
            "lv_oh_1ph_len_mi",
            "max_len_secondaries_mi",
            "lv_2ph_len_mi",
            "lv_oh_2ph_len_mi",
            "perct_lv_oh_len",
            "ratio_lv_len_to_num_cust",
            # Voltage control schemes
            "num_regulators",
            "num_capacitors",
            "num_boosters",
            "avg_regulator_sub_distance_mi",
            "avg_capacitor_sub_distance_mi",
            # Basic protection
            "num_fuses",
            "num_reclosers",
            "num_sectionalizers",
            "num_sectionalizers_per_recloser",
            "avg_recloser_sub_distance_mi",
            "num_breakers",
            # Reconfiguration Options
            "num_switches",
            "num_interruptors",
            "num_links_adjacent_feeders",
            "num_loops",
            # Transformers
            "num_distribution_transformers",
            "num_overloaded_transformers",
            "sum_distribution_transformer_mva",
            "num_1ph_transformers",
            "num_3ph_transformers",
            "ratio_1ph_to_3ph_transformers",
            # Substations
            "substation_name",
            "substation_capacity_mva",
            # Load specification
            "sum_load_kw",
            "sum_load_pha_kw",
            "sum_load_phb_kw",
            "sum_load_phc_kw",
            "sum_load_kvar",
            "perct_lv_pha_load_kw",
            "perct_lv_phb_load_kw",
            "perct_lv_phc_load_kw",
            "num_lv_1ph_loads",
            "num_lv_3ph_loads",
            "num_mv_3ph_loads",
            "avg_num_load_per_transformer",
            "avg_load_pf",
            "avg_load_imbalance_by_phase",
            "num_customers",
            "cust_density",
            "load_density_kw",
            "load_density_kvar",
            "kva_density",
            # Graph Topology
            "avg_degree",
            "avg_path_len",
            "diameter",
        ]

        # Create empty DataFrame for output
        card = pd.DataFrame(columns=cols)

        n_row = 0
        for key, data in self.results.items():
            card.loc[n_row] = [key] + [data[x] if x in data else None for x in cols[1:]]
            n_row += 1

        # Write to csv
        card.to_csv(export_path, header=True, index=False)

    def tag_objects(self):
        """
        Loop over the objects and fill the feeder_name and substaation_name attributes.
        """
        for obj in self.model.models:
            if hasattr(obj, "feeder_name") and hasattr(obj, "name"):
                if isinstance(obj, Node):
                    if obj.name in self.node_feeder_mapping:
                        obj.feeder_name = self.node_feeder_mapping[obj.name]
                        if obj.feeder_name in self.substations:
                            obj.substation_name = self.substations[obj.feeder_name]

                elif hasattr(obj, "connecting_element"):
                    if obj.connecting_element in self.node_feeder_mapping:
                        obj.feeder_name = self.node_feeder_mapping[
                            obj.connecting_element
                        ]
                        if obj.feeder_name in self.substations:
                            obj.substation_name = self.substations[obj.feeder_name]

                    if (
                        hasattr(obj, "timeseries")
                        and obj.timeseries is not None
                        and len(obj.timeseries) > 0
                    ):
                        for t in obj.timeseries:
                            t.feeder_name = obj.feeder_name
                            t.substation_name = obj.substation_name
                        logger.debug(
                            "Object {name} connecting element {namec} was not found in feeder mapping".format(
                                name=obj.name, namec=obj.connecting_element
                            )
                        )
                elif hasattr(obj, "from_element"):
                    if obj.from_element in self.node_feeder_mapping:
                        obj.feeder_name = self.node_feeder_mapping[obj.from_element]
                        if obj.feeder_name in self.substations:
                            obj.substation_name = self.substations[obj.feeder_name]

                else:
                    logger.debug(obj.name, type(obj))

        for obj in self.model.models:
            if hasattr(obj, "feeder_name") and hasattr(obj, "name"):
                if isinstance(obj, Node):
                    if obj.name not in self.node_feeder_mapping:
                        curr_name = obj.name
                        done_looping = False

                        while not done_looping:
                            try:
                                predecessor = next(
                                    self.G.digraph.predecessors(curr_name)
                                )
                            except StopIteration:
                                done_looping = True
                                break
                            prev_obj = self.model[predecessor]
                            curr_name = predecessor  # Only decent along the branch of the last predecessor for simplicity
                            if (
                                hasattr(prev_obj, "feeder_name")
                                and hasattr(prev_obj, "name")
                                and prev_obj.feeder_name is not None
                                and prev_obj.feeder_name is not ""
                                and prev_obj.name
                                in self.node_feeder_mapping  # In case a default value has been set for all feeder_name values
                            ):
                                obj.feeder_name = prev_obj.feeder_name
                                obj.substation_name = prev_obj.substation_name
                                done_looping = True
                                break

                        logger.debug(
                            "Node {name} was not found in feeder mapping".format(
                                name=obj.name
                            )
                        )

                elif hasattr(obj, "connecting_element"):
                    if obj.connecting_element not in self.node_feeder_mapping:
                        curr_name = obj.connecting_element
                        done_looping = False
                        while not done_looping:
                            try:
                                predecessor = next(
                                    self.G.digraph.predecessors(curr_name)
                                )
                            except StopIteration:
                                done_looping = True
                                break
                            prev_obj = self.model[predecessor]
                            curr_name = predecessor  # Only decent along the branch of the last predecessor for simplicity
                            if (
                                hasattr(prev_obj, "feeder_name")
                                and hasattr(prev_obj, "name")
                                and prev_obj.feeder_name is not None
                                and prev_obj.feeder_name is not ""
                                and prev_obj.name
                                in self.node_feeder_mapping  # In case a default value has been set for all feeder_name values
                            ):
                                obj.feeder_name = prev_obj.feeder_name
                                obj.substation_name = prev_obj.substation_name
                                done_looping = True
                                break

                elif hasattr(obj, "from_element"):
                    if obj.from_element not in self.node_feeder_mapping:
                        curr_name = obj.from_element
                        done_looping = False
                        while not done_looping:
                            try:
                                predecessor = next(
                                    self.G.digraph.predecessors(curr_name)
                                )
                            except StopIteration:
                                done_looping = True
                                break
                            prev_obj = self.model[predecessor]
                            curr_name = predecessor  # Only decent along the branch of the last predecessor for simplicity
                            if (
                                hasattr(prev_obj, "feeder_name")
                                and hasattr(prev_obj, "name")
                                and prev_obj.feeder_name is not None
                                and prev_obj.feeder_name is not ""
                                and prev_obj.name
                                in self.node_feeder_mapping  # In case a default value has been set for all feeder_name values
                            ):
                                obj.feeder_name = prev_obj.feeder_name
                                obj.substation_name = prev_obj.substation_name
                                done_looping = True
                                break

                        logger.debug(
                            "Object {name} from element {namec} was not found in feeder mapping".format(
                                name=obj.name, namec=obj.from_element
                            )
                        )
                else:
                    logger.debug(obj.name, type(obj))

    def connect_disconnected_components(self, feeder_name):
        """
        Helper function for split_network_into_feeders.
        This function takes the first two disconnected components in the feeder network corresponding to feeder_name, and connects them with a shortest path.
        The underlying assumption is that all nodes lying on the shortest path are actual members of this feeder.
        """
        # Get the index of feeder_name
        idx = self.feeder_names.index(feeder_name)

        # Get the feeder_node_list
        feeder_node_list = self.feeder_nodes[idx]

        # Build the subgraph from the complete network
        self.feeder_networks[feeder_name] = self.G.graph.subgraph(feeder_node_list)

        # Compute the connected components
        # Since we were called by split_network_into_feeders only if the graph was disconnected,
        # we know that we have at least 2 elements in cc
        cc = nx.connected_components(self.feeder_networks[feeder_name])

        # cc is a generator and calling list() on it is a bad idea...
        # We simply grab the first two components...
        first_component = next(cc)
        second_component = next(cc)

        # ...and we grab one node at random from each component.
        n1 = first_component.pop()
        n2 = second_component.pop()

        # If there are the same, you have a serious problem.
        # Better kill it here than waiting for weird issues later...
        if n1 == n2:
            raise ValueError(
                "Feeder splitting error. Nodes from 2 different components are the same."
            )

        # Compute the shortest path
        path = nx.shortest_path(self.G.graph, n1, n2)

        # For each node in the shortest path...
        for node in path:
            # ...if the node is not already in the feeder, then add it
            if node not in self.feeder_nodes[idx]:
                self.feeder_nodes[idx].append(node)

    def setup_results_data_structure(self, *args):
        """
        This function creates the data structure which contains the result metrics for a SINGLE network.

        **Usage:**

            >>> data_struct=network_analyzer.setup_results_data_structure(network)

            The network argument can be a networkx Graph or networkx DiGraph or a string representing the name of a known feeder.

            >>> data_struct=network_analyzer.setup_results_data_structure()

            This will create the data structure for the whole network.
        """
        # If arguments were provided
        if args:

            # Only accepts one argument
            if len(args) > 1:
                raise ValueError(
                    "setup_results_data_structure error: Too many input arguments."
                )

            # Cache it
            network = args[0]

            # Case one: it is a string
            if isinstance(network, string_types):

                # Check that this is the name of a feeder
                if network in self.feeder_names:

                    if network in self.substations:
                        _src = self.substations[network]
                    else:
                        raise ValueError(
                            "Could not find the substation for feeder {}".format(
                                network
                            )
                        )

                    # Check that we have split the network into feeders
                    if self.feeder_networks is not None:

                        # Check that the name is linked to a graph object
                        if network in self.feeder_networks:
                            _net = self.feeder_networks[network]

                        # Error raising...
                        else:
                            raise ValueError(
                                "{} is not a known feeder.".format(network)
                            )

                    # Error raising...
                    else:
                        raise ValueError(
                            "Trying to call setup_results_data_structure on feeder {}, but feeders were not defined yet. Try calling split_network_into_feeders.".format(
                                network
                            )
                        )

                # Error raising...
                else:
                    raise ValueError(
                        "{} is not a known feeder name. Try calling add_feeder_information"
                    )

            # Case two: it is a graph or a digrah (Only networkx is supported for this option...)
            elif isinstance(network, nx.classes.graph.Graph) or isinstance(
                network, nx.classes.digraph.DiGraph
            ):
                # Cache the network
                _net = network
                for feeder_name, nett in self.feeder_networks.items():
                    if nett == _net:
                        _src = feeder_name
                        network = feeder_name

            # Otherwise, the format of the input is not supported
            else:
                raise ValueError(
                    "Unsupported type of argument. Provide a graph, DiGraph, or string"
                )

        # If not input, use the whole network...
        else:
            _net = self.G.graph
            _src = self.source

        sub_MVA = None
        for su in self.__substations:
            if _src in su.name.replace(".", ""):
                sub_MVA = min([z.rated_power for z in su.windings]) * 10 ** -6

        # Create the results dictionary.
        # Note: All metrics relying on networkX calls are computed here.
        #

        # logger.info('Analyzing network {name}...'.format(name=network))

        results = {
            "num_regulators": 0,  # Number of regulators
            "sub_capacity_mva": sub_MVA,
            "num_fuses": 0,  # Number of fuses
            "num_switches": 0,  # Number of switches
            "num_reclosers": 0,  # Number of reclosers
            "num_breakers": 0,  # Number of breakers
            "num_capacitors": 0,  # Number of capacitors
            "num_sectionalizers": 0,  # Number of sectionalizers
            "num_customers": 0,  # Number of customers
            "num_links_adjacent_feeders": 0,  # Number of links to neighboring feeders
            "num_overloaded_transformers": 0,  # Number of overloaded transformers
            "num_distribution_transformers": 0,  # Number of distribution transformers
            "max_len_secondaries_mi": 0,  # Maximum distance in the feeder between a distribution transformer and a load
            "sum_distribution_transformer_mva": 0,  # Total capacity of distribution transformers (in MVA)
            "num_1ph_transformers": 0,  # Number of 1 phase distribution transformers
            "num_3ph_transformers": 0,  # Number of 3 phase distribution transformers
            "ratio_1ph_to_3ph_transformers": 0,  # Ratio of 1 phase distribution transformers to three phase distribution transformers
            "avg_degree": self.average_degree(_net),  # Average degree
            "diameter": self.diameter(
                _net
            ),  # Network diameter (in number of edges, NOT in distance)
            "avg_path_len": self.average_path_length(
                _net
            ),  # Average path length (in number of edges, NOT in distance)
            "avg_regulator_sub_distance_mi": self.average_regulator_sub_distance(
                _net, _src
            ),  # Average distance between substation and regulators (if any)
            "avg_capacitor_sub_distance_mi": self.average_capacitor_sub_distance(
                _net, _src
            ),  # Average distance between substation and capacitors (if any)
            "avg_recloser_sub_distance_mi": self.average_recloser_sub_distance(
                _net, _src
            ),  # Average distance between substation and reclosers (if any)
            "max_sub_node_distance_mi": self.furtherest_node_miles(_net, _src),
            "num_loops": self.loops_within_feeder(
                _net
            ),  # Number of loops inside the feeder
            "lv_len_mi": 0,  # Total length of LV lines (in miles)
            "mv_len_mi": 0,  # Total length of MV lines (in miles)
            "mv_1ph_len_mi": 0,  # Total length of 1 phase MV lines (in miles)
            "mv_oh_1ph_len_mi": 0,  # Total length of overhead 1 phase MV lines (in miles)
            "mv_2ph_len_mi": 0,  # Total length of 2 phase MV lines (in miles)
            "mv_oh_2ph_len_mi": 0,  # Total length of overhead 2 phase MV lines (in miles)
            "mv_3ph_len_mi": 0,  # Total length of 3 phase MV lines (in miles)
            "mv_oh_3ph_len_mi": 0,  # Total length of overhead 3 phase MV lines (in miles)
            "lv_1ph_len_mi": 0,  # Total length of 1 phase LV lines (in miles)
            "lv_oh_1ph_len_mi": 0,  # Total length of overhead 1 phase LV lines (in miles)
            "lv_2ph_len_mi": 0,  # Total length of 2 phase LV lines (in miles)
            "lv_oh_2ph_len_mi": 0,  # Total length of overhead 2 phase LV lines (in miles)
            "lv_3ph_len_mi": 0,  # Total length of 3 phase LV lines (in miles)
            "lv_oh_3ph_len_mi": 0,  # Total length of overhead 3 phase LV lines (in miles)
            "sum_load_kw": 0,  # Total demand (active power)
            "sum_load_pha_kw": 0,  # Total demand on phase A
            "sum_load_phb_kw": 0,  # Total demand on phase B
            "sum_load_phc_kw": 0,  # Total demand on phase C
            "sum_load_kvar": 0,  # Total demand (reactive power)
            "num_lv_1ph_loads": 0,  # Number of 1 phase LV loads
            "num_lv_3ph_loads": 0,  # Number of 3 phase LV loads
            "num_mv_3ph_loads": 0,  # Number of 3 phase MV loads
            "perct_lv_pha_load_kw": 0,  # Percentage of total LV demand that is phase A
            "perct_lv_phb_load_kw": 0,  # Percentage of total LV demand that is phase B
            "perct_lv_phc_load_kw": 0,  # Percentage of total LV demand that is phase C
            "sum_lv_pha_load_kw": 0,  # Total LV demand on phase A
            "sum_lv_phb_load_kw": 0,  # Total LV demand on phase B
            "sum_lv_phc_load_kw": 0,  # Total LV demand on phase C
            "avg_num_load_per_transformer": 0,  # Average number of loads per distribution transformer
            "num_load_per_transformer": {},  # Store the number of loads per distribution transformer
            "num_customer_per_transformer": {},  # Store the number of customers per distribution transformer
            "wire_equipment_distribution": {},  # Store the number of each wire equipment
            "transformer_kva_distribution": [],  # Store the distribution of transformer KVA values
            "ratio_load_kW_to_transformer_KVA_distribution": {},  # Store the ratio of load kW to distribution transformer KVA
            "switch_categories_distribution": {},  # Store the number of each different categories of switches
            "power_factor_distribution": [],  # Store the load poser factors
            "sub_trans_impedance_list": {},  # Store the list of line positive sequence impedances between the substation and each distribution transformer
            "trans_cust_impedance_list": {},  # Store the list of line positive sequence impedances between each customer and its distribution transformer
            "nominal_voltages": [],  # Store the different nominal voltage values
            "convex_hull_area_sqmi": 0,  # Convex hull area for the feeder
            "substation_name": _src,
            "feeder_type": None,
        }
        if "feeder_types" in self.__dict__ and network in self.feeder_types:
            results["Feeder_type"] = self.feeder_types[network]
        return results

    def analyze_object(self, obj, feeder_name):
        """
        This function takes as input a DiTTo object and the name of the corresponding feeder, and analyze it.
        All information needed for the metric extraction is updated here.
        """
        # Get the network and the source
        try:
            _net = self.feeder_networks[feeder_name]
        except KeyError:
            _net = self.G.graph
        try:
            _src = self.substations[feeder_name]
        except:
            _src = self.source

        # If the object has some coordinate values
        # then we add the points to the list of points for the feeder
        if hasattr(obj, "positions") and obj.positions is not None:
            for position in obj.positions:
                X = position.long
                Y = position.lat
                if X is not None and Y is not None:
                    if feeder_name in self.points:
                        self.points[feeder_name].append([X, Y])
                    else:
                        self.points[feeder_name] = [[X, Y]]

        # Nominal voltage
        if hasattr(obj, "nominal_voltage"):
            if obj.nominal_voltage not in self.results[feeder_name]["nominal_voltages"]:
                self.results[feeder_name]["nominal_voltages"].append(
                    obj.nominal_voltage
                )

        # If we get a line
        if isinstance(obj, Line):

            # Update the number of links to adjacent feeders
            # Look at the to and from element
            # If they have a valid feeder name attribute, simply compare the two and
            # update the count if needed
            if (
                hasattr(obj, "from_element")
                and obj.from_element is not None
                and hasattr(obj, "to_element")
                and obj.to_element is not None
            ):
                try:
                    _from = self.model[obj.from_element]
                    _to = self.model[obj.to_element]
                except KeyError:
                    _from = None
                    _to = None
                if (
                    hasattr(_from, "feeder_name")
                    and _from.feeder_name is not None
                    and hasattr(_to, "feeder_name")
                    and _to.feeder_name is not None
                ):
                    if _from.feeder_name != _to.feeder_name:
                        self.results[feeder_name]["num_links_adjacent_feeders"] += 1

            # Update the counts
            #
            # Fuses
            if obj.is_fuse is True:
                self.results[feeder_name]["num_fuses"] += 1

            # Switches
            if obj.is_switch == 1:
                self.results[feeder_name]["num_switches"] += 1
                if hasattr(obj, "nameclass") and obj.nameclass is not None:
                    if (
                        obj.nameclass
                        in self.results[feeder_name]["switch_categories_distribution"]
                    ):
                        self.results[feeder_name]["switch_categories_distribution"][
                            obj.nameclass
                        ] += 1
                    else:
                        self.results[feeder_name]["switch_categories_distribution"][
                            obj.nameclass
                        ] = 1

            # Reclosers
            if obj.is_recloser == 1:
                self.results[feeder_name]["num_reclosers"] += 1

            # Breakers
            if obj.is_breaker == 1:
                self.results[feeder_name]["num_breakers"] += 1

            # Sectionalizers
            if obj.is_sectionalizer == 1:
                self.results[feeder_name]["num_sectionalizers"] += 1

            if hasattr(obj, "wires") and obj.wires is not None:
                # Get the phases (needed later)
                phases = [
                    wire.phase
                    for wire in obj.wires
                    if wire.phase in ["A", "B", "C"] and wire.drop != 1
                ]

                # Get the equipment name distribution
                equipment_names = [wire.nameclass for wire in obj.wires]
                for eq in equipment_names:
                    if eq in self.results[feeder_name]["wire_equipment_distribution"]:
                        self.results[feeder_name]["wire_equipment_distribution"][
                            eq
                        ] += 1
                    else:
                        self.results[feeder_name]["wire_equipment_distribution"][eq] = 1

            # If we do not have phase information, raise an error...
            else:
                raise ValueError("No phase information for line {}".format(obj.name))

            # If the line is low voltage
            if (
                obj.nominal_voltage is not None
                and obj.nominal_voltage * math.sqrt(3) <= self.LV_threshold
            ):

                # Update the counter for low voltage line length
                if hasattr(obj, "length") and obj.length >= 0:
                    self.results[feeder_name]["lv_len_mi"] += obj.length

                    # Update the counters for specific number of phases
                    if phases is not None:

                        # Single Phase low voltage line
                        if len(phases) == 1:
                            self.results[feeder_name]["lv_1ph_len_mi"] += obj.length

                            # Single Phase low voltage Overhead Line
                            if obj.line_type == "overhead":
                                self.results[feeder_name][
                                    "lv_oh_1ph_len_mi"
                                ] += obj.length

                        # Two Phase low voltage Line
                        elif len(phases) == 2:
                            self.results[feeder_name]["lv_2ph_len_mi"] += obj.length

                            # Two Phase low voltage Overhead Line
                            if obj.line_type == "overhead":
                                self.results[feeder_name][
                                    "lv_oh_2ph_len_mi"
                                ] += obj.length

                        # Three Phase low voltage Line
                        elif len(phases) == 3:
                            self.results[feeder_name]["lv_3ph_len_mi"] += obj.length

                            # Three Phase low voltage Overhead Line
                            if obj.line_type == "overhead":
                                self.results[feeder_name][
                                    "lv_oh_3ph_len_mi"
                                ] += obj.length

            # If the line is medium voltage
            elif (
                obj.nominal_voltage is not None
                and self.MV_threshold
                > obj.nominal_voltage * math.sqrt(3)
                > self.LV_threshold
            ):

                # Update the counter for low voltage line length
                if hasattr(obj, "length") and obj.length >= 0:
                    self.results[feeder_name]["mv_len_mi"] += obj.length

                    # Update the counters for specific number of phases
                    if phases is not None:

                        # Single Phase medium voltage line
                        if len(phases) == 1:
                            self.results[feeder_name]["mv_1ph_len_mi"] += obj.length

                            # Single Phase medium voltage Overhead line
                            if obj.line_type == "overhead":
                                self.results[feeder_name][
                                    "mv_oh_1ph_len_mi"
                                ] += obj.length

                        # Two Phase medium voltage line
                        elif len(phases) == 2:
                            self.results[feeder_name]["mv_2ph_len_mi"] += obj.length

                            # Two Phase medium voltage Overhead line
                            if obj.line_type == "overhead":
                                self.results[feeder_name][
                                    "mv_oh_2ph_len_mi"
                                ] += obj.length

                        # Three Phase medium voltage line
                        elif len(phases) == 3:
                            self.results[feeder_name]["mv_3ph_len_mi"] += obj.length

                            # Three Phase medium voltage Overhead line
                            if obj.line_type == "overhead":
                                self.results[feeder_name][
                                    "mv_oh_3ph_len_mi"
                                ] += obj.length

            return

        # If we get a load
        if isinstance(obj, Load):

            if hasattr(obj, "num_users") and obj.num_users is not None:
                self.results[feeder_name]["num_customers"] += obj.num_users

            # If we use the loads to compute the kva distribution...
            if not self.compute_kva_density_with_transformers:
                if (
                    hasattr(obj, "transformer_connected_kva")
                    and obj.transformer_connected_kva is not None
                ):
                    self.results[feeder_name]["sum_distribution_transformer_mva"] += (
                        obj.transformer_connected_kva * 10 ** -6
                    )

            if (
                hasattr(obj, "upstream_transformer_name")
                and obj.upstream_transformer_name is not None
            ):
                # Number of loads per distribution transformer
                if (
                    obj.upstream_transformer_name
                    in self.results[feeder_name]["num_load_per_transformer"]
                ):
                    self.results[feeder_name]["num_load_per_transformer"][
                        obj.upstream_transformer_name
                    ] += 1
                else:
                    self.results[feeder_name]["num_load_per_transformer"][
                        obj.upstream_transformer_name
                    ] = 1

                # Number of customers per distribution transformer
                if (
                    obj.upstream_transformer_name
                    in self.results[feeder_name]["num_customer_per_transformer"]
                ):
                    self.results[feeder_name]["num_customer_per_transformer"][
                        obj.upstream_transformer_name
                    ] += 1
                else:
                    self.results[feeder_name]["num_customer_per_transformer"][
                        obj.upstream_transformer_name
                    ] = 1

                # Line impedance list
                # Get the secondary
                trans_obj = self.model[obj.upstream_transformer_name]
                if (
                    hasattr(trans_obj, "to_element")
                    and trans_obj.to_element is not None
                ):
                    _net3 = _net.copy()
                    if not _net3.has_node(trans_obj.to_element):
                        _sp = nx.shortest_path(
                            self.G.graph, trans_obj.to_element, list(_net3.nodes())[0]
                        )
                        for n1, n2 in zip(_sp[:-1], _sp[1:]):
                            _net3.add_edge(
                                n1, n2, length=self.G.graph[n1][n2]["length"]
                            )
                    self.results[feeder_name]["trans_cust_impedance_list"][
                        obj.name
                    ] = self.get_impedance_list_between_nodes(
                        _net3, trans_obj.to_element, obj.connecting_element
                    )

            # If the load is low voltage
            if hasattr(obj, "nominal_voltage") and obj.nominal_voltage is not None:
                if obj.nominal_voltage * math.sqrt(3) <= self.LV_threshold:

                    # Update the counters
                    if hasattr(obj, "phase_loads") and obj.phase_loads is not None:

                        _phase_loads_ = [p for p in obj.phase_loads if p.drop != 1]

                        # One phase low voltage load count
                        if len(_phase_loads_) == 1:
                            self.results[feeder_name]["num_lv_1ph_loads"] += 1

                        # Three phase low voltage load count
                        elif len(_phase_loads_) == 3:
                            self.results[feeder_name]["num_lv_3ph_loads"] += 1

                        # The following block keeps track of the total active power for each phase
                        for phase_load in _phase_loads_:
                            if hasattr(phase_load, "phase") and phase_load.phase in [
                                "A",
                                "B",
                                "C",
                            ]:
                                if (
                                    hasattr(phase_load, "p")
                                    and phase_load.p is not None
                                ):

                                    # Phase A
                                    if phase_load.phase == "A":
                                        self.results[feeder_name][
                                            "sum_lv_pha_load_kw"
                                        ] += phase_load.p

                                    # Phase B
                                    elif phase_load.phase == "B":
                                        self.results[feeder_name][
                                            "sum_lv_phb_load_kw"
                                        ] += phase_load.p

                                    # Phase C
                                    elif phase_load.phase == "C":
                                        self.results[feeder_name][
                                            "sum_lv_phc_load_kw"
                                        ] += phase_load.p

                # If the load is medium voltage
                elif (
                    self.MV_threshold
                    > obj.nominal_voltage * math.sqrt(3)
                    > self.LV_threshold
                ):
                    if hasattr(obj, "phase_loads") and obj.phase_loads is not None:

                        _phase_loads_ = [p for p in obj.phase_loads if p.drop != 1]

                        # Update the count of three phase medium voltage loads
                        if len(_phase_loads_) == 3:
                            self.results[feeder_name]["num_mv_3ph_loads"] += 1

            # Total demand and total KVAR updates
            if hasattr(obj, "phase_loads") and obj.phase_loads is not None:

                _phase_loads_ = [p for p in obj.phase_loads if p.drop != 1]

                # If P and Q are zero for all phase and we have the KVA of the connected_transformer, then use that...
                if np.all(np.array([pl.p for pl in _phase_loads_]) == 0) and np.all(
                    np.array([pl.q for pl in _phase_loads_]) == 0
                ):
                    if (
                        obj.transformer_connected_kva is not None
                        and obj.transformer_connected_kva != 0
                    ):
                        self.results[feeder_name][
                            "sum_load_kw"
                        ] += obj.transformer_connected_kva
                        self.load_distribution.append(obj.transformer_connected_kva)
                        # Assume balance accross phases...
                        for phase_load in [p for p in obj.phase_loads if p.drop != 1]:
                            if hasattr(phase_load, "phase") and phase_load.phase in [
                                "A",
                                "B",
                                "C",
                            ]:
                                if (
                                    hasattr(phase_load, "p")
                                    and phase_load.p is not None
                                ):
                                    if phase_load.phase == "A":
                                        self.results[feeder_name][
                                            "sum_load_pha_kw"
                                        ] += float(
                                            obj.transformer_connected_kva
                                        ) / float(
                                            len(_phase_loads_)
                                        )
                                    elif phase_load.phase == "B":
                                        self.results[feeder_name][
                                            "sum_load_phb_kw"
                                        ] += float(
                                            obj.transformer_connected_kva
                                        ) / float(
                                            len(_phase_loads_)
                                        )
                                    elif phase_load.phase == "C":
                                        self.results[feeder_name][
                                            "sum_load_phc_kw"
                                        ] += float(
                                            obj.transformer_connected_kva
                                        ) / float(
                                            len(_phase_loads_)
                                        )
                else:
                    self.results[feeder_name]["sum_load_kw"] += np.sum(
                        [pl.p for pl in _phase_loads_ if pl.p is not None]
                    )
                    self.load_distribution.append(
                        np.sum([pl.p for pl in _phase_loads_ if pl.p is not None])
                    )

                    for phase_load in [p for p in obj.phase_loads if p.drop != 1]:
                        if hasattr(phase_load, "phase") and phase_load.phase in [
                            "A",
                            "B",
                            "C",
                        ]:
                            if hasattr(phase_load, "p") and phase_load.p is not None:
                                if phase_load.phase == "A":
                                    self.results[feeder_name][
                                        "sum_load_pha_kw"
                                    ] += phase_load.p
                                elif phase_load.phase == "B":
                                    self.results[feeder_name][
                                        "sum_load_phb_kw"
                                    ] += phase_load.p
                                elif phase_load.phase == "C":
                                    self.results[feeder_name][
                                        "sum_load_phc_kw"
                                    ] += phase_load.p

                self.results[feeder_name]["sum_load_kvar"] += np.sum(
                    [pl.q for pl in _phase_loads_ if pl.q is not None]
                )
                # Pass if P and Q are zero (might happen in some datasets...)
                try:
                    load_power_factor = obj.phase_loads[0].p / float(
                        math.sqrt(obj.phase_loads[0].p ** 2 + obj.phase_loads[0].q ** 2)
                    )
                    self.results[feeder_name]["power_factor_distribution"].append(
                        load_power_factor
                    )
                except ZeroDivisionError:
                    pass

            return

        # If we get a regulator
        if isinstance(obj, Regulator):

            # Update the count
            self.results[feeder_name]["num_regulators"] += 1

            return

        # If we get a capacitor
        if isinstance(obj, Capacitor):

            # Update the count
            self.results[feeder_name]["num_capacitors"] += 1

            return

        # If we get a Transformer
        if isinstance(obj, PowerTransformer):

            # Determine if the transformer is overloaded or not
            # If we have the load names in the mapping for this transformer...
            if obj.name in self.transformer_load_mapping:
                load_names = self.transformer_load_mapping[obj.name]

                # Get the primary
                if hasattr(obj, "from_element") and obj.from_element is not None:
                    _net2 = _net.copy()
                    if not _net2.has_node(_src):
                        _sp = nx.shortest_path(
                            self.G.graph, _src, list(_net2.nodes())[0]
                        )
                        for n1, n2 in zip(_sp[:-1], _sp[1:]):
                            _net2.add_edge(
                                n1, n2, length=self.G.graph[n1][n2]["length"]
                            )

                    self.results[feeder_name]["sub_trans_impedance_list"][
                        obj.name
                    ] = self.get_impedance_list_between_nodes(
                        _net2, _src, obj.from_element
                    )

                # This section updates the maximum length of secondaries
                # If the graph contains the transformer's connecting element
                if (
                    hasattr(obj, "to_element")
                    and obj.to_element is not None
                    and self.G.graph.has_node(obj.to_element)
                ):
                    # Compute the distance from the transformer's connecting
                    # element to every load downstream of it
                    for load_name in load_names:
                        try:
                            load_obj = self.model[load_name]
                        except KeyError:
                            load_obj = None
                        if (
                            hasattr(load_obj, "connecting_element")
                            and load_obj.connecting_element is not None
                        ):
                            if self.G.graph.has_node(load_obj.connecting_element):
                                length = nx.shortest_path_length(
                                    self.G.graph,
                                    obj.to_element,
                                    load_obj.connecting_element,
                                    weight="length",
                                )
                                if (
                                    length
                                    > self.results[feeder_name][
                                        "max_len_secondaries_mi"
                                    ]
                                ):
                                    self.results[feeder_name][
                                        "max_len_secondaries_mi"
                                    ] = length

                # ...compute the total load KVA downstream
                total_load_kva = 0
                for load_name in load_names:
                    try:
                        load_obj = self.model[load_name]
                    except KeyError:
                        load_obj = None
                    if (
                        hasattr(load_obj, "phase_loads")
                        and load_obj.phase_loads is not None
                    ):
                        for pl in load_obj.phase_loads:
                            if (
                                hasattr(pl, "p")
                                and pl.p is not None
                                and hasattr(pl, "q")
                                and pl.q is not None
                            ):
                                total_load_kva += math.sqrt(pl.p ** 2 + pl.q ** 2)
                # ...compute the transformer KVA
                if hasattr(obj, "windings") and obj.windings is not None:
                    transformer_kva = max(
                        [
                            wdg.rated_power
                            for wdg in obj.windings
                            if wdg.rated_power is not None
                        ]  # The kva values should be the same on all windings but we take the max
                    )
                    self.results[feeder_name]["transformer_kva_distribution"].append(
                        transformer_kva
                    )
                # ...and, compare the two values
                if total_load_kva > transformer_kva:
                    self.results[feeder_name]["num_overloaded_transformers"] += 1
                # Store the ratio of load to transformer KVA
                if transformer_kva != 0:
                    self.results[feeder_name][
                        "ratio_load_kW_to_transformer_KVA_distribution"
                    ][obj.name] = float(total_load_kva) / float(transformer_kva)
                else:
                    self.results[feeder_name][
                        "ratio_load_kW_to_transformer_KVA_distribution"
                    ][obj.name] = np.nan

            if (
                hasattr(obj, "windings")
                and obj.windings is not None
                and len(obj.windings) > 0
            ):

                if (
                    hasattr(obj.windings[0], "nominal_voltage")
                    and obj.windings[0].nominal_voltage is not None
                    and hasattr(obj.windings[1], "nominal_voltage")
                    and obj.windings[1].nominal_voltage is not None
                    and obj.windings[0].nominal_voltage
                    != obj.windings[1].nominal_voltage
                ):
                    self.results[feeder_name]["num_distribution_transformers"] += 1

                    # If we use the transformers to compute the kva distribution
                    if self.compute_kva_density_with_transformers:
                        if (
                            hasattr(obj.windings[0], "rated_power")
                            and obj.windings[0].rated_power is not None
                        ):
                            self.results[feeder_name][
                                "sum_distribution_transformer_mva"
                            ] += (
                                obj.windings[0].rated_power * 10 ** -6
                            )  # DiTTo in va

                    if (
                        hasattr(obj.windings[0], "phase_windings")
                        and obj.windings[0].phase_windings is not None
                    ):
                        if len(obj.windings[0].phase_windings) == 1:
                            self.results[feeder_name]["num_1ph_transformers"] += 1
                        elif len(obj.windings[0].phase_windings) == 3:
                            self.results[feeder_name]["num_3ph_transformers"] += 1

            return

    def get_feeder(self, obj):
        """
        Returns the name of the feeder which contains the given object.
        If no matching feeder is found, the function returns None.
        """
        if obj.name in self.node_feeder_mapping:
            return self.node_feeder_mapping[obj.name]
        elif (
            hasattr(obj, "connecting_element")
            and obj.connecting_element in self.node_feeder_mapping
        ):
            return self.node_feeder_mapping[obj.connecting_element]
        elif (
            hasattr(obj, "from_element")
            and obj.from_element in self.node_feeder_mapping
        ):
            return self.node_feeder_mapping[obj.from_element]
        else:
            logger.debug("Could not find feeder for {}".format(obj.name))
            return None

    def compute_all_metrics_per_feeder(self, **kwargs):
        """
        Computes all the available metrics for each feeder.
        """
        # Enables changing the flag
        if "compute_kva_density_with_transformers" in kwargs and isinstance(
            kwargs["compute_kva_density_with_transformers"], bool
        ):
            self.compute_kva_density_with_transformers = kwargs[
                "compute_kva_density_with_transformers"
            ]

        self.transformer_load_mapping = self.get_transformer_load_mapping()
        self.compute_node_line_mapping()
        self.load_distribution = []
        # List of keys that will have to be converted to miles (DiTTo is in meter)
        keys_to_convert_to_miles = [
            "lv_len_mi",
            "mv_len_mi",
            "mv_1ph_len_mi",
            "mv_2ph_len_mi",
            "mv_3ph_len_mi",
            "lv_1ph_len_mi",
            "lv_2ph_len_mi",
            "lv_3ph_len_mi",
            "mv_oh_1ph_len_mi",
            "mv_oh_2ph_len_mi",
            "mv_oh_3ph_len_mi",
            "lv_oh_1ph_len_mi",
            "lv_oh_2ph_len_mi",
            "lv_oh_3ph_len_mi",
            "max_len_secondaries_mi",
            "avg_recloser_sub_distance_mi",
            "avg_regulator_sub_distance_mi",
            "avg_capacitor_sub_distance_mi",
        ]

        # List of keys to divide by 10^3
        keys_to_divide_by_1000 = [
            "sum_load_kw",
            "sum_load_kvar",
            "sum_lv_pha_load_kw",
            "sum_lv_phb_load_kw",
            "sum_lv_phc_load_kw",
            "sum_load_pha_kw",
            "sum_load_phb_kw",
            "sum_load_phc_kw",
        ]

        mv_feeder_names = [
            k
            for k in self.feeder_names
            if self.substations[k] is not None and len(self.substations[k]) > 0
        ]

        # Setup the data structures for all feeders
        self.results = {
            k: self.setup_results_data_structure(k) for k in mv_feeder_names
        }

        # Loop over the objects in the model and analyze them
        for obj in self.model.models:
            # Get the feeder of this object if it exists
            if hasattr(obj, "name"):
                _feeder_ref = self.get_feeder(obj)
                # If we have a valid name, analyze the object
                if _feeder_ref is not None and _feeder_ref in mv_feeder_names:
                    self.analyze_object(obj, _feeder_ref)

        # Do some post-processing of the results before returning them
        #
        # Compute the percentages of low voltage load kW for each phase
        for _feeder_ref in mv_feeder_names:
            total_demand_LV = (
                self.results[_feeder_ref]["sum_lv_pha_load_kw"]
                + self.results[_feeder_ref]["sum_lv_phb_load_kw"]
                + self.results[_feeder_ref]["sum_lv_phc_load_kw"]
            )
            if total_demand_LV != 0:
                self.results[_feeder_ref]["perct_lv_pha_load_kw"] = (
                    float(self.results[_feeder_ref]["sum_lv_pha_load_kw"])
                    / float(total_demand_LV)
                    * 100
                )
                self.results[_feeder_ref]["perct_lv_phb_load_kw"] = (
                    float(self.results[_feeder_ref]["sum_lv_phb_load_kw"])
                    / float(total_demand_LV)
                    * 100
                )
                self.results[_feeder_ref]["perct_lv_phc_load_kw"] = (
                    float(self.results[_feeder_ref]["sum_lv_phc_load_kw"])
                    / float(total_demand_LV)
                    * 100
                )
            else:
                self.results[_feeder_ref]["perct_lv_pha_load_kw"] = 0
                self.results[_feeder_ref]["perct_lv_phb_load_kw"] = 0
                self.results[_feeder_ref]["perct_lv_phc_load_kw"] = 0

            # ratio_1phto3ph_Xfrm
            if self.results[_feeder_ref]["num_3ph_transformers"] != 0:
                self.results[_feeder_ref]["ratio_1ph_to_3ph_transformers"] = float(
                    self.results[_feeder_ref]["num_1ph_transformers"]
                ) / float(self.results[_feeder_ref]["num_3ph_transformers"])
            else:
                self.results[_feeder_ref]["ratio_1ph_to_3ph_transformers"] = np.inf

            # avg_nb_load_per_transformer
            if len(self.results[_feeder_ref]["num_load_per_transformer"]) > 0:
                self.results[_feeder_ref]["avg_num_load_per_transformer"] = np.mean(
                    list(self.results[_feeder_ref]["num_load_per_transformer"].values())
                )

            # Convert to miles
            for k in keys_to_convert_to_miles:
                if k in self.results[_feeder_ref]:
                    self.results[_feeder_ref][k] *= 0.000621371

            # Divide by 10^3
            for k in keys_to_divide_by_1000:
                if k in self.results[_feeder_ref]:
                    self.results[_feeder_ref][k] *= 10 ** -3

            # Ratio of MV Line Length to Number of Customers
            if self.results[_feeder_ref]["num_customers"] != 0:
                self.results[_feeder_ref]["ratio_mv_len_to_num_cust"] = self.results[
                    _feeder_ref
                ]["mv_len_mi"] / float(self.results[_feeder_ref]["num_customers"])
            else:
                self.results[_feeder_ref]["ratio_mv_len_to_num_cust"] = np.nan

            # Percent of Overhead MV Lines
            try:
                self.results[_feeder_ref]["perct_mv_oh_len"] = (
                    (
                        self.results[_feeder_ref]["mv_oh_1ph_len_mi"]
                        + self.results[_feeder_ref]["mv_oh_2ph_len_mi"]
                        + self.results[_feeder_ref]["mv_oh_3ph_len_mi"]
                    )
                    / float(
                        self.results[_feeder_ref]["lv_len_mi"]
                        + self.results[_feeder_ref]["mv_len_mi"]
                    )
                    * 100
                )
            except ZeroDivisionError:
                self.results[_feeder_ref]["perct_mv_oh_len"] = np.nan

            # Percent of Overhead LV Lines
            try:
                self.results[_feeder_ref]["perct_lv_oh_len"] = (
                    (
                        self.results[_feeder_ref]["lv_oh_1ph_len_mi"]
                        + self.results[_feeder_ref]["lv_oh_2ph_len_mi"]
                        + self.results[_feeder_ref]["lv_oh_3ph_len_mi"]
                    )
                    / float(
                        self.results[_feeder_ref]["lv_len_mi"]
                        + self.results[_feeder_ref]["mv_len_mi"]
                    )
                    * 100
                )
            except ZeroDivisionError:
                self.results[_feeder_ref]["perct_lv_oh_len"] = np.nan

            # Sectionalizers per recloser
            if float(self.results[_feeder_ref]["num_reclosers"]) != 0:
                self.results[_feeder_ref]["num_sectionalizers_per_recloser"] = float(
                    self.results[_feeder_ref]["num_sectionalizers"]
                ) / float(self.results[_feeder_ref]["num_reclosers"])
            else:
                self.results[_feeder_ref]["num_sectionalizers_per_recloser"] = np.nan

            # Average load power factor
            self.results[_feeder_ref]["avg_load_pf"] = np.mean(
                self.results[_feeder_ref]["power_factor_distribution"]
            )

            # Average imbalance of load by phase
            #
            # sum_i |tot_demand_phase_i - 1/3 * tot_demand|
            if self.results[_feeder_ref]["sum_load_kw"] != 0:
                third_tot_demand = self.results[_feeder_ref]["sum_load_kw"] / 3.0
                self.results[_feeder_ref]["avg_load_imbalance_by_phase"] = (
                    abs(self.results[_feeder_ref]["sum_load_pha_kw"] - third_tot_demand)
                    + abs(
                        self.results[_feeder_ref]["sum_load_phb_kw"] - third_tot_demand
                    )
                    + abs(
                        self.results[_feeder_ref]["sum_load_phc_kw"] - third_tot_demand
                    )
                ) / self.results[_feeder_ref]["sum_load_kw"]
            else:
                self.results[_feeder_ref]["avg_load_imbalance_by_phase"] = np.nan

            # Ratio of LV line length to number of customers
            if self.results[_feeder_ref]["num_customers"] != 0:
                self.results[_feeder_ref]["ratio_lv_len_to_num_cust"] = self.results[
                    _feeder_ref
                ]["lv_len_mi"] / float(self.results[_feeder_ref]["num_customers"])
            else:
                self.results[_feeder_ref]["ratio_mv_len_to_num_cust"] = np.nan

            # Line impedances
            #
            # Average and Maximum MV line impedance from substation to MV side of distribution transformer
            self.results[_feeder_ref]["avg_mv_line_impedance_sub_transformers"] = {}
            self.results[_feeder_ref]["max_mv_line_impedance_sub_transformers"] = {}

            for trans_name, imp_list in self.results[_feeder_ref][
                "sub_trans_impedance_list"
            ].items():
                if len(imp_list) > 0:
                    self.results[_feeder_ref]["avg_mv_line_impedance_sub_transformers"][
                        trans_name
                    ] = np.mean(imp_list)
                    self.results[_feeder_ref]["max_mv_line_impedance_sub_transformers"][
                        trans_name
                    ] = np.max(imp_list)
                else:
                    self.results[_feeder_ref]["avg_mv_line_impedance_sub_transformers"][
                        trans_name
                    ] = None
                    self.results[_feeder_ref]["max_mv_line_impedance_sub_transformers"][
                        trans_name
                    ] = None

            # Average and Maximum LV line impedance from distribution transformer to customer
            self.results[_feeder_ref]["avg_lv_line_impedance_transformer_cust"] = {}
            self.results[_feeder_ref]["max_lv_line_impedance_transformer_cust"] = {}

            for cust_name, imp_list in self.results[_feeder_ref][
                "trans_cust_impedance_list"
            ].items():
                if len(imp_list) > 0:
                    self.results[_feeder_ref]["avg_lv_line_impedance_transformer_cust"][
                        cust_name
                    ] = np.mean(imp_list)
                    self.results[_feeder_ref]["max_lv_line_impedance_transformer_cust"][
                        cust_name
                    ] = np.max(imp_list)
                else:
                    self.results[_feeder_ref]["avg_lv_line_impedance_transformer_cust"][
                        cust_name
                    ] = None
                    self.results[_feeder_ref]["max_lv_line_impedance_transformer_cust"][
                        cust_name
                    ] = None

            try:
                self.results[_feeder_ref]["nominal_medium_voltage_class"] = np.max(
                    [
                        x
                        for x in self.results[_feeder_ref]["nominal_voltages"]
                        if x != None
                    ]
                )
            except:
                self.results[_feeder_ref]["nominal_medium_voltage_class"] = np.nan

            # Density metrics
            #
            # Get the list of points for the feeder
            self.results[_feeder_ref]["cust_density"] = np.nan
            self.results[_feeder_ref]["load_density_kw"] = np.nan
            self.results[_feeder_ref]["load_density_kvar"] = np.nan
            self.results[_feeder_ref]["kva_density"] = np.nan

            try:
                _points = np.array(self.points[_feeder_ref])
            except KeyError:
                _points = []
            # Having more than 2 points to compute the convex hull surface is a good thing...
            unique_points = set()
            for arr in _points:
                unique_points.add(tuple(list(arr)))
            if len(_points) > 2 and len(unique_points) > 4:  # Ignore tiny feeders
                hull = ConvexHull(_points)  # Compute the Convex Hull using Scipy
                hull_surf_sqmile = (
                    hull.area * 3.86102 * 10 ** -7
                )  # Convert surface from square meters to square miles
                self.results[_feeder_ref][
                    "convex_hull_area_sqmi"
                ] = hull_surf_sqmile  # Store the convex hull area
                if hull_surf_sqmile != 0:
                    self.results[_feeder_ref]["cust_density"] = float(
                        self.results[_feeder_ref]["num_customers"]
                    ) / float(hull_surf_sqmile)
                    self.results[_feeder_ref]["load_density_kw"] = float(
                        self.results[_feeder_ref]["sum_load_kw"]
                    ) / float(hull_surf_sqmile)
                    self.results[_feeder_ref]["load_density_kvar"] = float(
                        self.results[_feeder_ref]["sum_load_kvar"]
                    ) / float(hull_surf_sqmile)
                    self.results[_feeder_ref]["kva_density"] = float(
                        10 ** 3
                        * self.results[_feeder_ref]["sum_distribution_transformer_mva"]
                    ) / float(hull_surf_sqmile)

    def compute_all_metrics(self, *args, **kwargs):
        """
        This function computes all the metrics for the whole network in a way that optimizes performance.
        Instead of calling all the metrics one by one, we loop over the objects only once and update the metrics.

        .. note:: If you only need a very few metrics, it is probably better to call the functions responsible for them.
        """
        if len(args) == 1:
            f_name = args[0]
        else:
            f_name = "global"

        # Enables changing the flag
        if "compute_kva_density_with_transformers" in kwargs and isinstance(
            kwargs["compute_kva_density_with_transformers"], bool
        ):
            self.compute_kva_density_with_transformers = kwargs[
                "compute_kva_density_with_transformers"
            ]

        self.results = {f_name: self.setup_results_data_structure()}
        self.transformer_load_mapping = self.get_transformer_load_mapping()
        self.compute_node_line_mapping()
        self.load_distribution = []
        # List of keys that will have to be converted to miles (DiTTo is in meter)
        keys_to_convert_to_miles = [
            "lv_len_mi",
            "mv_len_mi",
            "mv_1ph_len_mi",
            "mv_2ph_len_mi",
            "mv_3ph_len_mi",
            "lv_1ph_len_mi",
            "lv_2ph_len_mi",
            "lv_3ph_len_mi",
            "mv_oh_1ph_len_mi",
            "mv_oh_2ph_len_mi",
            "mv_oh_3ph_len_mi",
            "lv_oh_1ph_len_mi",
            "lv_oh_2ph_len_mi",
            "lv_oh_3ph_len_mi",
            "max_len_secondaries_mi",
            "avg_recloser_sub_distance_mi",
            "avg_regulator_sub_distance_mi",
            "avg_capacitor_sub_distance_mi",
        ]

        # List of keys to divide by 10^3
        keys_to_divide_by_1000 = [
            "sum_load_kw",
            "sum_load_kvar",
            "sum_lv_pha_load_kw",
            "sum_lv_phb_load_kw",
            "sum_lv_phc_load_kw",
            "sum_load_pha_kw",
            "sum_load_phb_kw",
            "sum_load_phc_kw",
        ]

        # Loop over the objects in the model and analyze them
        for obj in self.model.models:
            self.analyze_object(obj, f_name)

        # Do some post-processing of the results before returning them
        #
        # Compute the percentages of low voltage load kW for each phase
        _feeder_ref = f_name

        total_demand_LV = (
            self.results[_feeder_ref]["sum_lv_pha_load_kw"]
            + self.results[_feeder_ref]["sum_lv_phb_load_kw"]
            + self.results[_feeder_ref]["sum_lv_phc_load_kw"]
        )
        if total_demand_LV != 0:
            self.results[_feeder_ref]["perct_lv_pha_load_kw"] = (
                float(self.results[_feeder_ref]["sum_lv_pha_load_kw"])
                / float(total_demand_LV)
                * 100
            )
            self.results[_feeder_ref]["perct_lv_phb_load_kw"] = (
                float(self.results[_feeder_ref]["sum_lv_phb_load_kw"])
                / float(total_demand_LV)
                * 100
            )
            self.results[_feeder_ref]["perct_lv_phc_load_kw"] = (
                float(self.results[_feeder_ref]["sum_lv_phc_load_kw"])
                / float(total_demand_LV)
                * 100
            )
        else:
            self.results[_feeder_ref]["perct_lv_pha_load_kw"] = 0
            self.results[_feeder_ref]["perct_lv_phb_load_kw"] = 0
            self.results[_feeder_ref]["perct_lv_phc_load_kw"] = 0

        # ratio_1phto3ph_Xfrm
        if self.results[_feeder_ref]["num_3ph_transformers"] != 0:
            self.results[_feeder_ref]["ratio_1ph_to_3ph_transformers"] = float(
                self.results[_feeder_ref]["num_1ph_transformers"]
            ) / float(self.results[_feeder_ref]["num_3ph_transformers"])
        else:
            self.results[_feeder_ref]["ratio_1ph_to_3ph_transformers"] = np.inf

        # avg_nb_load_per_transformer
        if len(self.results[_feeder_ref]["num_load_per_transformer"]) > 0:
            self.results[_feeder_ref]["avg_num_load_per_transformer"] = np.mean(
                list(self.results[_feeder_ref]["num_load_per_transformer"].values())
            )

        # Convert to miles
        for k in keys_to_convert_to_miles:
            if k in self.results[_feeder_ref]:
                self.results[_feeder_ref][k] *= 0.000621371

        # Divide by 10^3
        for k in keys_to_divide_by_1000:
            if k in self.results[_feeder_ref]:
                self.results[_feeder_ref][k] *= 10 ** -3

        # Ratio of MV Line Length to Number of Customers
        if self.results[_feeder_ref]["num_customers"] != 0:
            self.results[_feeder_ref]["ratio_mv_len_to_num_cust"] = self.results[
                _feeder_ref
            ]["mv_len_mi"] / float(self.results[_feeder_ref]["num_customers"])
        else:
            self.results[_feeder_ref]["ratio_mv_len_to_num_cust"] = np.nan

        # Percent of Overhead MV Lines
        try:
            self.results[_feeder_ref]["perct_mv_oh_len"] = (
                (
                    self.results[_feeder_ref]["mv_oh_1ph_len_mi"]
                    + self.results[_feeder_ref]["mv_oh_2ph_len_mi"]
                    + self.results[_feeder_ref]["mv_oh_3ph_len_mi"]
                )
                / float(
                    self.results[_feeder_ref]["lv_len_mi"]
                    + self.results[_feeder_ref]["mv_len_mi"]
                )
                * 100
            )
        except ZeroDivisionError:
            self.results[_feeder_ref]["perct_mv_oh_len"] = np.nan

        # Percent of Overhead LV Lines
        try:
            self.results[_feeder_ref]["perct_lv_oh_len"] = (
                (
                    self.results[_feeder_ref]["lv_oh_1ph_len_mi"]
                    + self.results[_feeder_ref]["lv_oh_2ph_len_mi"]
                    + self.results[_feeder_ref]["lv_oh_3ph_len_mi"]
                )
                / float(
                    self.results[_feeder_ref]["lv_len_mi"]
                    + self.results[_feeder_ref]["mv_len_mi"]
                )
                * 100
            )
        except ZeroDivisionError:
            self.results[_feeder_ref]["perct_lv_oh_len"] = np.nan

        # Sectionalizers per recloser
        if float(self.results[_feeder_ref]["num_reclosers"]) != 0:
            self.results[_feeder_ref]["num_sectionalizers_per_recloser"] = float(
                self.results[_feeder_ref]["num_sectionalizers"]
            ) / float(self.results[_feeder_ref]["num_reclosers"])
        else:
            self.results[_feeder_ref]["num_sectionalizers_per_recloser"] = np.nan

        # Average load power factor
        self.results[_feeder_ref]["avg_load_pf"] = np.mean(
            self.results[_feeder_ref]["power_factor_distribution"]
        )

        # Average imbalance of load by phase
        #
        # sum_i |tot_demand_phase_i - 1/3 * tot_demand|
        if self.results[_feeder_ref]["sum_load_kw"] != 0:
            third_tot_demand = self.results[_feeder_ref]["sum_load_kw"] / 3.0
            self.results[_feeder_ref]["avg_load_imbalance_by_phase"] = (
                abs(self.results[_feeder_ref]["sum_load_pha_kw"] - third_tot_demand)
                + abs(self.results[_feeder_ref]["sum_load_phb_kw"] - third_tot_demand)
                + abs(self.results[_feeder_ref]["sum_load_phc_kw"] - third_tot_demand)
            ) / self.results[_feeder_ref]["sum_load_kw"]
        else:
            self.results[_feeder_ref]["avg_load_imbalance_by_phase"] = np.nan

        # Ratio of LV line length to number of customers
        if self.results[_feeder_ref]["num_customers"] != 0:
            self.results[_feeder_ref]["ratio_lv_len_to_num_cust"] = self.results[
                _feeder_ref
            ]["lv_len_mi"] / float(self.results[_feeder_ref]["num_customers"])
        else:
            self.results[_feeder_ref]["ratio_mv_len_to_num_cust"] = np.nan

        # Line impedances
        #
        # Average and Maximum MV line impedance from substation to MV side of distribution transformer
        self.results[_feeder_ref]["avg_mv_line_impedance_sub_transformers"] = {}
        self.results[_feeder_ref]["max_mv_line_impedance_sub_transformers"] = {}

        for trans_name, imp_list in self.results[_feeder_ref][
            "sub_trans_impedance_list"
        ].items():
            if len(imp_list) > 0:
                self.results[_feeder_ref]["avg_mv_line_impedance_sub_transformers"][
                    trans_name
                ] = np.mean(imp_list)
                self.results[_feeder_ref]["max_mv_line_impedance_sub_transformers"][
                    trans_name
                ] = np.max(imp_list)
            else:
                self.results[_feeder_ref]["avg_mv_line_impedance_sub_transformers"][
                    trans_name
                ] = None
                self.results[_feeder_ref]["max_mv_line_impedance_sub_transformers"][
                    trans_name
                ] = None

        # Average and Maximum LV line impedance from distribution transformer to customer
        self.results[_feeder_ref]["avg_lv_line_impedance_transformer_cust"] = {}
        self.results[_feeder_ref]["max_lv_line_impedance_transformer_cust"] = {}

        for cust_name, imp_list in self.results[_feeder_ref][
            "trans_cust_impedance_list"
        ].items():
            if len(imp_list) > 0:
                self.results[_feeder_ref]["avg_lv_line_impedance_transformer_cust"][
                    cust_name
                ] = np.mean(imp_list)
                self.results[_feeder_ref]["max_lv_line_impedance_transformer_cust"][
                    cust_name
                ] = np.max(imp_list)
            else:
                self.results[_feeder_ref]["avg_lv_line_impedance_transformer_cust"][
                    cust_name
                ] = None
                self.results[_feeder_ref]["max_lv_line_impedance_transformer_cust"][
                    cust_name
                ] = None

        try:
            self.results[_feeder_ref]["nominal_medium_voltage_class"] = np.max(
                [x for x in self.results[_feeder_ref]["nominal_voltages"] if x != None]
            )
        except:
            self.results[_feeder_ref]["nominal_medium_voltage_class"] = np.nan

        # Density metrics
        #
        # Get the list of points for the feeder
        self.results[_feeder_ref]["cust_density"] = np.nan
        self.results[_feeder_ref]["load_density_kw"] = np.nan
        self.results[_feeder_ref]["load_density_kvar"] = np.nan
        self.results[_feeder_ref]["kva_density"] = np.nan

        try:
            _points = np.array(self.points[_feeder_ref])
        except KeyError:
            _points = []
        # Having more than 2 points to compute the convex hull surface is a good thing...
        if len(_points) > 2:
            hull = ConvexHull(_points)  # Compute the Convex Hull using Scipy
            hull_surf_sqmile = (
                hull.area * 3.86102 * 10 ** -7
            )  # Convert surface from square meters to square miles
            self.results[_feeder_ref][
                "convex_hull_area_sqmi"
            ] = hull_surf_sqmile  # Store the convex hull area
            if hull_surf_sqmile != 0:
                self.results[_feeder_ref]["cust_density"] = float(
                    self.results[_feeder_ref]["num_customers"]
                ) / float(hull_surf_sqmile)
                self.results[_feeder_ref]["load_density_kw"] = float(
                    self.results[_feeder_ref]["sum_load_kw"]
                ) / float(hull_surf_sqmile)
                self.results[_feeder_ref]["load_density_kvar"] = float(
                    self.results[_feeder_ref]["sum_load_kvar"]
                ) / float(hull_surf_sqmile)
                self.results[_feeder_ref]["kva_density"] = float(
                    10 ** 3
                    * self.results[_feeder_ref]["sum_distribution_transformer_mva"]
                ) / float(hull_surf_sqmile)

    def number_of_regulators(self):
        """Returns the number of regulators."""
        return sum([1 for obj in self.model.models if isinstance(obj, Regulator)])

    def number_of_fuses(self):
        """Returns the number of fuses."""
        return sum(
            [
                1
                for obj in self.model.models
                if isinstance(obj, Line) and obj.is_fuse == 1
            ]
        )

    def number_of_reclosers(self):
        """Returns the number of reclosers."""
        return sum(
            [
                1
                for obj in self.model.models
                if isinstance(obj, Line) and obj.is_recloser == 1
            ]
        )

    def number_of_switches(self):
        """Returns the number of switches."""
        return sum(
            [
                1
                for obj in self.model.models
                if isinstance(obj, Line) and obj.is_switch == 1
            ]
        )

    def number_of_capacitors(self):
        """Returns the number of capacitors."""
        return sum([1 for obj in self.model.models if isinstance(obj, Capacitor)])

    def average_degree(self, *args):
        """Returns the average degree of the network."""
        if args:
            return np.mean([x[1] for x in list(nx.degree(args[0]))])
        else:
            return np.mean([x[1] for x in list(nx.degree(self.G.graph))])

    def diameter(self, *args):
        """Returns the diameter of the network."""
        if args:
            return nx.diameter(args[0])
        else:
            return nx.diameter(self.G.graph)

    def loops_within_feeder(self, *args):
        """Returns the number of loops within a feeder."""
        if args:
            return len(nx.cycle_basis(args[0]))
        else:
            return len(nx.cycle_basis(self.G.graph))

    def get_transformer_load_mapping(self):
        """
        Loop over the loads and go upstream in the network until a distribution transformer is found.
        Returns a dictionary where keys are transformer names and values are lists holding names of
        loads downstream of the transformer.
        """
        transformer_load_mapping = {}
        load_list = []
        for _obj in self.model.models:
            if isinstance(_obj, Load):
                load_list.append(_obj)

        # Get the connecting elements of the loads.
        # These will be the starting points of the upstream walks in the graph
        connecting_elements = [load.connecting_element for load in load_list]

        # For each connecting element...
        for idx, end_node in enumerate(connecting_elements):

            if self.G.digraph.has_node(end_node):
                should_continue = True
            else:
                should_continue = False

            # Find the upstream transformer by walking the graph upstream
            while should_continue:

                # Get predecessor node of current node in the DAG
                try:
                    from_node = next(self.G.digraph.predecessors(end_node))
                except StopIteration:
                    should_continue = False
                    continue

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
                    should_continue = False

                    # ...and grab the transformer name to retrieve the data from the DiTTo object
                    if (from_node, end_node) in self.edge_equipment_name:
                        transformer_name = self.edge_equipment_name[
                            (from_node, end_node)
                        ]
                    elif (end_node, from_node) in self.edge_equipment_name:
                        transformer_name = self.edge_equipment_name[
                            (end_node, from_node)
                        ]
                    # If we cannot find the object, raise an error because it sould not be the case...
                    else:
                        raise ValueError(
                            "Unable to find equipment between {_from} and {_to}".format(
                                _from=from_node, _to=end_node
                            )
                        )

                    if transformer_name in transformer_load_mapping:
                        transformer_load_mapping[transformer_name].append(
                            load_list[idx].name
                        )
                    else:
                        transformer_load_mapping[transformer_name] = [
                            load_list[idx].name
                        ]

                # Go upstream...
                end_node = from_node

        return transformer_load_mapping

    def average_path_length(self, *args):
        """Returns the average path length of the network."""
        if args:
            try:
                return nx.average_shortest_path_length(args[0])
            except ZeroDivisionError:
                return 0
        else:
            return nx.average_shortest_path_length(self.G.graph)

    def compute_node_line_mapping(self):
        """
        Compute the following mapping:
        (from_element.name,to_element.name): Line.name
        """
        self.node_line_mapping = {}
        for obj in self.model.models:
            if isinstance(obj, Line):
                if (
                    hasattr(obj, "from_element")
                    and obj.from_element is not None
                    and hasattr(obj, "to_element")
                    and obj.to_element is not None
                ):
                    self.node_line_mapping[
                        (obj.from_element, obj.to_element)
                    ] = obj.name

    def get_impedance_list_between_nodes(self, net, node1, node2):
        """TODO"""
        impedance_list = []
        line_list = self.list_lines_betweeen_nodes(net, node1, node2)
        for line in line_list:
            line_object = self.model[line]
            if (
                hasattr(line_object, "impedance_matrix")
                and line_object.impedance_matrix is not None
                and line_object.impedance_matrix != []
            ):
                Z = np.array(line_object.impedance_matrix)
                if Z.shape == (1, 1):
                    impedance_list.append(Z[0, 0])
                # elif Z.shape==(3,3):
                else:
                    Z2 = self.abs_reader.get_sequence_impedance_matrix(Z)
                    Z_plus = self.abs_reader.get_positive_sequence_impedance(Z2)
                    impedance_list.append(Z_plus)
        return impedance_list

    def list_lines_betweeen_nodes(self, net, node1, node2):
        """
        The function takes a network and two nodes as inputs.
        It returns a list of Line names forming the shortest path between the two nodes.
        """
        # Compute the shortest path as a sequence of node names
        path = nx.shortest_path(net, node1, node2)
        # Transform it in a sequence of edges (n0,n1),(n1,n2),(n2,n3)...
        edge_list = [(a, b) for a, b in zip(path[:-1], path[1:])]
        # Compute the sequence of corresponding lines
        line_list = []
        for edge in edge_list:
            if edge in self.node_line_mapping:
                line_list.append(self.node_line_mapping[edge])
            # If the edge might is reversed
            elif edge[::-1] in self.node_line_mapping:
                line_list.append(self.node_line_mapping[edge[::-1]])
        return line_list

    def average_regulator_sub_distance(self, *args):
        """
        Returns the average distance between the substation and the regulators (if any).
        """
        if args:
            if len(args) == 1:
                _net = args[0]
                _src = self.source
            elif len(args) == 2:
                _net, _src = args
        else:
            _net = self.G.graph
            _src = self.source
        _net = _net.copy()
        if not _net.has_node(_src):
            _sp = nx.shortest_path(self.G.graph, _src, list(_net.nodes())[0])
            for n1, n2 in zip(_sp[:-1], _sp[1:]):
                _net.add_edge(n1, n2, length=self.G.graph[n1][n2]["length"])
        L = []
        for obj in self.model.models:
            if isinstance(obj, Regulator):
                if _net.has_node(obj.from_element):
                    L.append(
                        nx.shortest_path_length(
                            _net, _src, obj.from_element, weight="length"
                        )
                    )
        if len(L) > 0:
            return np.mean(L)
        else:
            return np.nan

    def average_capacitor_sub_distance(self, *args):
        """
        Returns the average distance between the substation and the capacitors (if any).
        """
        if args:
            if len(args) == 1:
                _net = args[0]
                _src = self.source
            elif len(args) == 2:
                _net, _src = args
        else:
            _net = self.G.graph
            _src = self.source
        _net = _net.copy()
        if not _net.has_node(_src):
            _sp = nx.shortest_path(self.G.graph, _src, list(_net.nodes())[0])
            for n1, n2 in zip(_sp[:-1], _sp[1:]):
                _net.add_edge(n1, n2, length=self.G.graph[n1][n2]["length"])
        L = []
        for obj in self.model.models:
            if isinstance(obj, Capacitor):
                if _net.has_node(obj.connecting_element):
                    L.append(
                        nx.shortest_path_length(
                            _net, _src, obj.connecting_element, weight="length"
                        )
                    )
        if len(L) > 0:
            return np.mean(L)
        else:
            return np.nan

    def average_recloser_sub_distance(self, *args):
        """
        Returns the average distance between the substation and the reclosers (if any).
        """
        if args:
            if len(args) == 1:
                _net = args[0]
                _src = self.source
            elif len(args) == 2:
                _net, _src = args
        else:
            _net = self.G.graph
            _src = self.source
        _net = _net.copy()
        if not _net.has_node(_src):
            _sp = nx.shortest_path(self.G.graph, _src, list(_net.nodes())[0])
            for n1, n2 in zip(_sp[:-1], _sp[1:]):
                _net.add_edge(n1, n2, length=self.G.graph[n1][n2]["length"])
        L = []
        for obj in self.model.models:
            if isinstance(obj, Line) and obj.is_recloser == 1:
                if hasattr(obj, "from_element") and obj.from_element is not None:
                    if _net.has_node(obj.from_element):
                        L.append(
                            nx.shortest_path_length(
                                _net, _src, obj.from_element, weight="length"
                            )
                        )
        if len(L) > 0:
            return np.mean(L)
        else:
            return np.nan

    def furtherest_node_miles(self, *args):
        """
        Returns the maximum eccentricity from the source, in miles.

        .. warning:: Not working....
        """
        if args:
            if len(args) == 1:
                _net = args[0]
                _src = self.source
            elif len(args) == 2:
                _net, _src = args
        else:
            _net = self.G.graph
            _src = self.source
        dist = {}
        _net = _net.copy()
        if not _net.has_node(_src):
            _sp = nx.shortest_path(self.G.graph, _src, list(_net.nodes())[0])
            for n1, n2 in zip(_sp[:-1], _sp[1:]):
                _net.add_edge(n1, n2, length=self.G.graph[n1][n2]["length"])
        for node in _net.nodes():
            dist[node] = nx.shortest_path_length(_net, _src, node, weight="length")
        return np.max(list(dist.values())) * 0.000621371  # Convert length to miles

    def furtherest_node_miles_clever(self):
        """
        Returns the maximum eccentricity from the source, in miles.

        Relies on the assumption that the furthrest node is a leaf, which is often True in distribution systems.

        .. warning:: Not working....
        """
        dist = {}
        for node in self.G.graph.nodes():
            if nx.degree(self.G.graph, node) == 1:
                dist[node] = nx.shortest_path_length(
                    self.G.graph, self.source, node, weight="length"
                )
        return np.max(list(dist.values())) * 0.000621371  # Convert length to miles

    def lv_length_miles(self):
        """Returns the sum of the low voltage line lengths in miles."""
        total_length = 0
        for obj in self.model.models:
            if isinstance(obj, Line):
                if obj.nominal_voltage <= self.LV_threshold:
                    if hasattr(obj, "length") and obj.length >= 0:
                        total_length += obj.length
        return total_length * 0.000621371  # Convert length to miles

    def mv_length_miles(self):
        """Returns the sum of the medium voltage line lengths in miles."""
        total_length = 0
        for obj in self.model.models:
            if isinstance(obj, Line):
                if self.MV_threshold >= obj.nominal_voltage > self.LV_threshold:
                    if hasattr(obj, "length") and obj.length >= 0:
                        total_length += obj.length
        return total_length * 0.000621371  # Convert length to miles

    def length_mvXph_miles(self, X):
        """Returns the sum of the medium voltage, X phase, line lengths in miles."""
        if not isinstance(X, int):
            raise ValueError("Number of phases should be an integer.")
        if not 1 <= X <= 3:
            raise ValueError("Number of phases should be 1, 2, or 3.")
        total_length = 0
        for obj in self.model.models:
            if isinstance(obj, Line):
                if self.MV_threshold >= obj.nominal_voltage > self.LV_threshold:
                    if hasattr(obj, "wires") and obj.wires is not None:
                        phases = [
                            wire.phase
                            for wire in obj.wires
                            if wire.phase in ["A", "B", "C"]
                        ]
                        if (
                            len(phases) == X
                            and hasattr(obj, "length")
                            and obj.length >= 0
                        ):
                            total_length += obj.length
        return total_length * 0.000621371  # Convert length to miles

    def length_lvXph_miles(self, X):
        """Returns the sum of the low voltage, X phase, line lengths in miles."""
        if not isinstance(X, int):
            raise ValueError("Number of phases should be an integer.")
        if not 1 <= X <= 3:
            raise ValueError("Number of phases should be 1, 2, or 3.")
        total_length = 0
        for obj in self.model.models:
            if isinstance(obj, Line):
                if obj.nominal_voltage <= self.LV_threshold:
                    if hasattr(obj, "wires") and obj.wires is not None:
                        phases = [
                            wire.phase
                            for wire in obj.wires
                            if wire.phase in ["A", "B", "C"]
                        ]
                        if (
                            len(phases) == X
                            and hasattr(obj, "length")
                            and obj.length >= 0
                        ):
                            total_length += obj.length
        return total_length * 0.000621371  # Convert length to miles

    def total_demand(self):
        """Returns the sum of all loads active power in kW."""
        tot_demand = 0
        for obj in self.model.models:
            if isinstance(obj, Load):
                if hasattr(obj, "phase_loads") and obj.phase_loads is not None:
                    tot_demand += np.sum(
                        [pl.p for pl in obj.phase_loads if pl.p is not None]
                    )
        return tot_demand * 10 ** -3  # in kW

    def total_reactive_power(self):
        """Returns the sum of all loads reactive power in kVar."""
        tot_kVar = 0
        for obj in self.model.models:
            if isinstance(obj, Load):
                if hasattr(obj, "phase_loads") and obj.phase_loads is not None:
                    tot_kVar += np.sum(
                        [pl.q for pl in obj.phase_loads if pl.q is not None]
                    )
        return tot_kVar * 10 ** -3  # in kW

    def number_of_loads_LV_Xph(self, X):
        """Returns the number of low voltage, X phase, loads."""
        if not isinstance(X, int):
            raise ValueError("Number of phases should be an integer.")
        if X not in [1, 3]:
            raise ValueError("Number of phases should be 1, or 3.")
        nb = 0
        for obj in self.model.models:
            if isinstance(obj, Load):
                if hasattr(obj, "nominal_voltage") and obj.nominal_voltage is not None:
                    if obj.nominal_voltage <= self.LV_threshold:
                        if hasattr(obj, "phase_loads") and obj.phase_loads is not None:
                            if len(obj.phase_loads) == X:
                                nb += 1
        return nb

    def number_of_loads_MV_3ph(self):
        """Returns the number of medium voltage, 3 phase, loads."""
        nb = 0
        for obj in self.model.models:
            if isinstance(obj, Load):
                if hasattr(obj, "nominal_voltage") and obj.nominal_voltage is not None:
                    if self.MV_threshold >= obj.nominal_voltage > self.LV_threshold:
                        if hasattr(obj, "phase_loads") and obj.phase_loads is not None:
                            if len(obj.phase_loads) == 3:
                                nb += 1
        return nb

    def percentage_load_LV_kW_phX(self, X):
        """
        Returns the percentage of low voltage phase X in kW:

        res=(sum of active power for all phase_loads X)/(total_demand)*100
        """
        if not isinstance(X, string_types):
            raise ValueError("Phase should be a string.")
        if X not in ["A", "B", "C"]:
            raise ValueError("Phase should be A, B, or C.")

        demand_phase_X = 0
        tot_demand = 0

        for obj in self.model.models:
            if isinstance(obj, Load):
                if hasattr(obj, "nominal_voltage") and obj.nominal_voltage is not None:
                    if obj.nominal_voltage <= self.LV_threshold:
                        if hasattr(obj, "phase_loads") and obj.phase_loads is not None:
                            for phase_load in obj.phase_loads:
                                if hasattr(
                                    phase_load, "phase"
                                ) and phase_load.phase in ["A", "B", "C"]:
                                    if (
                                        hasattr(phase_load, "p")
                                        and phase_load.p is not None
                                    ):
                                        if phase_load.phase == X:
                                            demand_phase_X += phase_load.p
                                            tot_demand += phase_load.p
                                        else:
                                            tot_demand += phase_load.p
        return float(demand_phase_X) / float(tot_demand) * 100
