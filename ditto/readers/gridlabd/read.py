from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from datetime import datetime
from datetime import timedelta
from croniter import croniter
import logging
import math
import sys
import os
import json

import networkx as nx

import numpy as np

try:
    from lxml import etree
except ImportError:
    from xml import etree

from ditto.compat import ModuleType
from ditto.store import Store
from ditto.models.node import Node
from ditto.models.power_source import PowerSource
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.phase_load import PhaseLoad
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding
from ditto.models.phase_winding import PhaseWinding

from ditto.formats.gridlabd import gridlabd
from ditto.formats.gridlabd import base
from ditto.models.base import Unicode

from ..abstract_reader import AbstractReader

logger = logging.getLogger(__name__)


class Reader(AbstractReader):
    """
    The schema is read in gridlabd.py which is imported as a module here.
    The class objects are stored in the global space of the gridlabd module
    """
    register_names = ["glm", "gridlabd"]

    all_gld_objects = {}
    all_api_objects = {}

    def __init__(self, **kwargs):
        """Gridlabd class CONSTRUCTOR."""

        self.input_file = kwargs.get("input_file", "./input.glm")
        super(Reader, self).__init__(**kwargs)

    def compute_spacing(self, spacing, conductors, default_height=30):
        lookup = ["A", "B", "C", "N", "E"]
        rev_lookup = {"A": 0, "B": 1, "C": 2, "N": 3, "E": 4}
        num_dists = len(lookup)
        distances = [[-1 for i in range(num_dists)] for j in range(num_dists)]
        max_dist = -100
        max_from = -1
        max_to = -1
        for i in range(num_dists):
            for j in range(i + 1, num_dists):
                name = "distance_%s%s" % (lookup[i], lookup[j])
                try:
                    dist = float(spacing[name])
                    distances[i][j] = dist
                    distances[j][i] = dist
                    distances[i][i] = 0
                    distances[j][j] = 0
                    if dist > max_dist and i < (num_dists - 1) and j < (num_dists - 1):
                        max_dist = dist
                        max_from = i
                        max_to = j
                except AttributeError:
                    pass
        n_entries = num_dists ** 2
        for i in range(num_dists):
            for j in range(num_dists):
                if distances[i][j] == -1:
                    n_entries = n_entries - 1
        n_entries = int(math.sqrt(n_entries))
        has_earth = max(distances[:][-1]) > -1
        # import pdb; pdb.set_trace()

        if has_earth:
            n_entries = n_entries - 1

        if n_entries <= 0:
            logger.debug("Warning: No elements included in spacing")

        if n_entries == 1:
            for w in conductors:
                w.X = 0
                if has_earth:
                    index = rev_lookup[w.phase]
                    w.Y = distances[index][-1] / 3.28084
                else:
                    w.Y = default_height / 3.28084

        if (
            n_entries == 2
        ):  # If only two wires and no ground distances given assume they are vertically in line
            tmp_map = {}
            if max_dist == 0:
                cnt = 0
                logger.warning("Spacing distance is 0 - using default positions")
                for w in conductors:
                    w.X = 0
                    w.Y = default_height + 2 * cnt
                    cnt += 1

            else:
                for w in conductors:
                    index = rev_lookup[w.phase]
                    if index == max_from:
                        tmp_map[w.phase] = (0, 0)
                    if index == max_to:
                        tmp_map[w.phase] = (0, 0 - max_dist)

                for w in conductors:
                    non_rotated = np.array(tmp_map[w.phase])
                    if has_earth:
                        # Rotate then translate
                        h = distances[max_from][-1] - distances[max_to][-1]
                        theta = math.acos(h / float(max_dist))
                        rotation = np.array(
                            [
                                [math.cos(theta), -1 * math.sin(theta)],
                                [math.sin(theta), math.cos(theta)],
                            ]
                        )
                        final = rotation.dot(non_rotated)
                        final[1] = final[1] + distances[max_from][-1]
                    else:
                        final = non_rotated
                        final[1] = final[1] + default_height
                    w.X = final[0] / 3.28084
                    w.Y = final[1] / 3.28084

        if (
            n_entries == 3
        ):  # If there are three wires and no ground distances assume the furthest appart are on a horizontal axis.
            tmp_map = {}
            try:
                for w in conductors:
                    index = rev_lookup[w.phase]
                    if index == max_from:
                        tmp_map[w.phase] = [(0, 0)]
                    elif index == max_to:
                        tmp_map[w.phase] = [(0, 0 - max_dist)]

                    else:
                        dist_a = distances[index][max_from]
                        dist_b = distances[index][max_to]
                        heron_p = (dist_a + dist_b + max_dist) / 2.0
                        try:
                            x = (
                                2
                                * math.sqrt(
                                    heron_p
                                    * (heron_p - dist_a)
                                    * (heron_p - dist_b)
                                    * (heron_p - max_dist)
                                )
                                / max_dist
                            )  # May be +-x as it could be on either side of the max_dist edge
                            y = -1 * math.sqrt(dist_a ** 2 - x ** 2)
                            tmp_map[w.phase] = [(x, y), (-1 * x, y)]
                        except:
                            raise ValueError(
                                "Line Geometry infeasible with distances %f %f %f"
                                % (dist_a, dist_b, max_dist)
                            )

                for w in conductors:
                    final = []
                    for non_rotated in tmp_map[w.phase]:
                        non_rotated = np.array(non_rotated)
                        if has_earth:
                            index = rev_lookup[w.phase]
                            # Rotate then translate
                            h = distances[max_from][-1] - distances[max_to][-1]
                            theta = math.acos(h / float(max_dist))
                            rotation = np.array(
                                [
                                    [math.cos(theta), -1 * math.sin(theta)],
                                    [math.sin(theta), math.cos(theta)],
                                ]
                            )
                            final = rotation.dot(non_rotated)
                            final[1] = final[1] + distances[max_from][-1]
                            if final[1] == distances[index][-1]:
                                break

                        else:
                            rotation = np.array(
                                [
                                    [math.cos(math.pi / 2), -1 * math.sin(math.pi / 2)],
                                    [math.sin(math.pi / 2), math.cos(math.pi / 2)],
                                ]
                            )
                            final = rotation.dot(non_rotated)
                            final[1] = final[1] + default_height
                            break
                    w.X = final[0] / 3.28084
                    w.Y = final[1] / 3.28084
            except:
                cnt = 0
                logger.warning("Failed to read spacing - using default positions")
                for w in conductors:
                    if w.phase.lower() == "n":
                        w.X = 0
                        w.Y = default_height + 2
                    else:
                        w.X = cnt * 2
                        w.Y = default_height
                        cnt += 1

        if (
            n_entries == 4
        ):  # If there are three wires and no ground distances assume the furthest appart are on a horizontal axis.
            tmp_map = {}
            seen_one = False
            first_x = -10
            first_y = -10
            first_index = -10
            try:
                for w in conductors:
                    index = rev_lookup[w.phase]
                    if index == max_from:
                        tmp_map[w.phase] = [(0, 0)]
                    elif index == max_to:
                        tmp_map[w.phase] = [(0, 0 - max_dist)]

                    else:
                        dist_a = distances[index][max_from]
                        dist_b = distances[index][max_to]
                        heron_p = (dist_a + dist_b + max_dist) / 2.0
                        x = (
                            2
                            * math.sqrt(
                                heron_p
                                * (heron_p - dist_a)
                                * (heron_p - dist_b)
                                * (heron_p - max_dist)
                            )
                            / max_dist
                        )  # May be +-x as it could be on either side of the max_dist edge
                        y = -1 * math.sqrt(dist_a ** 2 - x ** 2)
                        if seen_one:
                            # Warning : possible bug in here - needs more testing
                            if (x - first_x) ** 2 + (y - first_y) ** 2 != distances[
                                index
                            ][first_index] ** 2:
                                x = x * -1
                        else:
                            seen_one = True
                            first_x = x
                            first_y = y
                            first_index = index
                        tmp_map[w.phase] = [(x, y)]

                for w in conductors:
                    final = []
                    for non_rotated in tmp_map[w.phase]:
                        non_rotated = np.array(non_rotated)
                        if has_earth:
                            index = rev_lookup[w.phase]
                            # Rotate then translate
                            h = distances[max_from][-1] - distances[max_to][-1]
                            theta = math.acos(h / float(max_dist))
                            rotation = np.array(
                                [
                                    [math.cos(theta), -1 * math.sin(theta)],
                                    [math.sin(theta), math.cos(theta)],
                                ]
                            )
                            final = rotation.dot(non_rotated)
                            final[1] = final[1] + distances[max_from][-1]
                            if final[1] == distances[index][-1]:
                                break

                        else:
                            rotation = np.array(
                                [
                                    [math.cos(math.pi / 2), -1 * math.sin(math.pi / 2)],
                                    [math.sin(math.pi / 2), math.cos(math.pi / 2)],
                                ]
                            )
                            final = rotation.dot(non_rotated)
                            final[1] = final[1] + default_height
                            break
                    w.X = final[0] / 3.28084
                    w.Y = final[1] / 3.28084
            except:
                cnt = 0
                logger.warning("Failed to read spacing - using default positions")
                for w in conductors:
                    if w.phase.lower() == "n":
                        w.X = 0
                        w.Y = default_height + 2
                    else:
                        w.X = cnt * 2
                        w.Y = default_height
                        cnt += 1

    def compute_secondary_matrix(
        self, wire_list, freq=60, resistivity=100, kron_reduce=True
    ):
        # wire_map = {'1':0,'2':1,'N':2} TODO: Use this for phases
        wire_map = {"A": 0, "B": 1, "N": 2}
        matrix = [[0 for i in range(3)] for j in range(3)]
        d12 = 0
        d1n = 0
        distances_mapped = False
        for w in wire_list:
            if w.diameter is not None and w.insulation_thickness is not None:
                d12 = (w.diameter + 2 * w.insulation_thickness) / 12.0
                d1n = (w.diameter + w.insulation_thickness) / 12.0
                distances_mapped = True
                break

        for i in range(len(wire_list)):
            for j in range(len(wire_list)):
                if i == j:
                    z = 0
                    if (
                        wire_list[i].resistance is not None
                        and wire_list[i].gmr is not None
                    ):
                        z = complex(
                            wire_list[i].resistance + 0.00158836 * freq,
                            0.00202237
                            * freq
                            * (
                                math.log(1 / wire_list[i].gmr)
                                + 7.6786
                                + 0.5 * math.log(resistivity / freq)
                            ),
                        )
                    else:
                        logger.debug("Warning: resistance or GMR is missing from wire")

                    if wire_list[i].phase is not None:
                        index = wire_map[wire_list[i].phase]
                        matrix[index][index] = z / 1609.34
                    else:
                        logger.debug("Warning: phase missing from wire")

                else:
                    z = 0
                    if (
                        wire_list[i].phase is not None
                        and wire_list[j].phase is not None
                        and distances_mapped
                    ):
                        if wire_list[i].phase == "N" or wire_list[j].phase == "N":
                            z = complex(
                                0.00158836 * freq,
                                0.00202237
                                * freq
                                * (
                                    math.log(1 / d1n)
                                    + 7.6786
                                    + 0.5 * math.log(resistivity / freq)
                                ),
                            )
                        else:
                            z = complex(
                                0.00158836 * freq,
                                0.00202237
                                * freq
                                * (
                                    math.log(1 / d12)
                                    + 7.6786
                                    + 0.5 * math.log(resistivity / freq)
                                ),
                            )
                        index1 = wire_map[wire_list[i].phase]
                        index2 = wire_map[wire_list[j].phase]
                        matrix[index1][index2] = z / 1609.34  # ohms per meter

                    else:
                        # import pdb; pdb.set_trace()
                        logger.debug(
                            "Warning phase missing from wire, or Insulation_thickness/diameter not set"
                        )

        if kron_reduce:
            kron_matrix = [[0 for i in range(2)] for j in range(2)]
            for i in range(2):
                for j in range(2):
                    kron_matrix[i][j] = (
                        matrix[i][j] - matrix[i][2] * 1 / matrix[2][2] * matrix[2][j]
                    )

            matrix = kron_matrix
        return matrix

    def compute_matrix(self, wire_list, freq=60, resistivity=100, kron_reduce=True):
        wire_map = {"A": 0, "B": 1, "C": 2, "N": 3}
        matrix = [[0 for i in range(4)] for j in range(4)]
        has_neutral = False
        for i in range(len(wire_list)):
            if wire_list[i].phase == "N":
                has_neutral = True
            for j in range(len(wire_list)):
                if i == j:
                    z = 0
                    if (
                        wire_list[i].resistance is not None
                        and wire_list[i].gmr is not None
                    ):
                        z = complex(
                            wire_list[i].resistance + 0.00158836 * freq,
                            0.00202237
                            * freq
                            * (
                                math.log(1 / wire_list[i].gmr)
                                + 7.6786
                                + 0.5 * math.log(resistivity / freq)
                            ),
                        )
                    else:
                        logger.debug("Warning: resistance or GMR is missing from wire")

                    if wire_list[i].phase is not None:
                        index = wire_map[wire_list[i].phase]
                        matrix[index][index] = z
                    else:
                        logger.debug("Warning: phase missing from wire")

                else:
                    z = 0
                    if (
                        wire_list[i].X is not None
                        and wire_list[i].Y is not None
                        and wire_list[j].X is not None
                        and wire_list[j].Y is not None
                    ):
                        x1 = wire_list[i].X
                        x2 = wire_list[j].X
                        y1 = wire_list[i].Y
                        y2 = wire_list[j].Y
                        distance = math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
                        z = complex(
                            0.00158836 * freq,
                            0.00202237
                            * freq
                            * (
                                math.log(1 / distance)
                                + 7.6786
                                + 0.5 * math.log(resistivity / freq)
                            ),
                        )
                    else:
                        logger.debug("Warning X or Y values missing from wire")
                        # import pdb; pdb.set_trace()
                    if (
                        wire_list[i].phase is not None
                        and wire_list[j].phase is not None
                    ):
                        index1 = wire_map[wire_list[i].phase]
                        index2 = wire_map[wire_list[j].phase]
                        matrix[index1][index2] = z  # ohms per meter
                    else:
                        logger.debug("Warning: phase missing from wire")

        if kron_reduce and has_neutral:
            kron_matrix = [[0 for i in range(3)] for j in range(3)]
            for i in range(3):
                for j in range(3):
                    kron_matrix[i][j] = (
                        matrix[i][j] - matrix[i][3] * 1 / matrix[3][3] * matrix[3][j]
                    )

            matrix = kron_matrix
        elif has_neutral == False:
            matrix_reduced = [[0 for i in range(3)] for j in range(3)]
            for i in range(3):
                for j in range(3):
                    matrix_reduced[i][j] = matrix[i][j]
            matrix = matrix_reduced
        return matrix

    def parse(self, model, origin_datetime="2017 Jun 1 2:00PM"):
        origin_datetime = datetime.strptime(origin_datetime, "%Y %b %d %I:%M%p")
        delta_datetime = timedelta(minutes=1)
        sub_datetime = origin_datetime - delta_datetime

        inputfile = open(self.input_file, "r")
        all_rows = inputfile.readlines()
        curr_object = None
        curr_schedule = None
        ignore_elements = False
        found_schedule = False
        all_includes = []
        all_schedules = {}
        for row in all_rows:
            if row[:8] == "#include":
                entries = row.split()
                location = entries[1].strip('"')
                include_file = open(location, "r")
                include_rows = include_file.readlines()
                all_includes = all_includes + include_rows
        all_rows = all_rows + all_includes
        for row in all_rows:
            row = row.strip()

            if row[:2] == "//":
                continue
            entries = row.split()
            if len(entries) > 0 and entries[0] == "object":
                if curr_object is None:
                    obj = entries[1].split(":")
                    obj_class = obj[0]
                    if (
                        obj_class == "house"
                        or obj_class == "solar"
                        or obj_class == "inverter"
                        or obj_class == "waterheater"
                        or obj_class == "climate"
                        or obj_class == "ZIPload"
                        or obj_class == "tape.recorder"
                        or obj_class == "player"
                        or obj_class == "tape.collector"
                        or obj_class == "tape.group_recorder"
                        or obj_class == "recorder"
                    ):
                        continue
                    curr_object = getattr(gridlabd, obj_class)()
                    if len(obj) > 1:
                        curr_object["name"] = obj_class + ":" + obj[1]
                else:
                    ignore_elements = True

            elif len(entries) > 0 and entries[0] == "schedule":
                if curr_schedule is None:
                    schedule = entries[1]
                    schedule_bracket_cnt = 1
                curr_schedule = schedule

            else:
                if curr_object == None and curr_schedule == None:
                    continue
                if curr_object != None:
                    entries = row.split()
                    if len(entries) > 1:
                        element = entries[0]
                        value = entries[1]
                        if value[-1] == ";":
                            value = value[:-1]
                        if len(entries) > 2:
                            units = entries[2]
                            # TODO: Deal with units correctly
                            # print element,value,units
                            # if units[0] =='k':
                            #    value = value/1000.0
                        # Assuming no nested objects for now.
                        curr_object[element] = value

                    if len(row) >= 1:
                        if row[-1] == "}" or row[-2:] == "};":
                            if ignore_elements:  # Assumes only one layer of nesting
                                ignore_elements = False
                            else:
                                try:
                                    self.all_gld_objects[
                                        curr_object["name"]
                                    ] = curr_object
                                    curr_object = None
                                except:

                                    if (
                                        curr_object["from"] != None
                                        and curr_object["to"] != None
                                    ):
                                        curr_object["name"] = (
                                            curr_object["from"]
                                            + "-"
                                            + curr_object["to"]
                                        )
                                        self.all_gld_objects[
                                            curr_object["name"]
                                        ] = curr_object

                                    else:
                                        logger.debug("Warning object missing a name")
                                    curr_object = None
                if curr_schedule != None:
                    row = row.strip(";")
                    entries = row.split()
                    if len(entries) > 5 and not found_schedule:
                        cron = " ".join(entries[:-1])
                        value = entries[-1]
                        iter = croniter(cron, sub_datetime)
                        if iter.get_next(datetime) == origin_datetime:
                            found_schedule = True
                            all_schedules[curr_schedule] = value

                    if len(row) >= 1:
                        if row[-1] == "}":
                            schedule_bracket_cnt = schedule_bracket_cnt - 1
                        if row[0] == "{":
                            schedule_bracket_cnt = schedule_bracket_cnt + 1
                        if schedule_bracket_cnt == 0:
                            curr_schedule = None
                            found_schedule = False

        logger.debug(all_schedules)
        for obj_name, obj in self.all_gld_objects.items():
            obj_type = type(obj).__name__

            if obj_type == "node" or obj_type == "meter":
                # Using "easier to ask for forgiveness than permission" (EAFP) rather than "look before you leap" (LBYL) which would use if has_attr(obj,'_name').

                api_node = None
                try:
                    bustype = obj["bustype"]
                    if bustype == "SWING":
                        api_node = PowerSource(model)
                    else:
                        api_node = Node(model)
                except AttributeError:
                    api_node = Node(model)
                try:
                    api_node.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_node.nominal_voltage = float(obj["nominal_voltage"])
                except AttributeError:
                    pass

                try:
                    phases = []
                    for i in obj["phases"][
                        0:-1
                    ]:  # Ignore the 'N' at the end and just say if A,B or C
                        # With lists of traitlets, the strings aren't automatically cast
                        phases.append(Unicode(i))
                    api_node.phases = phases
                except AttributeError:
                    pass

            if obj_type == "triplex_node" or obj_type == "triplex_meter":
                api_node = Node(model)
                try:
                    api_node.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_node.nominal_voltage = float(obj["nominal_voltage"])
                except AttributeError:
                    pass

                try:
                    phases = []
                    cnt = 0
                    for i in obj["phases"][
                        1:-1
                    ]:  # Ignore the 'S' at the end and just say if A,B or C
                        # With lists of traitlets, the strings aren't automatically cast
                        cnt = cnt + 1
                        phases.append(Unicode(str(cnt)))
                    api_node.phases = phases
                except AttributeError:
                    pass

            if obj_type == "transformer":

                api_transformer = PowerTransformer(model)
                try:
                    api_transformer.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_transformer.from_element = obj["from"]
                except AttributeError:
                    pass

                try:
                    api_transformer.to_element = obj["to"]
                except AttributeError:
                    pass

                winding1 = Winding(model)
                winding2 = Winding(model)
                winding3 = Winding(model)
                num_windings = 2
                winding1.voltage_type = 0
                winding2.voltage_type = 2
                winding3.voltage_type = 2

                try:
                    phases = obj["phases"].strip('"')
                    winding1.phase_windings = []
                    winding2.phase_windings = []
                    winding3.phase_windings = []
                    for p in phases:
                        if p == "N" or p == "S":
                            continue
                        pw1 = PhaseWinding(model)
                        pw1.phase = p
                        winding1.phase_windings.append(pw1)
                        pw2 = PhaseWinding(model)
                        pw2.phase = p
                        winding2.phase_windings.append(pw2)

                except AttributeError:
                    pass

                try:
                    # Even though the transformer may be ABCN, (ie there's a neutral on the wire) we assume a delta primary doesn't connect the the neutral wire.
                    config_name1 = obj["configuration"]
                    for config_name, config in self.all_gld_objects.items():
                        if config_name == config_name1:
                            try:
                                conn = config["connect_type"]
                                # Assume a grounded Wye - Wye connection has a neutral on both sides
                                if conn == 1 or conn == "WYE_WYE":
                                    winding1.connection_type = "Y"
                                    winding2.connection_type = "Y"

                                # Assume that the secondary on a delta-delta has a grounding neutral, but the high side doesn't
                                if conn == 2 or conn == "DELTA_DELTA":
                                    winding1.connection_type = "D"
                                    winding2.connection_type = "D"

                                # Assume that the secondary on a delta-wye has a grounding neutral, but the high side doesn't
                                if conn == 3 or conn == "DELTA_GWYE":
                                    winding1.connection_type = "D"
                                    winding2.connection_type = "Y"

                                # For a single phase transformer, no connection type is specified. It steps from a single phase and neutral to a single phase and neutral
                                if conn == 4 or conn == "SINGLE_PHASE":
                                    pass  # The phase is already covered by the "phases" attribute

                                # For a single phase center tapped transformer no connection type is specified. Its steps from a single phase and neutral to a neutral and two low voltage lines
                                if conn == 5 or conn == "SINGLE_PHASE_CENTER_TAPPED":
                                    num_windings = 3
                                    winding2.phase_windings[
                                        0
                                    ].phase = (
                                        "A"
                                    )  # Assume that only one phase from A/B/C was assigned to the winding. TODO replace with 2 to represent secondaries.

                                    pw3 = PhaseWinding(model)
                                    pw3.phase = (
                                        "B"
                                    )  # TODO replace with 2 to represent secondaries.
                                    winding3.phase_windings.append(pw3)
                            except AttributeError:
                                pass

                            try:
                                install_type = config["install_type"]
                                api_transformer.install_type = install_type
                            except AttributeError:
                                pass

                            try:
                                noloadloss = config["no_load_loss"]
                                api_transformer.noload_loss = float(noloadloss)
                            except AttributeError:
                                pass

                            try:
                                high_voltage = config["primary_voltage"]
                                winding1.nominal_voltage = float(high_voltage)
                            except AttributeError:
                                pass

                            try:
                                low_voltage = config["secondary_voltage"]
                                winding2.nominal_voltage = float(low_voltage)
                                if num_windings == 3:
                                    winding3.nominal_voltage = float(low_voltage)
                            except AttributeError:
                                pass

                            try:
                                resistance = float(config["resistance"])
                                if num_windings == 2:
                                    winding1.resistance = resistance / 2.0
                                    winding2.resistance = resistance / 2.0
                                if num_windings == 3:
                                    winding1.resistance = resistance / 2.0
                                    winding2.resistance = (
                                        resistance
                                    )  # Using power flow approximation from "Electric Power Distribution Handbook" by Short page 188
                                    winding3.resistance = resistance

                            except AttributeError:
                                pass

                            failed_reactance = True

                            reactances = []
                            try:
                                reactance = float(config["reactance"])
                                failed_reactance = False
                                reactance1 = reactance
                                reactances.append(
                                    reactance1
                                )  # TODO: Change documentation to reflect that we aren't indicating the from-to relation in reactances.
                                # reactances.append((0,1,reactance1))
                                if (
                                    num_windings == 3
                                ):  # TODO: Change documentation to reflect that we aren't indicating the from-to relation in reactances.
                                    reactance2 = complex(config["impedance1"])
                                    reactances.append(reactance2.imag)
                                    reactance3 = complex(config["impedance2"])
                                    reactances.append(reactance3.imag)

                            except AttributeError:
                                if (
                                    not failed_reactance
                                ):  # Should only fail if there are three windings in the system
                                    reactance = float(config["reactance"])
                                    reactances[0] = 0.8 * reactance
                                    reactances.append(
                                        0.4 * reactance
                                    )  # Using power flow approximation from "Electric Power Distribution Handbook" by Short page 188 of transformer with no center tap
                                    reactances.append(0.4 * reactance)

                            if failed_reactance:
                                try:
                                    impedance = complex(config["impedance"])
                                    resistance = impedance.real
                                    reactance = impedance.imag
                                    if num_windings == 2:
                                        winding1.resistance
                                        winding1.resistance = resistance / 2.0
                                        winding2.resistance = resistance / 2.0
                                        reactances.append(reactance)

                                    if num_windings == 3:
                                        winding1.resistance = resistance / 2.0
                                        winding2.resistance = (
                                            resistance
                                        )  # Using power flow approximation from "Electric Power Distribution Handbook" by Short page 188
                                        winding3.resistance = resistance
                                        reactances.append(0.8 * reactance)
                                        reactances.append(
                                            0.4 * reactance
                                        )  # Using power flow approximation from "Electric Power Distribution Handbook" by Short page 188 of transformer with no center tap
                                        reactances.append(0.4 * reactance)
                                except AttributeError:
                                    pass

                            if len(reactances) > 0:
                                for x in reactances:
                                    api_transformer.reactances.append(x)

                            try:
                                power_rating = float(config["power_rating"]) * 1000
                                winding1.rated_power = power_rating
                                if num_windings == 3:
                                    winding2.rated_power = power_rating / 2.0
                                    winding3.rated_power = power_rating / 2.0
                                else:
                                    winding2.rated_power = power_rating
                            except AttributeError:
                                pass
                            try:
                                power_rating = float(config["powerA_rating"]) * 1000
                                winding1.rated_power = power_rating
                                if num_windings == 3:
                                    winding2.rated_power = power_rating / 2.0
                                    winding3.rated_power = power_rating / 2.0
                                else:
                                    winding2.rated_power = power_rating
                            except AttributeError:
                                pass

                            try:
                                power_rating = float(config["powerB_rating"]) * 1000
                                winding1.rated_power = power_rating
                                if num_windings == 3:
                                    winding2.rated_power = power_rating / 2.0
                                    winding3.rated_power = power_rating / 2.0
                                else:
                                    winding2.rated_power = power_rating
                            except AttributeError:
                                pass
                            try:
                                power_rating = float(config["powerC_rating"]) * 1000
                                winding1.rated_power = power_rating
                                if num_windings == 3:
                                    winding2.rated_power = power_rating / 2.0
                                    winding3.rated_power = power_rating / 2.0
                                else:
                                    winding2.rated_power = power_rating
                            except AttributeError:
                                pass

                except AttributeError:
                    pass

                windings = [winding1, winding2]
                if num_windings == 3:
                    windings.append(winding3)
                api_transformer.windings = windings

            if obj_type == "load":

                api_load = Load(model)
                api_node = None
                has_parent = None
                try:
                    api_load.connecting_element = obj["parent"]
                    has_parent = True
                except AttributeError:
                    has_parent = False
                    api_node = Node(model)
                try:
                    if has_parent:
                        api_load.name = obj["name"]
                    else:
                        api_load.name = "load_" + obj["name"]
                        api_load.connecting_element = obj["name"]
                        api_node.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_load.nominal_voltage = float(obj["nominal_voltage"])
                    if not has_parent:
                        api_node.nominal_voltage = float(obj["nominal_voltage"])

                except AttributeError:
                    pass

                phases = []
                phaseloads = []
                try:
                    for i in obj["phases"].strip('"'):
                        if i == "A" or i == "B" or i == "C":
                            phases.append(i)
                    if not has_parent:
                        api_node.phases = list(map(lambda x: Unicode(x), phases))
                except AttributeError:
                    pass
                num_phases = 0

                # The use_zip parameter is used to determine whether the load is zip or not.
                for phase in phases:
                    if phase == "A":
                        num_phases = num_phases + 1
                        phaseload = PhaseLoad(model)
                        phaseload.phase = phase
                        phaseload.p = 0  # Default value
                        phaseload.q = 0
                        try:
                            # Firstly check if it's using a non-zip model.
                            complex_power = complex(obj["constant_power_A"])
                            p = complex_power.real
                            q = complex_power.imag
                            if (
                                p != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that I or Z is being used instead.
                                phaseload.p = p
                                phaseload.q = q
                                phaseload.model = (
                                    1
                                )  # The opendss model number (specifying constant power)
                                phaseload.use_zip = 0
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            # Firstly check if it's using a non-zip model.
                            complex_impedance = complex(obj["constant_impedance_A"])
                            complex_voltage = complex(
                                obj["voltage_A"]
                            )  # Needed to compute the power
                            if (
                                complex_impedance.real != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that I or P is being used instead.
                                p = (
                                    (
                                        (
                                            complex_voltage.real ** 2
                                            + complex_voltage.imag ** 2
                                        )
                                    )
                                    / complex_impedance.conjugate()
                                ).real
                                q = (
                                    (
                                        (
                                            complex_voltage.real ** 2
                                            + complex_voltage.imag ** 2
                                        )
                                    )
                                    / complex_impedance.conjugate()
                                ).imag
                                phaseload.p = p
                                phaseload.q = q
                                phaseload.use_zip = 0
                                phaseload.model = (
                                    2
                                )  # The opendss model number (specifying constant impedance)
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            # Firstly check if it's using a non-zip model.
                            complex_current = complex(obj["constant_current_A"])
                            complex_voltage = complex(
                                obj["voltage_A"]
                            )  # Needed to compute the power
                            p = (complex_voltage * complex_current.conjugate()).real
                            q = (complex_voltage * complex_current.conjugate()).imag
                            if (
                                complex_current.real != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that Z or P is being used instead.

                                phaseload.p = p
                                phaseload.q = q
                                phaseload.use_zip = 0
                                phaseload.model = (
                                    5
                                )  # The opendss model number (specifying constant current)
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            base_power = float(obj["base_power_A"])
                            p = base_power
                            phaseload.p = p
                        except AttributeError:
                            pass

                        except ValueError:
                            data = obj["base_power_A"].split("*")

                            if data[0] in all_schedules:
                                phaseload.p = float(all_schedules[data[0]]) * float(
                                    data[1]
                                )
                            if data[1] in all_schedules:
                                phaseload.p = float(all_schedules[data[1]]) * float(
                                    data[0]
                                )

                        try:
                            # Require all six elements to compute the ZIP load model
                            current_fraction = float(obj["current_fraction_A"])
                            current_pf = float(obj["current_pf_A"])
                            power_fraction = float(obj["power_fraction_A"])
                            power_pf = float(obj["power_pf_A"])
                            impedance_fraction = float(obj["impedance_fraction_A"])
                            impedance_pf = float(obj["impedance_pf_A"])

                            phaseload.ppercentcurrent = current_fraction * current_pf
                            phaseload.qpercentcurrent = current_fraction * (
                                1 - current_pf
                            )
                            phaseload.ppercentpower = power_fraction * power_pf
                            phaseload.qpercentpower = power_fraction * (1 - power_pf)
                            phaseload.ppercentimpedance = (
                                impedance_fraction * impedance_pf
                            )
                            phaseload.qpercentimpedance = impedance_fraction * (
                                1 - impedance_pf
                            )
                            phaseload.use_zip = 1
                        except AttributeError:
                            pass

                        phaseloads.append(phaseload)

                    elif phase == "B":
                        num_phases = num_phases + 1
                        phaseload = PhaseLoad(model)
                        phaseload.phase = phase
                        phaseload.p = 0  # Default value
                        phaseload.q = 0
                        try:
                            complex_power = complex(obj["constant_power_B"])
                            p = complex_power.real
                            q = complex_power.imag
                            if (
                                p != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that I or Z is being used instead.
                                phaseload.p = p
                                phaseload.q = q
                                phaseload.model = (
                                    1
                                )  # The opendss model number (specifying constant power)
                                phaseload.use_zip = 0
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            # Firstly check if it's using a non-zip model.
                            complex_impedance = complex(obj["constant_impedance_B"])
                            complex_voltage = complex(
                                obj["voltage_B"]
                            )  # Needed to compute the power
                            if (
                                complex_impedance.real != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that I or P is being used instead.
                                p = (
                                    (
                                        (
                                            complex_voltage.real ** 2
                                            + complex_voltage.imag ** 2
                                        )
                                    )
                                    / complex_impedance.conjugate()
                                ).real
                                q = (
                                    (
                                        (
                                            complex_voltage.real ** 2
                                            + complex_voltage.imag ** 2
                                        )
                                    )
                                    / complex_impedance.conjugate()
                                ).imag
                                phaseload.p = p
                                phaseload.q = q
                                phaseload.model = (
                                    2
                                )  # The opendss model number (specifying constant impedance)
                                phaseload.use_zip = 0
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            # Firstly check if it's using a non-zip model.
                            complex_current = complex(obj["constant_current_B"])
                            complex_voltage = complex(
                                obj["voltage_B"]
                            )  # Needed to compute the power
                            p = (complex_voltage * complex_current.conjugate()).real
                            q = (complex_voltage * complex_current.conjugate()).imag
                            if (
                                complex_current.real != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that Z or P is being used instead.
                                phaseload.p = p
                                phaseload.q = q
                                phaseload.use_zip = 0
                                phaseload.model = (
                                    5
                                )  # The opendss model number (specifying constant current)
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            base_power = float(obj["base_power_B"])
                            p = base_power
                            phaseload.p = p
                        except AttributeError:
                            pass
                        except ValueError:
                            data = obj["base_power_B"].split("*")
                            if data[0] in all_schedules:
                                phaseload.p = float(all_schedules[data[0]]) * float(
                                    data[1]
                                )
                            if data[1] in all_schedules:
                                phaseload.p = float(all_schedules[data[1]]) * float(
                                    data[0]
                                )

                        try:
                            # Require all six elements to compute the ZIP load model
                            current_fraction = float(obj["current_fraction_B"])
                            current_pf = float(obj["current_pf_B"])
                            power_fraction = float(obj["power_fraction_B"])
                            power_pf = float(obj["power_pf_B"])
                            impedance_fraction = float(obj["impedance_fraction_B"])
                            impedance_pf = float(obj["impedance_pf_B"])

                            phaseload.ppercentcurrent = current_fraction * current_pf
                            phaseload.qpercentcurrent = current_fraction * (
                                1 - current_pf
                            )
                            phaseload.ppercentpower = power_fraction * power_pf
                            phaseload.qpercentpower = power_fraction * (1 - power_pf)
                            phaseload.ppercentimpedance = (
                                impedance_fraction * impedance_pf
                            )
                            phaseload.qpercentimpedance = impedance_fraction * (
                                1 - impedance_pf
                            )
                            phaseload.use_zip = 1
                        except AttributeError:
                            pass

                        phaseloads.append(phaseload)

                    elif phase == "C":
                        num_phases = num_phases + 1
                        phaseload = PhaseLoad(model)
                        phaseload.phase = phase
                        phaseload.p = 0  # Default value
                        phaseload.q = 0
                        try:
                            complex_power = complex(obj["constant_power_C"])
                            p = complex_power.real
                            q = complex_power.imag
                            if (
                                p != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that I or Z is being used instead.
                                phaseload.p = p
                                phaseload.q = q
                                phaseload.model = (
                                    1
                                )  # The opendss model number (specifying constant power)
                                phaseload.use_zip = 0
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            # Firstly check if it's using a non-zip model.
                            complex_impedance = complex(obj["constant_impedance_C"])
                            complex_voltage = complex(
                                obj["voltage_C"]
                            )  # Needed to compute the power
                            if (
                                complex_impedance.real != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that I or P is being used instead.
                                p = (
                                    (
                                        (
                                            complex_voltage.real ** 2
                                            + complex_voltage.imag ** 2
                                        )
                                    )
                                    / complex_impedance.conjugate()
                                ).real
                                q = (
                                    (
                                        (
                                            complex_voltage.real ** 2
                                            + complex_voltage.imag ** 2
                                        )
                                    )
                                    / complex_impedance.conjugate()
                                ).imag
                                phaseload.p = p
                                phaseload.q = q
                                phaseload.use_zip = 0
                                phaseload.model = (
                                    2
                                )  # The opendss model number (specifying constant impedance)
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            # Firstly check if it's using a non-zip model.
                            complex_current = complex(obj["constant_current_C"])
                            complex_voltage = complex(
                                obj["voltage_C"]
                            )  # Needed to compute the power
                            p = (complex_voltage * complex_current.conjugate()).real
                            q = (complex_voltage * complex_current.conjugate()).imag
                            if (
                                complex_current.real != 0
                            ):  # Assume that unless ZIP is specifically specified only one of constant_power, constant_current and constant_impedance is used. A real part of 0 means that Z or P is being used instead.
                                phaseload.p = p
                                phaseload.q = q
                                phaseload.use_zip = 0
                                phaseload.model = (
                                    5
                                )  # The opendss model number (specifying constant current)
                                phaseloads.append(phaseload)
                                continue
                        except AttributeError:
                            pass

                        try:
                            base_power = float(obj["base_power_C"])
                            p = base_power
                            phaseload.p = p
                        except AttributeError:
                            pass
                        except ValueError:
                            data = obj["base_power_C"].split("*")
                            if data[0] in all_schedules:
                                phaseload.p = float(all_schedules[data[0]]) * float(
                                    data[1]
                                )
                            if data[1] in all_schedules:
                                phaseload.p = float(all_schedules[data[1]]) * float(
                                    data[0]
                                )

                        try:
                            # Require all six elements to compute the ZIP load model
                            current_fraction = float(obj["current_fraction_C"])
                            current_pf = float(obj["current_pf_C"])
                            power_fraction = float(obj["power_fraction_C"])
                            power_pf = float(obj["power_pf_C"])
                            impedance_fraction = float(obj["impedance_fraction_C"])
                            impedance_pf = float(obj["impedance_pf_C"])

                            phaseload.ppercentcurrent = current_fraction * current_pf
                            phaseload.qpercentcurrent = current_fraction * (
                                1 - current_pf
                            )
                            phaseload.ppercentpower = power_fraction * power_pf
                            phaseload.qpercentpower = power_fraction * (1 - power_pf)
                            phaseload.ppercentimpedance = (
                                impedance_fraction * impedance_pf
                            )
                            phaseload.qpercentimpedance = impedance_fraction * (
                                1 - impedance_pf
                            )
                            phaseload.use_zip = 1
                        except AttributeError:
                            pass

                        phaseloads.append(phaseload)

                if num_phases > 0:
                    api_load.phase_loads = phaseloads

            if obj_type == "fuse":
                api_line = Line(model)
                api_line.is_fuse = True
                try:
                    api_line.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_line.from_element = obj["from"]
                except AttributeError:
                    pass

                try:
                    api_line.to_element = obj["to"]
                except AttributeError:
                    pass

                wires = []
                try:
                    status = obj["phase_A_status"]
                    api_wire = Wire(model)
                    api_wire.phase = "A"
                    if status == "BLOWN":
                        api_wire.is_open = True
                    else:
                        api_wire.is_open = False
                    wires.append(api_wire)
                except AttributeError:
                    pass
                try:
                    status = obj["phase_B_status"]
                    api_wire = Wire(model)
                    api_wire.phase = "B"
                    if status == "BLOWN":
                        api_wire.is_open = True
                    else:
                        api_wire.is_open = False
                    wires.append(api_wire)
                except AttributeError:
                    pass

                try:
                    status = obj["phase_C_status"]
                    api_wire = Wire(model)
                    api_wire.phase = "C"
                    if status == "BLOWN":
                        api_wire.is_open = True
                    else:
                        api_wire.is_open = False
                    wires.append(api_wire)
                except AttributeError:
                    pass

                try:
                    if len(wires) == 0:
                        for p in obj["phases"].strip('"'):
                            if p == "N":
                                continue
                            api_wire = Wire(model)
                            api_wire.phase = p
                            wires.append(api_wire)
                            if obj["status"] == "OPEN":
                                wires[-1].is_open = True
                            else:
                                wires[-1].is_open = False
                except AttributeError:
                    pass

                api_line.wires = wires

            if obj_type == "switch":
                api_line = Line(model)
                api_line.is_switch = True
                api_line.length = 1
                try:
                    api_line.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_line.from_element = obj["from"]
                except AttributeError:
                    pass

                try:
                    api_line.to_element = obj["to"]
                except AttributeError:
                    pass

                wires = []
                try:
                    status = obj["phase_A_state"]
                    api_wire = Wire(model)
                    api_wire.phase = "A"
                    if status == "OPEN":
                        api_wire.is_open = True
                    else:
                        api_wire.is_open = False
                    wires.append(api_wire)
                except AttributeError:
                    pass
                try:
                    status = obj["phase_B_state"]
                    api_wire = Wire(model)
                    api_wire.phase = "B"
                    if status == "OPEN":
                        api_wire.is_open = True
                    else:
                        api_wire.is_open = False
                    wires.append(api_wire)
                except AttributeError:
                    pass

                try:
                    status = obj["phase_C_state"]
                    api_wire = Wire(model)
                    api_wire.phase = "C"
                    if status == "OPEN":
                        api_wire.is_open = True
                    else:
                        api_wire.is_open = False
                    wires.append(api_wire)
                except AttributeError:
                    pass
                try:
                    if len(wires) == 0:
                        for p in obj["phases"].strip('"'):
                            if p == "N":
                                continue
                            api_wire = Wire(model)
                            api_wire.phase = p
                            wires.append(api_wire)
                            if obj["status"] == "OPEN":
                                wires[-1].is_open = True
                            else:
                                wires[-1].is_open = False
                except AttributeError:
                    pass

                api_line.wires = wires

            if obj_type == "overhead_line":

                api_line = Line(model)
                api_line.line_type = "overhead"
                try:
                    api_line.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_line.length = float(obj["length"]) * 0.3048
                except AttributeError:
                    pass

                try:
                    api_line.from_element = obj["from"]
                except AttributeError:
                    pass

                try:
                    api_line.to_element = obj["to"]
                except AttributeError:
                    pass

                try:
                    config_name = obj["configuration"]
                    config = self.all_gld_objects[config_name]
                    conductors = {}
                    num_phases = 0
                    try:
                        conna = config["conductor_A"]
                        api_wire = Wire(model)
                        api_wire.phase = "A"
                        conductors[api_wire] = conna
                    except AttributeError:
                        pass
                    try:
                        connb = config["conductor_B"]
                        api_wire = Wire(model)
                        api_wire.phase = "B"
                        conductors[api_wire] = connb
                    except AttributeError:
                        pass
                    try:
                        connc = config["conductor_C"]
                        api_wire = Wire(model)
                        api_wire.phase = "C"
                        conductors[api_wire] = connc
                    except AttributeError:
                        pass
                    try:
                        connn = config["conductor_N"]
                        api_wire = Wire(model)
                        api_wire.phase = "N"
                        conductors[api_wire] = connn
                    except AttributeError:
                        pass

                    # Pass by reference so the conductors are updated in dictionary when api_wire is changed
                    for api_wire in conductors:
                        cond_name = conductors[api_wire]
                        conductor = self.all_gld_objects[cond_name]
                        try:
                            api_wire.diameter = float(
                                conductor["diameter"]
                            )  # i.e. the same for all the wires.
                        except AttributeError:
                            pass
                        try:
                            api_wire.gmr = float(conductor["geometric_mean_radius"])
                        except AttributeError:
                            pass
                        try:
                            api_wire.resistance = float(conductor["resistance"])
                        except AttributeError:
                            pass
                        try:
                            api_wire.ampacity = float(
                                conductor["rating.summer.continuous"]
                            )
                        except AttributeError:
                            pass
                        try:
                            api_wire.emergency_ampacity = float(
                                conductor["rating.summer.emergency"]
                            )
                        except AttributeError:
                            pass

                    spacing_name = None
                    try:
                        spacing_name = config["spacing"]
                    except AttributeError:
                        pass
                    if spacing_name is not None:
                        spacing = self.all_gld_objects[spacing_name]
                        self.compute_spacing(spacing, conductors)
                except AttributeError:
                    pass

                impedance_matrix = [[0 for i in range(3)] for j in range(3)]
                impedance_matrix_direct = False
                try:
                    impedance_matrix[0][0] = config["z11"]
                    impedance_matrix[0][1] = config["z12"]
                    impedance_matrix[0][2] = config["z13"]
                    impedance_matrix[1][0] = config["z21"]
                    impedance_matrix[1][1] = config["z22"]
                    impedance_matrix[1][2] = config["z23"]
                    impedance_matrix[2][0] = config["z31"]
                    impedance_matrix[2][1] = config["z32"]
                    impedance_matrix[2][1] = config["z33"]
                    impedance_matrix_direct = True
                except AttributeError:
                    pass

                if not impedance_matrix_direct:
                    impedance_matrix = self.compute_matrix(list(conductors.keys()))
                    for i in range(len(impedance_matrix)):
                        for j in range(len(impedance_matrix[0])):
                            impedance_matrix[i][j] = impedance_matrix[i][j] / 1609.34

                api_line.impedance_matrix = impedance_matrix
                api_line.wires = list(conductors.keys())
                for api_wire in conductors:
                    try:
                        if api_wire.diameter is not None:
                            api_wire.diameter = (
                                api_wire.diameter / 39.3701
                            )  # i.e. the same for all the wires.
                    except AttributeError:
                        pass
                    try:
                        if api_wire.gmr is not None:
                            api_wire.gmr = api_wire.gmr / 3.28084
                    except AttributeError:
                        pass
                    try:
                        if api_wire.resistance is not None:
                            api_wire.resistance = (
                                api_wire.resistance / 1609.34
                            )  # In Ohms per meter
                    except AttributeError:
                        pass

            if obj_type == "triplex_line":
                api_line = Line(model)
                try:
                    api_line.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_line.length = float(obj["length"]) * 0.3048
                except AttributeError:
                    pass

                try:
                    api_line.from_element = obj["from"]
                except AttributeError:
                    pass

                try:
                    api_line.to_element = obj["to"]
                except AttributeError:
                    pass

                try:
                    config_name = obj["configuration"]
                    config = self.all_gld_objects[config_name]
                    conductors = {}
                    num_phases = 0
                    try:
                        conn1 = config["conductor_1"]
                        num_phases = num_phases + 1
                        api_wire = Wire(model)
                        # api_wire.phase='1' TODO: set the triplex phases to be 1 and 2
                        api_wire.phase = "A"
                        conductors[api_wire] = conn1
                    except AttributeError:
                        pass
                    try:
                        conn2 = config["conductor_2"]
                        num_phases = num_phases + 1
                        api_wire = Wire(model)
                        # api_wire.phase='2' TODO: set the triplex phases to be 1 and 2
                        api_wire.phase = "B"
                        conductors[api_wire] = conn2
                    except AttributeError:
                        pass

                    try:
                        conn1 = config["conductor_N"]
                        num_phases = num_phases + 1
                        api_wire = Wire(model)
                        api_wire.phase = "N"
                        conductors[api_wire] = conn2
                    except AttributeError:
                        pass

                    try:
                        api_wire.insulation_thickness = (
                            float(config["insulation_thickness"]) / 39.3701
                        )
                    except AttributeError:
                        pass

                    try:
                        api_wire.diameter = float(config["diameter"]) / 39.3701
                    except AttributeError:
                        pass

                    for api_wire in conductors:
                        cond_name = conductors[api_wire]
                        conductor = self.all_gld_objects[cond_name]
                        try:
                            api_wire.gmr = (
                                float(conductor["geometric_mean_radius"]) / 3.28084
                            )
                        except AttributeError:
                            pass
                        try:
                            if api_line.length is not None:
                                api_wire.resistance = (
                                    float(conductor["resistance"])
                                    * api_line.length
                                    / 1609.34
                                )  # since we converted the length to m already
                        except AttributeError:
                            pass

                except AttributeError:
                    pass
                impedance_matrix = [[0 for i in range(2)] for j in range(2)]
                impedance_matrix_direct = False
                try:
                    impedance_matrix[0][0] = config["z11"]
                    impedance_matrix[0][1] = config["z12"]
                    impedance_matrix[1][0] = config["z21"]
                    impedance_matrix[1][1] = config["z22"]
                    impedance_matrix_direct = True
                except AttributeError:
                    pass

                if not impedance_matrix_direct:
                    impedance_matrix = self.compute_secondary_matrix(
                        list(conductors.keys())
                    )

                api_line.impedance_matrix = impedance_matrix
                for wire in conductors.keys():
                    api_line.wires.append(wire)

            if obj_type == "underground_line":

                api_line = Line(model)
                api_line.line_type = "underground"
                try:
                    api_line.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_line.length = float(obj["length"]) * 0.3048
                except AttributeError:
                    pass

                try:
                    api_line.from_element = obj["from"]
                except AttributeError:
                    pass

                try:
                    api_line.to_element = obj["to"]
                except AttributeError:
                    pass

                try:
                    config_name = obj["configuration"]
                    config = self.all_gld_objects[config_name]
                    conductors = {}
                    num_phases = 0
                    try:
                        conna = config["conductor_A"]
                        num_phases = num_phases + 1
                        api_wire = Wire(model)
                        api_wire.phase = "A"
                        conductors[api_wire] = conna
                    except AttributeError:
                        pass
                    try:
                        connb = config["conductor_B"]
                        num_phases = num_phases + 1
                        api_wire = Wire(model)
                        api_wire.phase = "B"
                        conductors[api_wire] = connb
                    except AttributeError:
                        pass
                    try:
                        connc = config["conductor_C"]
                        num_phases = num_phases + 1
                        api_wire = Wire(model)
                        api_wire.phase = "C"
                        conductors[api_wire] = connc
                    except AttributeError:
                        pass
                    try:
                        connn = config["conductor_N"]
                        api_wire = Wire(model)
                        api_wire.phase = "N"
                        conductors[api_wire] = connn
                    except AttributeError:
                        pass

                    # Neutral may be concentric for underground cables or may be a separate wire
                    # TODO: consider other attributes of underground cables?
                    for api_wire in conductors:
                        cond_name = conductors[api_wire]
                        conductor = self.all_gld_objects[cond_name]
                        # set gmr to be the conductor gmr for underground cables
                        try:
                            api_wire.gmr = float(conductor["conductor_gmr"])
                        except AttributeError:
                            pass
                        # set resistance to be the conductor gmr for underground cables
                        try:
                            api_wire.resistance = float(
                                conductor["conductor_resistance"]
                            )
                        except AttributeError:
                            pass

                        # if concentric gmr in not None set it for the underground cables
                        try:
                            api_wire.concentric_neutral_gmr = float(
                                conductor["neutral_gmr"]
                            )
                        except AttributeError:
                            pass
                        # if concentric resistances is not None set it for underground cables
                        try:
                            api_wire.concentric_neutral_resistance = float(
                                conductor["neutral_resistance"]
                            )
                        except AttributeError:
                            pass

                    spacing_name = None
                    try:
                        spacing_name = config["spacing"]
                    except AttributeError:
                        pass
                    if spacing_name is not None:
                        # Assume all wires are 6 feet under by default
                        spacing = self.all_gld_objects[spacing_name]
                        lookup = ["A", "B", "C", "N"]
                        rev_lookup = {"A": 0, "B": 1, "C": 2, "N": 3, "E": 4}
                        num_dists = len(lookup)
                        distances = [
                            [-1 for i in range(num_dists)] for j in range(num_dists)
                        ]
                        for i in range(num_dists):
                            for j in range(i + 1, num_dists):
                                name = "distance_%s%s" % (lookup[i], lookup[j])
                                try:
                                    dist = float(spacing[name])
                                    distances[i][j] = dist
                                    distances[j][i] = dist
                                    distances[i][i] = 0
                                    distances[j][j] = 0
                                except AttributeError:
                                    pass
                        n_entries = num_dists ** 2
                        i_index = 0
                        j_index = 0
                        for i in range(num_dists):
                            for j in range(num_dists):
                                if distances[i][j] == -1:
                                    n_entries = n_entries - 1
                                elif distances[i][j] != 0:
                                    i_index = i
                                    j_index = j
                        n_entries = int(math.sqrt(n_entries))
                        if n_entries == 2:
                            if distances[i_index][j_index] != 0:
                                is_seen = False
                                for w in conductors:
                                    if is_seen:
                                        w.X = distances[i_index][j_index]
                                        w.Y = -6
                                    else:
                                        w.X = 0
                                        w.Y = -6
                                        is_seen = True
                            else:
                                logger.warning(
                                    "Spacing distance is 0 - using default positions"
                                )
                                cnt = 0
                                for w in conductors:
                                    w.X = 0.5 * cnt
                                    w.Y = -6
                                    cnt += 1

                        if (
                            n_entries == 3
                        ):  # make longest side on bottom to form a triangle
                            first = -1
                            middle = -1
                            last = -1
                            max = -1
                            total = 0
                            try:
                                for i in range(num_dists):
                                    for j in range(i + 1, num_dists):
                                        if distances[i][j] != -1:
                                            total = total + distances[i][j]
                                            if distances[i][j] > max:
                                                max = distances[i][j]
                                                first = i
                                                last = j

                                for i in range(num_dists):
                                    if (
                                        i != first
                                        and i != last
                                        and distances[i][first] != -1
                                    ):
                                        middle = i
                                heron_s = total / 2.0
                                heron_area = heron_s
                                for i in range(n_entries):
                                    for j in range(i + 1, n_entries):
                                        if distances[i][j] != -1:
                                            heron_area = heron_area * (
                                                heron_s - distances[i][j]
                                            )
                                logger.debug(heron_area)
                                heron_area = math.sqrt(heron_area)
                                height = heron_area * 2 / (max * 1.0)
                                for w in conductors:
                                    if w.phase == lookup[first]:
                                        w.X = 0
                                        w.Y = -6
                                    elif w.phase == lookup[last]:
                                        w.X = max
                                        w.Y = -6
                                    else:
                                        w.Y = -6 + height
                                        w.X = math.sqrt(
                                            distances[middle][first] ** 2 - height ** 2
                                        )

                            except:
                                logger.warning(
                                    "Failed to read spacing - using default positions"
                                )
                                cnt = 0
                                for w in conductors:
                                    w.X = 0.5 * cnt
                                    w.Y = -6
                                    cnt += 1

                            # TODO: underground lines with 4 conductors ABCN. Use Heron's formula for there too in a similar way (works since we have pairwise distances)

                        if (
                            n_entries == 4
                        ):  # make longest side on bottom to form a triangle
                            max_dist = -100
                            max_from = -1
                            max_to = -1
                            try:
                                for i in range(n_entries):
                                    for j in range(n_entries):
                                        if distances[i][j] > max_dist:
                                            max_dist = distances[i][j]
                                            max_from = i
                                            max_to = j

                                seen_one = False
                                first_x = -10
                                first_y = -10
                                first_i = -1
                                for w in conductors:
                                    i = rev_lookup[w.phase]
                                    if i != max_to and i != max_from:
                                        heron_s = (
                                            max_dist
                                            + distances[i][max_to]
                                            + distances[i][max_from]
                                        ) / 2.0
                                        heron_area = (
                                            heron_s
                                            * (heron_s - max_dist)
                                            * (heron_s - distances[i][max_to])
                                            * (heron_s - distances[i][max_from])
                                        )
                                        heron_area = math.sqrt(heron_area)
                                        height = heron_area * 2 / (max_dist * 1.0)
                                        if not seen_one:
                                            w.Y = -6 + height
                                            w.X = math.sqrt(
                                                distances[i][max_from] ** 2
                                                - height ** 2
                                            )
                                            seen_one = True
                                            first_x = w.X
                                            first_y = w.Y
                                            first_i = i

                                        else:
                                            # Warning: possible bug here - needs extra testing.
                                            w.Y = -6 + height
                                            w.X = math.sqrt(
                                                distances[i][max_from] ** 2
                                                - height ** 2
                                            )
                                            if (w.X - first_x) ** 2 + (
                                                w.Y - first_y
                                            ) ** 2 != distances[i][first_i] ** 2:
                                                w.Y = -6 - height
                                    elif i == max_from:
                                        w.X = 0
                                        w.Y = -6
                                    elif i == max_to:
                                        w.X = max_dist
                                        w.Y = -6

                            except:
                                logger.warning(
                                    "Failed to read spacing - using default positions"
                                )
                                cnt = 0
                                for w in conductors:
                                    w.X = 0.5 * cnt
                                    w.Y = -6
                                    cnt += 1

                except AttributeError:
                    pass

                impedance_matrix = [[0 for i in range(3)] for j in range(3)]
                impedance_matrix_direct = False
                try:
                    impedance_matrix[0][0] = config["z11"]
                    impedance_matrix[0][1] = config["z12"]
                    impedance_matrix[0][2] = config["z13"]
                    impedance_matrix[1][0] = config["z21"]
                    impedance_matrix[1][1] = config["z22"]
                    impedance_matrix[1][2] = config["z23"]
                    impedance_matrix[2][0] = config["z31"]
                    impedance_matrix[2][1] = config["z32"]
                    impedance_matrix[2][1] = config["z33"]
                    impedance_matrix_direct = True
                except AttributeError:
                    pass

                if not impedance_matrix_direct:
                    impedance_matrix = self.compute_matrix(list(conductors.keys()))
                    for i in range(len(impedance_matrix)):
                        for j in range(len(impedance_matrix[0])):
                            impedance_matrix[i][j] = impedance_matrix[i][j] / 1609.34

                api_line.impedance_matrix = impedance_matrix
                for wire in conductors.keys():
                    api_line.wires.append(wire)
                for api_wire in conductors:
                    try:
                        if api_wire.gmr is not None:
                            api_wire.gmr = api_wire.gmr / 3.28084
                    except AttributeError:
                        pass
                    try:
                        if api_wire.concentric_neutral_gmr is not None:
                            api_wire.concentric_neutral_gmr = (
                                api_wire.concentric_neutral_gmr / 3.28084
                            )
                    except AttributeError:
                        pass
                    try:
                        if api_wire.resistance is not None:
                            api_wire.resistance = (
                                api_wire.resistance / 1609.34
                            )  # In Ohms per meter
                    except AttributeError:
                        pass
                    try:
                        if api_wire.concentric_neutral_resistance is not None:
                            api_wire.concentric_neutral_resistance = (
                                api_wire.concentric_neutral_resistance / 1609.34
                            )  # In Ohms per meter
                    except AttributeError:
                        pass

            if obj_type == "capacitor":

                api_capacitor = Capacitor(model)
                phase_capacitors = []
                try:
                    api_capacitor.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_capacitor.nominal_voltage = float(obj["nominal_voltage"])
                except AttributeError:
                    pass

                try:
                    api_capacitor.delay = float(obj["time_delay"])
                except AttributeError:
                    pass

                try:
                    control = obj["control"].upper()
                    if control == "VOLT":
                        api_capacitor.mode = "voltage"
                    if control == "VAR":
                        api_capacitor.mode = "reactivePower"
                    if control == "MANUAL":
                        api_capacitor.mode = "none"
                except AttributeError:
                    pass

                try:
                    connecting_element = obj["parent"]
                except AttributeError:
                    pass

                # If both volt and Var limits are set use the Volt ones. Therefore we set the Var values first and overwrite high and low if there are volt ones as well
                try:
                    api_capacitor.high = float(obj["VAr_set_high"])
                    api_capacitor.low = float(obj["VAr_set_low"])
                except AttributeError:
                    pass

                try:
                    api_capacitor.high = float(obj["voltage_set_high"])
                    api_capacitor.low = float(obj["voltage_set_low"])
                except AttributeError:
                    pass

                try:
                    api_capacitor.pt_phase = obj["pt_phase"]
                except AttributeError:
                    pass

                try:
                    varA = float(obj["capacitor_A"])
                    pc = PhaseCapacitor(model)
                    pc.phase = "A"
                    pc.var = varA * 1000000
                    phase_capacitors.append(
                        pc
                    )  # in case there is no switching attribute
                    phase_capacitors[-1].switch = obj["switch_A"]

                except AttributeError:
                    pass

                try:
                    varB = float(obj["capacitor_B"])
                    pc = PhaseCapacitor(model)
                    pc.phase = "B"
                    pc.var = varB * 1000000
                    phase_capacitors.append(
                        pc
                    )  # in case there is no switching attribute
                    phase_capacitors[-1].switch = obj["switch_B"]
                except AttributeError:
                    pass

                try:
                    varC = float(obj["capacitor_C"])
                    pc = PhaseCapacitor(model)
                    pc.phase = "C"
                    pc.var = varC * 1000000
                    phase_capacitors.append(
                        pc
                    )  # in case there is no switching attribute
                    phase_capacitors[-1].switch = obj["switch_C"]
                except AttributeError:
                    pass

                api_capacitor.phase_capacitors = phase_capacitors

            if obj_type == "regulator":
                api_regulator = Regulator(model)
                try:
                    api_regulator.name = obj["name"]
                except AttributeError:
                    pass

                try:
                    api_regulator.high_from = obj["from"]
                except AttributeError:
                    pass

                try:
                    api_regulator.low_to = obj["to"]
                except AttributeError:
                    pass

                winding1 = Winding(model)
                winding1.voltage_type = 0
                winding2 = Winding(model)
                winding2.voltage_type = 2

                try:
                    if hasattr(obj,"nominal_voltage"):
                        nominal_voltage = obj["nominal_voltage"]
                        winding1.nominal_voltage = float(nominal_voltage)
                        winding2.nominal_voltage = float(nominal_voltage)
                    else:
                        from_element = obj["from"]
                        from_nominal_voltage = self.all_gld_objects[from_element]["nominal_voltage"]
                        winding1.nominal_voltage = float(from_nominal_voltage)
                        winding2.nominal_voltage = float(from_nominal_voltage)
                        
                except AttributeError:
                    pass

                try:
                    phases = obj["phases"].strip('"')
                    winding1.phase_windings = []
                    winding2.phase_windings = []
                    for p in phases:
                        if p == "N" or p == "S":
                            continue
                        pw1 = PhaseWinding(model)
                        pw1.phase = p
                        winding1.phase_windings.append(pw1)
                        pw2 = PhaseWinding(model)
                        pw2.phase = p
                        winding2.phase_windings.append(pw2)

                except AttributeError:
                    pass

                try:
                    config_name1 = obj["configuration"]
                    for config_name, config in self.all_gld_objects.items():
                        if config_name == config_name1:

                            for tap_phase in ["A", "B", "C"]:
                                try:
                                    tap = config["tap_pos_%s" % tap_phase]
                                    if (
                                        winding2.phase_windings is None
                                    ):  # i.e. no phases were listed even though they are there. Should only need to check winding2 (not both windings) since the phases are populated at the same time.
                                        winding1.phase_windings = []
                                        winding2.phase_windings = []

                                    index = None
                                    for i in range(len(winding2.phase_windings)):
                                        if (
                                            winding2.phase_windings[i].phase
                                            == tap_phase
                                        ):
                                            index = i
                                            break
                                    if index is None:
                                        pw1 = PhaseWinding(model)
                                        pw1.phase = tap_phase
                                        winding1.phase_windings.append(pw1)
                                        pw2 = PhaseWinding(model)
                                        pw2.phase = tap_phase
                                        winding2.phase_windings.append(pw2)
                                        index = len(winding2.phase_windings) - 1

                                    winding2.phase_windings[index].tap_position = int(
                                        tap
                                    )

                                except AttributeError:
                                    pass

                            for r_comp_phase in ["A", "B", "C"]:
                                try:
                                    r_comp = config[
                                        "compensator_r_setting_%s" % r_comp_phase
                                    ]
                                    if (
                                        winding2.phase_windings is None
                                    ):  # i.e. no phases were listed even though they are there. Should only need to check winding2 (not both windings) since the phases are populated at the same time.
                                        winding1.phase_windings = []
                                        winding2.phase_windings = []

                                    index = None
                                    for i in range(len(winding2.phase_windings)):
                                        if (
                                            winding2.phase_windings[i].phase
                                            == r_comp_phase
                                        ):
                                            index = i
                                            break
                                    if index is None:
                                        pw1 = PhaseWinding(model)
                                        pw1.phase = r_comp_phase
                                        winding1.phase_windings.append(pw1)
                                        pw2 = PhaseWinding(model)
                                        pw2.phase = r_comp_phase
                                        winding2.phase_windings.append(
                                            pw2
                                        )  # Add the phase in for winding 1 as well
                                        index = len(windings2.phase_windings) - 1

                                    winding2.phase_windings[
                                        index
                                    ].compensator_r = float(r_comp)

                                except AttributeError:
                                    pass

                            for x_comp_phase in ["A", "B", "C"]:
                                try:
                                    x_comp = config[
                                        "compensator_x_setting_%s" % x_comp_phase
                                    ]
                                    if (
                                        winding2.phase_windings is None
                                    ):  # i.e. no phases were listed even though they are there. Should only need to check winding2 (not both windings) since the phases are populated at the same time.
                                        winding1.phase_windings = []
                                        winding2.phase_windings = []

                                    index = None
                                    for i in range(len(winding2.phase_windings)):
                                        if (
                                            winding2.phase_windings[i].phase
                                            == x_comp_phase
                                        ):
                                            index = i
                                            break
                                    if index is None:
                                        pw1 = PhaseWinding(model)
                                        pw1.phase = x_comp_phase
                                        winding1.phase_windings.append(pw1)
                                        pw2 = PhaseWinding(model)
                                        pw2.phase = x_comp_phase
                                        winding2.phase_windings.append(
                                            pw2
                                        )  # Add the phase in for winding 1 as well
                                        index = len(windings2.phase_windings) - 1

                                    winding2.phase_windings[
                                        index
                                    ].compensator_x = float(x_comp)

                                except AttributeError:
                                    pass

                            try:
                                conn = config["connect_type"]

                                if conn == 1 or conn == "WYE_WYE":
                                    winding1.connection_type = "Y"
                                    winding2.connection_type = "Y"

                                # Version of GLD this is based on only has Wye-Wye regulators

                            except AttributeError:
                                pass

                            try:
                                api_regulator.delay = float(config["time_delay"])
                            except AttributeError:
                                pass

                            try:
                                api_regulator.bandwidth = float(config["band_width"])
                            except AttributeError:
                                pass

                            try:
                                api_regulator.bandcenter = float(config["band_center"])
                            except AttributeError:
                                pass

                            try:
                                api_regulator.highstep = int(config["raise_taps"])
                            except AttributeError:
                                pass

                            try:
                                api_regulator.lowstep = int(config["lower_taps"])
                            except AttributeError:
                                pass

                            try:
                                api_regulator.pt_ratio = float(
                                    config["power_transducer_ratio"]
                                )
                            except AttributeError:
                                pass

                            try:
                                api_regulator.ct_ratio = float(
                                    config["current_transducer_ratio"]
                                )
                            except AttributeError:
                                pass

                            try:
                                # wire_map = {'A':1,'B':2,'C':3} #Only take one phase (GLD seems to have 3 sometimes)
                                api_regulator.pt_phase = config["PT_phase"].strip('"')[
                                    0
                                ]  # wire_map[config['PT_phase'].strip('"')[0]]
                            except AttributeError:
                                pass

                except AttributeError:
                    pass

                windings = [winding1, winding2]
                api_regulator.windings = windings
