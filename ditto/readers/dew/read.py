# -*- coding: utf-8 -*-
"""
EDD DEW TO DiTTo Conversion

Created on Mon Aug 20 20:18:01 2017

@author: Abilash Thakallapelli

Developed based on EDD DEW Version V10.62.0
"""

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import logging
import os
import math

import numpy as np
import xlrd

from ditto.store import Store
from ditto.models.node import Node
from ditto.models.regulator import Regulator
from ditto.models.base import Unicode
from ditto.models.phase_winding import PhaseWinding
from ditto.models.winding import Winding
from ditto.models.powertransformer import PowerTransformer
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.capacitor import Capacitor
from ditto.models.wire import Wire
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.phase_load import PhaseLoad
from ditto.models.position import Position

logger = logging.getLogger(__name__)


class reader:
    def __init__(self, **kwargs):
        """reader class CONSTRUCTOR.

"""
        if "input_file_path" in kwargs:
            self.input_file_path = kwargs["input_file_path"]
        else:
            self.input_file_path = "./input_file.dew"

        if "databasepath" in kwargs:
            self.databasepath = kwargs["databasepath"]
        else:
            self.databasepath = "./data_base.xlsx"

    def parse(self, model, **kwargs):
        """DEW--->DiTTo parser.

"""
        xl_workbook = xlrd.open_workbook(self.databasepath, "r")
        sheet_names = xl_workbook.sheet_names()
        xl_sheet = xl_workbook.sheet_by_name(sheet_names[0])
        xl_sheet = xl_workbook.sheet_by_index(0)

        for j in range(0, len(sheet_names)):
            globals()["xl_sheet1" + str(j)] = xl_workbook.sheet_by_index(j)
            xl_sheet1 = globals()["xl_sheet1" + str(j)]
            st_name = sheet_names[j] + "_"
            for i in range(0, xl_sheet1.ncols, 1):
                aa = xl_sheet1.col_values(i)
                globals()[st_name + str(xl_sheet1.cell(0, i).value)] = aa[1:]

        #

        #        model = Store()

        #        inputfile = open(os.path.join(dew_models_dir,modelfile),'r')
        inputfile = open(self.input_file_path, "r")
        all_rows = inputfile.readlines()
        curr_object = None
        iter = -1
        niter = -1
        node_volt_dict = {"node": "voltage"}
        for nrow in all_rows:
            niter += 1
            nrow = nrow.strip()
            nentries = nrow.split()
            if nentries[0] == "$CMP," and nentries[18] == "513,":
                nNAM = all_rows[niter + 1].strip()
                nNAM = nNAM.split()
                nNAM1 = all_rows[niter + 1]
                node_path = nentries[32]
                node_frm = -1
                while True:
                    node_frm += 1
                    if node_frm == len(all_rows) - 1:
                        break
                    row_node = all_rows[node_frm]
                    row_node = row_node.strip()
                    row_node1 = row_node.split()
                    if row_node1[0] == "$CMP," and row_node1[1] == node_path:
                        if row_node1[18] == "16,":
                            voltage_node = (
                                float(PTXFRM_DSECKV[int(row_node1[6][:-1])])
                                * 1.732
                                * 1000
                            )
                            break
                        elif row_node1[18] == "1032,":
                            voltage_node = (
                                float(PTSUB_DPHABKV[int(row_node1[6][:-1])]) * 1000
                            )  # multiplied by 1000 to match with ditto, ditto dividing by 1000
                            break
                        else:
                            node_path = row_node1[32]
                            node_frm = -1
                node_volt_dict[nNAM[1][1:-2]] = voltage_node

        for row in all_rows:
            iter += 1
            row = row.strip()
            #        if row[:13]=='$CMP_NEWDATA1':
            #            continue
            entries = row.split()
            # Node Data Start
            if len(entries) > 10 and entries[18] == "513,":
                #            obj = entries[1].split(':')
                obj_class = "node"
                NAM = all_rows[iter + 1].strip()
                NAM = NAM.split()
                NAM1 = all_rows[iter + 1]
                if obj_class == "node":
                    # Using "easier to ask for forgiveness than permission" (EAFP) rather than "look before you leap" (LBYL) which would use if has_attr(obj,'_name').
                    api_node = Node(model)
                    try:
                        if NAM1[:7] == "$CMPNAM":
                            api_node.name = NAM[1][1:-2]
                    except AttributeError:
                        pass

                    try:
                        api_node.nominal_voltage = node_volt_dict[NAM[1][1:-2]]
                    except AttributeError:
                        pass
                    # Posiiton information can be used if required (not stored and not included in ditto)
                    try:
                        position = Position(model)
                        position.lat = float(entries[13][:-1])  # X position in EDD DEW
                        position.long = float(entries[14][:-1])  # Y posiiton in EDD
                        position.elevation = 0
                        api_node.positions.append(position)
                    except AttributeError:
                        pass
                    try:
                        phases = []
                        if entries[7] == "7,":
                            ph = "ABC"
                        elif entries[7] == "6,":
                            ph = "BC"
                        elif entries[7] == "5,":
                            ph = "AC"
                        elif entries[7] == "4,":
                            ph = "C"
                        elif entries[7] == "3,":
                            ph = "AB"
                        elif entries[7] == "2,":
                            ph = "B"
                        else:
                            ph = "A"
                        for i in ph:
                            # With lists of traitlets, the strings aren't automatically cast
                            phases.append(Unicode(i))
                        api_node.phases = phases
                    except AttributeError:
                        pass
            # Node Data End
            # Regulator Start
            if entries[0] == "$CMP," and entries[5] == "22,":
                obj_class = "regulator"
                if obj_class == "regulator":
                    try:
                        phases = []
                        if entries[7] == "7,":
                            ph = "ABC"
                        elif entries[7] == "6,":
                            ph = "BC"
                        elif entries[7] == "5,":
                            ph = "AC"
                        elif entries[7] == "4,":
                            ph = "C"
                        elif entries[7] == "3,":
                            ph = "AB"
                        elif entries[7] == "2,":
                            ph = "B"
                        else:
                            ph = "A"
                    except AttributeError:
                        pass
                    for kk in ph:
                        api_regulator = Regulator(model)
                        iter_reg = iter
                        row_reg = all_rows[iter_reg]
                        while True:
                            iter_reg += 1
                            row_reg = all_rows[iter_reg]
                            if row_reg[:13] == "$CMPSERIALNUM":
                                row_reg = row_reg.strip()
                                row_reg1 = row_reg.split()
                                try:
                                    api_regulator.name = row_reg1[1][1:-2] + "_" + kk
                                    api_regulator.connected_transformer = (
                                        row_reg1[1][1:-2] + "_" + kk
                                    )
                                except AttributeError:
                                    pass
                            if row_reg[:13] == "$CMP_NEWDATA1":
                                break
                        if entries[0] == "$CMP," and entries[5] == "22,":
                            frm = entries[30]
                            iter_frm = -1
                            while True:
                                iter_frm += 1
                                row_frm = all_rows[iter_frm]
                                row_frm = row_frm.strip()
                                row_frm1 = row_frm.split()
                                if row_frm1[0] == "$CMP," and row_frm1[1] == frm:
                                    row_frm2 = all_rows[iter_frm + 1]
                                    row_frm2 = row_frm2.strip()
                                    row_frm3 = row_frm2.split()
                                    try:
                                        api_regulator.from_element = row_frm3[1][1:-2]
                                    except AttributeError:
                                        pass
                                    break
                        if entries[0] == "$CMP," and entries[5] == "22,":
                            frm = entries[29]
                            iter_frm = -1
                            while True:
                                iter_frm += 1
                                row_frm = all_rows[iter_frm]
                                row_frm = row_frm.strip()
                                row_frm1 = row_frm.split()
                                if row_frm1[0] == "$CMP," and row_frm1[1] == frm:
                                    row_frm2 = all_rows[iter_frm + 1]
                                    row_frm2 = row_frm2.strip()
                                    row_frm3 = row_frm2.split()
                                    try:
                                        api_regulator.to_element = row_frm3[1][1:-2]
                                    except AttributeError:
                                        pass
                                    break

                            try:
                                iptr = entries[6][:-1]
                                api_regulator.highstep = int(
                                    PTXFRM_SNUMSTEPS[PTXFRM_IPTROW.index(float(iptr))]
                                )
                                api_regulator.lowstep = int(
                                    PTXFRM_SNUMSTEPS[PTXFRM_IPTROW.index(float(iptr))]
                                )

                            except AttributeError:
                                pass
                        #
                        iter_rwdg = iter
                        row_rwdg = all_rows[iter_rwdg]
                        row_rwdg = row_rwdg.strip()
                        row_rwdg1 = row_rwdg.split()
                        iptr_rwdg = float(row_rwdg1[6][:-1])
                        tf_rcfg = APIXFRMCONIDX_STNAM[
                            int(PTXFRM_IXFRMCON[PTXFRM_IPTROW.index(iptr_rwdg)])
                        ]
                        tf_rcfg1 = tf_rcfg.split(":")
                        if "3-wireSec" in tf_rcfg1[1]:
                            api_regulator.winding = int(3)
                        else:
                            api_regulator.winding = int(2)
                        #
                        iter_wt = iter
                        row_wt = all_rows[iter_wt]
                        while True:
                            iter_wt += 1
                            row_wt = all_rows[iter_wt]
                            if row_wt[:7] == "$CMPCTR":
                                row_wt = row_wt.strip()
                                row_wt1 = row_wt.split()
                                try:
                                    xfrmcon = row_wt1[11][:-1]
                                #                            logger.debug(xfrmcon)
                                except AttributeError:
                                    pass
                                try:
                                    api_regulator.delay = float(row_wt1[50][:-1])
                                except AttributeError:
                                    pass
                                try:
                                    api_regulator.bandwidth = float(row_wt1[18][:-1])
                                except AttributeError:
                                    pass
                                try:
                                    api_regulator.bandcenter = float(row_wt1[17][:-1])
                                except AttributeError:
                                    pass
                            if row_reg[:13] == "$CMP_NEWDATA1":
                                break

                        iter_pt = iter
                        row_pt = all_rows[iter_pt]
                        while True:
                            iter_pt += 1
                            row_pt2 = all_rows[iter_pt]
                            row_pt = row_pt2.strip()
                            row_pt1 = row_pt.split()
                            if row_pt2[:9] == "$CMPADDPT" and row_pt1[1] == "49,":
                                try:
                                    api_regulator.pt_ratio = float(row_pt1[7][:-1])
                                except AttributeError:
                                    pass
                            if row_pt2[:9] == "$CMPADDPT" and row_pt1[1] == "48,":
                                try:
                                    api_regulator.ct_ratio = float(row_pt1[7][:-1])
                                except AttributeError:
                                    pass
                                try:
                                    api_regulator.ct_prim = float(
                                        PTINST_DSECDRATA[
                                            PTINST_IPTROW.index(float(row_pt1[2][:-1]))
                                        ]
                                    ) * float(row_pt1[7][:-1])
                                except AttributeError:
                                    pass
                            if row_pt2[:13] == "$CMP_NEWDATA1":
                                break

            # Regulator End
            # Windings Start
            if entries[0] == "$CMP," and entries[18] == "16,":
                obj_class = "transformer"
                if entries[7] == "7,":
                    ph1 = "ABC"
                elif entries[7] == "6,":
                    ph1 = "BC"
                elif entries[7] == "5,":
                    ph1 = "AC"
                elif entries[7] == "4,":
                    ph1 = "C"
                elif entries[7] == "3,":
                    ph1 = "AB"
                elif entries[7] == "2,":
                    ph1 = "B"
                else:
                    ph1 = "A"
                ph2 = ph1
                if entries[0] == "$CMP," and entries[5] == "22,":
                    nreg = len(ph1)
                else:
                    nreg = 1
                for nr in range(nreg):
                    windings = []
                    if entries[0] == "$CMP," and entries[5] == "22,":
                        ph1 = ph2[nr]
                    else:
                        ph1 = ph2
                    if obj_class == "transformer":
                        iter_wdg = iter
                        row_wdg = all_rows[iter_wdg]
                        row_wdg = row_wdg.strip()
                        row_wdg1 = row_wdg.split()
                        iptr_wdg = float(row_wdg1[6][:-1])
                        tf_cfg = APIXFRMCONIDX_STNAM[
                            int(PTXFRM_IXFRMCON[PTXFRM_IPTROW.index(iptr_wdg)])
                        ]
                        tf_cfg1 = tf_cfg.split(":")
                        prv = PTXFRM_DPRIKV[int(PTXFRM_IPTROW.index(iptr_wdg))]
                        sev = PTXFRM_DSECKV[int(PTXFRM_IPTROW.index(iptr_wdg))]
                        zmag = float(PTXFRM_DISAT0A[int(PTXFRM_IPTROW.index(iptr_wdg))])
                        zang = float(
                            PTXFRM_DVSAT0PC[int(PTXFRM_IPTROW.index(iptr_wdg))]
                        )
                        resistance = zmag * math.cos(math.radians(zang))
                        reactance = zmag * math.sin(math.radians(zang))
                        #                    if resistance == 0.0:
                        #                        resistance = 0.001
                        if "3-wireSec" in tf_cfg1[1]:
                            num_windings = 3
                        else:
                            num_windings = 2
                        for w in range(num_windings):
                            windings.append(Winding(model))
                            if num_windings == 2:
                                if "Y" in tf_cfg1[0 + w]:
                                    windings[w].connection_type = "Y"
                                if "Delta" in tf_cfg1[0 + w] or "Del" in tf_cfg1[0 + w]:
                                    windings[w].connection_type = "D"
                            # TO-DO FOR 3-WINDING TRANSFORMER
                            if w == 0:
                                try:
                                    if len(ph1) == 1:
                                        windings[w].nominal_voltage = (
                                            float(
                                                PTXFRM_DPRIKV[
                                                    int(PTXFRM_IPTROW.index(iptr_wdg))
                                                ]
                                            )
                                            * 10 ** 3
                                        )
                                    else:
                                        windings[w].nominal_voltage = (
                                            float(
                                                PTXFRM_DPRIKV[
                                                    int(PTXFRM_IPTROW.index(iptr_wdg))
                                                ]
                                            )
                                            * 10 ** 3
                                            * pow(3, 0.5)
                                        )
                                    windings[w].rated_power = (
                                        float(
                                            PTXFRM_DNOMKVA[
                                                int(PTXFRM_IPTROW.index(iptr_wdg))
                                            ]
                                        )
                                        * 10 ** 3
                                    )
                                    windings[w].resistance = resistance / 2.0
                                    if prv > sev:
                                        windings[w].voltage_type = 0
                                    else:
                                        windings[w].voltage_type = 0
                                except AttributeError:
                                    pass
                            if w == 1:
                                try:
                                    if len(ph1) == 1:
                                        windings[w].nominal_voltage = (
                                            float(
                                                PTXFRM_DSECKV[
                                                    int(PTXFRM_IPTROW.index(iptr_wdg))
                                                ]
                                            )
                                            * 10 ** 3
                                        )
                                    else:
                                        windings[w].nominal_voltage = (
                                            float(
                                                PTXFRM_DSECKV[
                                                    int(PTXFRM_IPTROW.index(iptr_wdg))
                                                ]
                                            )
                                            * 10 ** 3
                                            * pow(3, 0.5)
                                        )
                                    windings[w].rated_power = (
                                        float(
                                            PTXFRM_DNOMKVA[
                                                int(PTXFRM_IPTROW.index(iptr_wdg))
                                            ]
                                        )
                                        * 10 ** 3
                                    )
                                    if num_windings == 3:
                                        windings[w].resistance = resistance
                                    else:
                                        windings[w].resistance = resistance / 2.0
                                    if prv > sev:
                                        windings[w].voltage_type = 2
                                    else:
                                        windings[w].voltage_type = 2
                                except AttributeError:
                                    pass
                            if w == 2:
                                try:
                                    windings[w].nominal_voltage = (
                                        float(
                                            PTXFRM_DSECKV[
                                                int(PTXFRM_IPTROW.index(iptr_wdg))
                                            ]
                                        )
                                        * 10 ** 3
                                    )
                                    windings[w].rated_power = (
                                        float(
                                            PTXFRM_DNOMKVA[
                                                int(PTXFRM_IPTROW.index(iptr_wdg))
                                            ]
                                        )
                                        * 10 ** 3
                                    )
                                    windings[w].resistance = resistance
                                    if prv > sev:
                                        windings[w].voltage_type = 2
                                    else:
                                        windings[w].voltage_type = 2
                                except AttributeError:
                                    pass
                            iter_pwg = iter
                            row_pwg = all_rows[iter_pwg]
                            while True:
                                iter_pwg += 1
                                row_pwg = all_rows[iter_pwg]
                                if row_pwg[:7] == "$CMPCTR":
                                    row_pwg = row_pwg.strip()
                                    row_pwg1 = row_pwg.split()
                                    try:
                                        phase_windings = []
                                        for p in range(len(ph1)):
                                            phase_windings.append(PhaseWinding(model))
                                            tp = p
                                            if ph1 == "A":
                                                tp = 0
                                            if ph1 == "B":
                                                tp = 1
                                            if ph1 == "C":
                                                tp = 2
                                            phase_windings[p].tap_position = float(
                                                row_pwg1[7 + tp][:-1]
                                            )
                                            #                                                logger.debug(float(row_pwg1[7+tp][:-1]))
                                            phase_windings[p].phase = ph1[p]
                                            phase_windings[p].compensator_r = float(
                                                row_pwg1[19][:-1]
                                            )
                                            phase_windings[p].compensator_x = float(
                                                row_pwg1[20][:-1]
                                            )
                                    except AttributeError:
                                        pass
                                if row_pwg[:13] == "$CMP_NEWDATA1":
                                    break
                            windings[w].phase_windings = phase_windings
                    #                    api_regulator.windings=windings
                    # Windings End
                    #
                    # Transformers Start
                    iter_tf = iter
                    row_tf = all_rows[iter_tf]
                    api_transformer = PowerTransformer(model)
                    while True:
                        iter_tf += 1
                        row_tf = all_rows[iter_tf]
                        if row_tf[:13] == "$CMPSERIALNUM":
                            row_tf = row_tf.strip()
                            row_tf1 = row_tf.split()
                            try:
                                api_transformer.name = row_tf1[1][1:-2] + "_" + ph1
                            except AttributeError:
                                pass
                        if row_tf[:13] == "$CMP_NEWDATA1":
                            break
                    try:
                        api_transformer.emergency_power = (
                            float(
                                PTXFRM_DFAVLTMRATKVA[int(PTXFRM_IPTROW.index(iptr_wdg))]
                            )
                            * 10 ** 3
                        )  # DiTTo in volt ampere
                    except:
                        pass

                    try:
                        api_transformer.loadloss = (
                            float(PTXFRM_DWINDLOSSW[int(PTXFRM_IPTROW.index(iptr_wdg))])
                            + float(
                                PTXFRM_DCORELOSSW[int(PTXFRM_IPTROW.index(iptr_wdg))]
                            )
                        ) / 1000.0  # DiTTo in volt ampere
                    except:
                        pass

                    try:
                        api_transformer.normhkva = (
                            float(PTXFRM_DPRIKV[int(PTXFRM_IPTROW.index(iptr_wdg))])
                            * 10 ** 3
                        )  # DiTTo in volt ampere
                    except:
                        pass

                    try:
                        api_transformer.noload_loss = (
                            float(PTXFRM_DCORELOSSW[int(PTXFRM_IPTROW.index(iptr_wdg))])
                        ) / 1000.0  # DiTTo in volt ampere
                    except:
                        pass

                    if num_windings == 1:
                        api_transformer.reactances = reactance
                    elif num_windings == 2:
                        if reactance == 0.0:
                            reactance = 0.001
                        api_transformer.reactances = []
                        api_transformer.reactances.append(float(reactance))  # XHL
                    #                   logger.debug(reactance)
                    #                    api_transformer.reactances.append(float(reactance*0.5))   #XLT
                    #                    api_transformer.reactances.append(float(reactance*0.5))   #XHT
                    elif num_windings == 3:
                        if (
                            PTXFRM_QCOMPEXISTS[int(PTXFRM_IPTROW.index(iptr_wdg))]
                            == 205.0
                        ):
                            zmag1 = float(
                                PTXFRM_DISAT1A[int(PTXFRM_IPTROW.index(iptr_wdg))]
                            )
                            zang1 = float(
                                PTXFRM_DVSAT1PC[int(PTXFRM_IPTROW.index(iptr_wdg))]
                            )
                            zmag2 = float(
                                PTXFRM_DISAT2A[int(PTXFRM_IPTROW.index(iptr_wdg))]
                            )
                            zang2 = float(
                                PTXFRM_DVSAT2PC[int(PTXFRM_IPTROW.index(iptr_wdg))]
                            )
                            reactance1 = zmag1 * math.sin(math.radians(zang1))
                            reactance2 = zmag2 * math.sin(math.radians(zang2))
                            api_transformer.reactances = []
                            api_transformer.reactances.append(
                                float(reactance1 + reactance2)
                            )  # XHL
                            api_transformer.reactances.append(float(reactance2))  # XLT
                            api_transformer.reactances.append(float(reactance2))  # XHT
                        else:
                            api_transformer.reactances = []
                            api_transformer.reactances.append(float(reactance))  # XHL
                            api_transformer.reactances.append(
                                float(reactance * 0.5)
                            )  # XLT
                            api_transformer.reactances.append(
                                float(reactance * 0.5)
                            )  # XHT
                        #
                        #
                        api_transformer.positions = None
                    #
                    #
                    #
                    if entries[0] == "$CMP," and entries[18] == "16,":
                        frm_tf = entries[30]
                        iter_frm_tf = -1
                        while True:
                            iter_frm_tf += 1
                            row_frm_tf = all_rows[iter_frm_tf]
                            row_frm_tf = row_frm_tf.strip()
                            row_frm1_tf = row_frm_tf.split()
                            if row_frm1_tf[0] == "$CMP," and row_frm1_tf[1] == frm_tf:
                                row_frm2_tf = all_rows[iter_frm_tf + 1]
                                row_frm2_tf = row_frm2_tf.strip()
                                row_frm3_tf = row_frm2_tf.split()
                                try:
                                    api_transformer.from_element = row_frm3_tf[1][1:-2]
                                except AttributeError:
                                    pass
                                break
                    if entries[0] == "$CMP," and entries[18] == "16,":
                        frm_tf = entries[29]
                        iter_frm_tf = -1
                        while True:
                            iter_frm_tf += 1
                            row_frm_tf = all_rows[iter_frm_tf]
                            row_frm_tf = row_frm_tf.strip()
                            row_frm1_tf = row_frm_tf.split()
                            if row_frm1_tf[0] == "$CMP," and row_frm1_tf[1] == frm_tf:
                                row_frm2_tf = all_rows[iter_frm_tf + 1]
                                row_frm2_tf = row_frm2_tf.strip()
                                row_frm3_tf = row_frm2_tf.split()
                                try:
                                    api_transformer.to_element = row_frm3_tf[1][1:-2]
                                except AttributeError:
                                    pass
                                break
                    #
                    api_transformer.windings = windings
            # Transformers End

            # Phase Capacitor

            if entries[0] == "$CMP," and (entries[18] == "32," or entries[18] == "40,"):
                iter_cap = iter
                row_cap = all_rows[iter_cap]
                row_cap = row_cap.strip()
                row_cap1 = row_cap.split()
                iptr_cap = float(row_cap1[6][:-1])
                if entries[7] == "7,":
                    ph_c = "ABC"
                elif entries[7] == "6,":
                    ph_c = "BC"
                elif entries[7] == "5,":
                    ph_c = "AC"
                elif entries[7] == "4,":
                    ph_c = "C"
                elif entries[7] == "3,":
                    ph_c = "AB"
                elif entries[7] == "2,":
                    ph_c = "B"
                else:
                    ph_c = "A"

                api_capacitor = Capacitor(model)
                iter_cap_n = iter
                row_cap_n = all_rows[iter_cap_n]
                while True:
                    iter_cap_n += 1
                    row_cap_n = all_rows[iter_cap_n]
                    if row_cap_n[:13] == "$CMPSERIALNUM":
                        row_cap_n = row_cap_n.strip()
                        row_cap1_n = row_cap_n.split()
                        try:
                            api_capacitor.name = row_cap1_n[1][1:-2]
                        except AttributeError:
                            pass
                    if row_cap_n[:13] == "$CMP_NEWDATA1":
                        break

                if (
                    PTCAP_SCON[PTCAP_IPTROW.index(iptr_cap)] == 1.0
                    or PTCAP_SCON[PTCAP_IPTROW.index(iptr_cap)] == 3.0
                ):
                    api_capacitor.connection_type = "Y"
                    api_capacitor.nominal_voltage = (
                        float(
                            (
                                APILEVIDX_DVARLEV[
                                    int(PTCAP_IVLEV[PTCAP_IPTROW.index(iptr_cap)])
                                ]
                            )
                        )
                        * 10 ** 3
                    )
                elif PTCAP_SCON[PTCAP_IPTROW.index(iptr_cap)] == 2.0:
                    api_capacitor.connection_type = "D"
                    api_capacitor.nominal_voltage = (
                        float(
                            (
                                APILEVIDX_DVARLEV[
                                    int(PTCAP_IVLEV[PTCAP_IPTROW.index(iptr_cap)])
                                ]
                            )
                        )
                        * 10 ** 3
                    )
                else:
                    api_capacitor.nominal_voltage = (
                        float(
                            (
                                APILEVIDX_DVARLEV[
                                    int(PTCAP_IVLEV[PTCAP_IPTROW.index(iptr_cap)])
                                ]
                            )
                            / 1.732
                        )
                        * 10 ** 3
                    )
                    # single phase

                api_capacitor.low = (
                    float(
                        APIRANIDX_DLOWVAL[
                            int(PTCAP_IVRAN[PTCAP_IPTROW.index(iptr_cap)])
                        ]
                    )
                    * 1000
                )  # cross check
                api_capacitor.high = (
                    float(
                        APIRANIDX_DUPVAL[int(PTCAP_IVRAN[PTCAP_IPTROW.index(iptr_cap)])]
                    )
                    * 1000
                )  # cross check

                if entries[0] == "$CMP," and (
                    entries[18] == "32," or entries[18] == "40,"
                ):
                    frm_cap = entries[32]
                    iter_frm_cap = -1
                    while True:
                        iter_frm_cap += 1
                        row_frm_cap = all_rows[iter_frm_cap]
                        row_frm_cap = row_frm_cap.strip()
                        row_frm1_cap = row_frm_cap.split()
                        if row_frm1_cap[0] == "$CMP," and row_frm1_cap[1] == frm_cap:
                            row_frm2_cap = all_rows[iter_frm_cap + 1]
                            row_frm2_cap = row_frm2_cap.strip()
                            row_frm3_cap = row_frm2_cap.split()
                            try:
                                api_capacitor.connecting_element = row_frm3_cap[1][1:-2]
                            except AttributeError:
                                pass
                            break

                iter_sec = iter
                row_sec = all_rows[iter_sec]
                while True:
                    iter_sec += 1
                    row_sec = all_rows[iter_sec]
                    if row_sec[:7] == "$CMPCTR":
                        row_sec = row_sec.strip()
                        row_sec1 = row_sec.split()
                        normalsec = int(row_sec1[44][:-1])
                    if row_sec[:13] == "$CMP_NEWDATA1":
                        break

                phase_capacitors = []
                for p, p_c in enumerate(ph_c):
                    phase_capacitors.append(PhaseCapacitor(model))
                    phase_capacitors[p].phase = p_c
                    if float(PTCAP_SCON[PTCAP_IPTROW.index(iptr_cap)]) in (
                        1.0,
                        2.0,
                        3.0,
                    ):
                        phase_capacitors[p].var = (
                            float(PTCAP_DRATKVAR[PTCAP_IPTROW.index(iptr_cap)])
                            * 10 ** 3
                        ) / 3.0
                    else:
                        phase_capacitors[p].var = (
                            float(PTCAP_DRATKVAR[PTCAP_IPTROW.index(iptr_cap)])
                            * 10 ** 3
                        )
                    phase_capacitors[p].sections = int(
                        PTCAP_SNUMPOSRACK[PTCAP_IPTROW.index(iptr_cap)]
                    )
                    phase_capacitors[p].normalsections = normalsec
                    iter_pcap = iter_cap
                    row_pcap = all_rows[iter_pcap]
                    while True:
                        iter_pcap += 1
                        row_pcap = all_rows[iter_pcap]
                        if row_pcap[:7] == "$CMPCTR":
                            row_pcap = row_pcap.strip()
                            row_pcap1 = row_pcap.split()
                            if p == 0:
                                try:
                                    api_capacitor.delay = float(row_pcap1[50][:-1])
                                except AttributeError:
                                    pass
                            if row_pcap1[3] == "1,":
                                phase_capacitors[p].switch = int(1)
                            else:
                                phase_capacitors[p].switch = int(0)
                        if row_pcap[:13] == "$CMP_NEWDATA1":
                            break
                api_capacitor.phase_capacitors = phase_capacitors

            # Capacitor End
            # Wire Data
            if entries[0] == "$CMP," and (
                entries[18] == "1,"
                or entries[18] == "65,"
                or entries[18] == "129,"
                or entries[18] == "258,"
                or entries[18] == "2,"
                or entries[18] == "6,"
            ):
                # impedance matrix here
                if entries[7] == "7,":
                    ph_w = "ABC"
                elif entries[7] == "6,":
                    ph_w = "BC"
                elif entries[7] == "5,":
                    ph_w = "AC"
                elif entries[7] == "4,":
                    ph_w = "C"
                elif entries[7] == "3,":
                    ph_w = "AB"
                elif entries[7] == "2,":
                    ph_w = "B"
                else:
                    ph_w = "A"
                iter_seq = iter
                row_seq = all_rows[iter_seq]
                while True:
                    iter_seq += 1
                    #                        logger.debug(row_seq)
                    row_seq = all_rows[iter_seq]
                    if row_seq[:7] == "$CMPCHN":
                        row_seq = row_seq.strip()
                        row_seq1 = row_seq.split()
                        PH1 = ""
                        PH2 = ""
                        PH3 = ""
                        if int(row_seq1[9][:-1]) == 0:
                            PH1 = "A"
                        elif int(row_seq1[9][:-1]) == 1:
                            PH1 = "B"
                        elif int(row_seq1[9][:-1]) == 2:
                            PH1 = "C"
                        if int(row_seq1[10][:-1]) == 0:
                            PH2 = "A"
                        elif int(row_seq1[10][:-1]) == 1:
                            PH2 = "B"
                        elif int(row_seq1[10][:-1]) == 2:
                            PH2 = "C"
                        if int(row_seq1[11][:-1]) == 0:
                            PH3 = "A"
                        elif int(row_seq1[11][:-1]) == 1:
                            PH3 = "B"
                        elif int(row_seq1[11][:-1]) == 2:
                            PH3 = "C"
                        PH_SEQ = PH1 + PH2 + PH3
                        ph_w = PH_SEQ
                    #                    logger.debug(ph_w)
                    if row_seq[:13] == "$CMP_NEWDATA1":
                        break
                num_ph = len(ph_w)
                wires = []
                for pw in range(num_ph + 1):
                    wires.append(Wire(model))
                    if pw >= num_ph:
                        wires[pw].phase = "N"
                    else:
                        wires[pw].phase = ph_w[pw]
                        if int(entries[5][:-1]) == 8 or int(entries[5][:-1]) == 100:
                            wires[pw].nameclass = PTSWT_STDESC[int(entries[6][:-1])]
                            wires[pw].is_fuse = True
                            wires[pw].resistance = 0.001
                            wires[pw].ampacity = float(
                                PTSWT_DCURTRATA[int(entries[6][:-1])]
                            )
                            wires[pw].emergency_ampacity = (
                                float(PTSWT_DCURTRATA[int(entries[6][:-1])]) * 1.5
                            )
                        else:
                            wires[pw].is_fuse = False
                        if int(entries[5][:-1]) in (
                            4,
                            5,
                            120,
                            141,
                            216,
                            221,
                            222,
                            226,
                            238,
                            246,
                            6,
                            7,
                            53,
                            58,
                            76,
                        ):
                            wires[pw].nameclass = PTSWT_STDESC[int(entries[6][:-1])]
                            wires[pw].is_switch = 1
                            wires[pw].resistance = 0.001
                            wires[pw].ampacity = float(
                                PTSWT_DCURTRATA[int(entries[6][:-1])]
                            )
                            wires[pw].emergency_ampacity = float(
                                PTSWT_DCURTRATA[int(entries[6][:-1])]
                            )
                        else:
                            wires[pw].is_switch = 0
                    iter_wr = iter
                    row_wr = all_rows[iter_wr]
                    while True:
                        iter_wr += 1
                        row_wr = all_rows[iter_wr]
                        if row_wr[:7] == "$CMPCHN":
                            row_wr = row_wr.strip()
                            row_wr1 = row_wr.split()
                            if (
                                int(entries[5][:-1]) == 35
                                or int(entries[5][:-1]) == 36
                                or int(entries[5][:-1]) == 37
                                or int(entries[5][:-1]) == 38
                            ):
                                #                        if PTLINESPC_SOVERHEAD[int(row_wr1[4][:-1])] == 0.0:
                                if pw >= num_ph:
                                    if int(row_wr1[6][:-1]) == -1:
                                        wires[pw].nameclass = None
                                        wires[pw].diameter = None
                                        wires[pw].gmr = None
                                        wires[
                                            pw
                                        ].ampacity = None  # switches ampacity update it
                                        wires[pw].emergency_ampacity = None
                                        wires[
                                            pw
                                        ].resistance = (
                                            None  # switches resistance update it
                                        )
                                    else:
                                        wires[pw].nameclass = PTLINECOND_STDESC[
                                            int(row_wr1[6][:-1])
                                        ]
                                        wires[pw].diameter = (
                                            float(
                                                PTLINECOND_DRADCONDSUL[
                                                    int(row_wr1[6][:-1])
                                                ]
                                            )
                                            * 2
                                        )
                                        wires[pw].gmr = float(
                                            PTLINECOND_DGMRSUL[int(row_wr1[6][:-1])]
                                        )
                                        wires[pw].ampacity = float(
                                            PTLINECOND_DRATAMBTEMP0A[
                                                int(row_wr1[6][:-1])
                                            ]
                                        )
                                        wires[pw].emergency_ampacity = float(
                                            PTLINECOND_DRATAMBTEMP1A[
                                                int(row_wr1[6][:-1])
                                            ]
                                        )
                                        wires[pw].resistance = float(
                                            PTLINECOND_DROHMPRLUL[int(row_wr1[6][:-1])]
                                        ) * float(row_wr1[13][:-1])
                                else:
                                    wires[pw].nameclass = PTLINECOND_STDESC[
                                        int(row_wr1[5][:-1])
                                    ]
                                    wires[pw].diameter = (
                                        float(
                                            PTLINECOND_DRADCONDSUL[int(row_wr1[5][:-1])]
                                        )
                                        * 2
                                    )
                                    wires[pw].gmr = float(
                                        PTLINECOND_DGMRSUL[int(row_wr1[5][:-1])]
                                    )
                                    #                                logger.debug(float(PTLINECOND_DGMRSUL[int(row_wr1[5][:-1])]))
                                    wires[pw].ampacity = float(
                                        PTLINECOND_DRATAMBTEMP1A[int(row_wr1[5][:-1])]
                                    )
                                    wires[pw].emergency_ampacity = float(
                                        PTLINECOND_DRATAMBTEMP1A[int(row_wr1[5][:-1])]
                                    )
                                    wires[pw].resistance = float(
                                        PTLINECOND_DROHMPRLUL[int(row_wr1[5][:-1])]
                                    ) * float(row_wr1[13][:-1])
                            else:
                                if pw >= num_ph:
                                    if int(row_wr1[6][:-1]) == -1:
                                        wires[pw].nameclass = None
                                        wires[pw].diameter = None
                                        wires[pw].gmr = None
                                        wires[
                                            pw
                                        ].ampacity = None  # switches ampacity update it
                                        wires[pw].emergency_ampacity = None
                                        wires[pw].resistance = None
                                    else:
                                        wires[pw].nameclass = PTCABCOND_STDESC[
                                            int(row_wr1[6][:-1])
                                        ]
                                        wires[pw].diameter = (
                                            float(
                                                PTCABCOND_DRADCONDSUL[
                                                    int(row_wr1[6][:-1])
                                                ]
                                            )
                                            * 2
                                        )
                                        wires[pw].gmr = float(
                                            PTCABCOND_DGMRSUL[int(row_wr1[6][:-1])]
                                        )
                                        wires[pw].resistance = float(
                                            PTCABCOND_DROHMPRLUL[int(row_wr1[6][:-1])]
                                        ) * float(row_wr1[13][:-1])
                                        if (
                                            PTLINESPC_SOVERHEAD[int(row_wr1[4][:-1])]
                                            == 0.0
                                        ):
                                            wires[pw].ampacity = float(
                                                PTCABCOND_DRATA0[int(row_wr1[6][:-1])]
                                            )
                                            wires[pw].emergency_ampacity = float(
                                                PTCABCOND_DRATA0[int(row_wr1[5][:-1])]
                                            )  # not provided
                                        if (
                                            PTLINESPC_SOVERHEAD[int(row_wr1[4][:-1])]
                                            == 1.0
                                        ):
                                            wires[pw].ampacity = float(
                                                PTCABCOND_DRATA1[int(row_wr1[6][:-1])]
                                            )
                                            wires[pw].emergency_ampacity = float(
                                                PTCABCOND_DRATA1[int(row_wr1[5][:-1])]
                                            )  # not provided
                                        if (
                                            PTLINESPC_SOVERHEAD[int(row_wr1[4][:-1])]
                                            == 2.0
                                        ):
                                            wires[pw].ampacity = float(
                                                PTCABCOND_DRATA2[int(row_wr1[6][:-1])]
                                            )
                                            wires[pw].emergency_ampacity = float(
                                                PTCABCOND_DRATA2[int(row_wr1[5][:-1])]
                                            )  # not provided
                                else:
                                    wires[pw].nameclass = PTCABCOND_STDESC[
                                        int(row_wr1[5][:-1])
                                    ]
                                    wires[pw].diameter = (
                                        float(
                                            PTCABCOND_DRADCONDSUL[int(row_wr1[5][:-1])]
                                        )
                                        * 2
                                    )
                                    wires[pw].gmr = float(
                                        PTCABCOND_DGMRSUL[int(row_wr1[5][:-1])]
                                    )
                                    wires[pw].resistance = float(
                                        PTCABCOND_DROHMPRLUL[int(row_wr1[5][:-1])]
                                    ) * float(row_wr1[13][:-1])
                                    if PTLINESPC_SOVERHEAD[int(row_wr1[4][:-1])] == 0.0:
                                        wires[pw].ampacity = float(
                                            PTCABCOND_DRATA0[int(row_wr1[5][:-1])]
                                        )
                                        wires[pw].emergency_ampacity = float(
                                            PTCABCOND_DRATA0[int(row_wr1[5][:-1])]
                                        )  # not provided
                                    if PTLINESPC_SOVERHEAD[int(row_wr1[4][:-1])] == 1.0:
                                        wires[pw].ampacity = float(
                                            PTCABCOND_DRATA1[int(row_wr1[5][:-1])]
                                        )
                                        wires[pw].emergency_ampacity = float(
                                            PTCABCOND_DRATA1[int(row_wr1[5][:-1])]
                                        )  # not provided
                                    if PTLINESPC_SOVERHEAD[int(row_wr1[4][:-1])] == 2.0:
                                        wires[pw].ampacity = float(
                                            PTCABCOND_DRATA2[int(row_wr1[5][:-1])]
                                        )
                                        wires[pw].emergency_ampacity = float(
                                            PTCABCOND_DRATA2[int(row_wr1[5][:-1])]
                                        )  # not provided

                            if (
                                PTLINESPC_TMUTSPC[int(row_wr1[4][:-1])] == 0.0
                                or PTLINESPC_TMUTSPC[int(row_wr1[4][:-1])] == 1.0
                            ):
                                if pw >= num_ph:
                                    wires[pw].X = (
                                        float(PTLINESPC_DXNEU[int(row_wr1[4][:-1])])
                                        * 0.3048
                                        - float(
                                            PTLINESPC_DXPH1ORR1[int(row_wr1[4][:-1])]
                                        )
                                        * 0.3048
                                    )
                                    wires[pw].Y = (
                                        float(PTLINESPC_DYNEU[int(row_wr1[4][:-1])])
                                        * 0.3048
                                        - float(
                                            PTLINESPC_DYPH1ORX1[int(row_wr1[4][:-1])]
                                        )
                                        * 0.3048
                                    )
                                else:
                                    if pw == 0:
                                        wires[pw].X = (
                                            float(
                                                PTLINESPC_DXPH1ORR1[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                        )  # feet to meter converted
                                        wires[pw].Y = (
                                            float(
                                                PTLINESPC_DYPH1ORX1[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                        )  # feet to meter converted
                                    if pw == 1:
                                        wires[pw].X = (
                                            float(
                                                PTLINESPC_DXPH2ORR0[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                            - float(
                                                PTLINESPC_DXPH1ORR1[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                        )
                                        wires[pw].Y = (
                                            float(
                                                PTLINESPC_DYPH2ORX0[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                            - float(
                                                PTLINESPC_DYPH1ORX1[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                        )
                                    if pw == 2:
                                        wires[pw].X = (
                                            float(
                                                PTLINESPC_DXPH3ORY0[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                            - float(
                                                PTLINESPC_DXPH1ORR1[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                        )
                                        wires[pw].Y = (
                                            float(
                                                PTLINESPC_DYPH3ORY1[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                            - float(
                                                PTLINESPC_DYPH1ORX1[
                                                    int(row_wr1[4][:-1])
                                                ]
                                            )
                                            * 0.3048
                                        )

                        if row_wr[:8] == "$CMPOPER":
                            row_wr = row_wr.strip()
                            row_wr1 = row_wr.split()
                            if (
                                int(entries[5][:-1]) == 8 or int(entries[5][:-1]) == 100
                            ) and (int(row_wr1[5]) == 1):
                                wires[pw].is_open = 1  # blown
                            if (
                                int(entries[5][:-1]) == 8 or int(entries[5][:-1]) == 100
                            ) and (int(row_wr1[5]) == 0):
                                wires[pw].is_open = 0  # good
                            if (
                                int(entries[5][:-1])
                                in (
                                    4,
                                    5,
                                    120,
                                    141,
                                    216,
                                    221,
                                    222,
                                    226,
                                    238,
                                    246,
                                    6,
                                    7,
                                    53,
                                    58,
                                    76,
                                )
                            ) and (row_wr1[5] == str(1)):
                                wires[pw].is_open = 1  # open
                            if (
                                int(entries[5][:-1])
                                in (
                                    4,
                                    5,
                                    120,
                                    141,
                                    216,
                                    221,
                                    222,
                                    226,
                                    238,
                                    246,
                                    6,
                                    7,
                                    53,
                                    58,
                                    76,
                                )
                            ) and (row_wr1[5] == str(0)):
                                wires[pw].is_open = 0  # close
                        if row_wr[:13] == "$CMP_NEWDATA1":
                            break
                api_line = Line(model)
                api_line.wires = wires
                if (
                    entries[5] == "35,"
                    or entries[5] == "36,"
                    or entries[5] == "37,"
                    or entries[5] == "38,"
                    or entries[5] == "39,"
                    or entries[5] == "40,"
                    or entries[5] == "41,"
                    or entries[5] == "41,"
                ):
                    api_line.line_type = "overhead"
                if (
                    entries[5] == "43,"
                    or entries[5] == "44,"
                    or entries[5] == "45,"
                    or entries[5] == "46,"
                ):
                    api_line.line_type = "underground"
                if int(entries[5][:-1]) == 8 or int(entries[5][:-1]) == 100:
                    api_line.is_fuse = True
                    api_line.length = 0.1
                else:
                    api_line.is_fuse = False
                if int(entries[5][:-1]) in (
                    4,
                    5,
                    120,
                    141,
                    216,
                    221,
                    222,
                    226,
                    238,
                    246,
                    6,
                    7,
                    53,
                    58,
                    76,
                ):
                    api_line.is_switch = 1
                    api_line.length = 0.1
                else:
                    api_line.is_switch = 0
                #
                iter_lin = iter
                row_lin = all_rows[iter_lin]
                while True:
                    iter_lin += 1
                    row_lin = all_rows[iter_lin]
                    if row_lin[:13] == "$CMPSERIALNUM":
                        row_lin = row_lin.strip()
                        row_lin1 = row_lin.split()
                        try:
                            api_line.name = row_lin1[1][1:-2]
                        except AttributeError:
                            pass
                    if row_lin[:7] == "$CMPCHN":
                        row_lin = row_lin.strip()
                        row_lin1 = row_lin.split()
                        api_line.length = float(row_lin1[13][:-1]) * 304.8
                    if row_lin[:13] == "$CMP_NEWDATA1":
                        break
                if entries[0] == "$CMP," and (
                    entries[18] == "1,"
                    or entries[18] == "65,"
                    or entries[18] == "129,"
                    or entries[18] == "258,"
                    or entries[18] == "2,"
                    or entries[18] == "6,"
                ):
                    frm_ln = entries[32]
                    iter_frm_ln = -1
                    tr = 32
                    while True:
                        iter_frm_ln += 1
                        row_frm_ln = all_rows[iter_frm_ln]
                        row_frm_ln = row_frm_ln.strip()
                        row_frm1_ln = row_frm_ln.split()
                        if row_frm1_ln[0] == "$CMP," and row_frm1_ln[1] == frm_ln:
                            row_frm2_ln = all_rows[iter_frm_ln + 1]
                            row_frm2_ln = row_frm2_ln.strip()
                            row_frm3_ln = row_frm2_ln.split()
                            if row_frm1_ln[18] == "513,":
                                try:
                                    api_line.from_element = row_frm3_ln[1][1:-2]
                                except AttributeError:
                                    pass
                                break
                            else:
                                tr -= 1
                                frm_ln = entries[tr]
                                iter_frm_ln = -1
                #
                if entries[0] == "$CMP," and (
                    entries[18] == "1,"
                    or entries[18] == "65,"
                    or entries[18] == "129,"
                    or entries[18] == "258,"
                    or entries[18] == "2,"
                    or entries[18] == "6,"
                ):
                    frm_ln = entries[1]
                    iter_frm_ln = -1
                    while True:
                        iter_frm_ln += 1
                        row_frm_ln = all_rows[iter_frm_ln]
                        row_frm_ln = row_frm_ln.strip()
                        row_frm1_ln = row_frm_ln.split()
                        if (
                            row_frm1_ln[0] == "$CMP,"
                            and row_frm1_ln[18] == "513,"
                            and row_frm1_ln[32] == frm_ln
                        ):
                            row_frm2_ln = all_rows[iter_frm_ln + 1]
                            row_frm2_ln = row_frm2_ln.strip()
                            row_frm3_ln = row_frm2_ln.split()
                            try:
                                api_line.to_element = row_frm3_ln[1][1:-2]
                            except AttributeError:
                                pass
                            break
                        elif (
                            row_frm1_ln[0] == "$CMP,"
                            and row_frm1_ln[18] == "513,"
                            and row_frm1_ln[34] == frm_ln
                        ):
                            row_frm2_ln = all_rows[iter_frm_ln + 1]
                            row_frm2_ln = row_frm2_ln.strip()
                            row_frm3_ln = row_frm2_ln.split()
                            try:
                                api_line.to_element = row_frm3_ln[1][1:-2]
                            #                            logger.debug('to')
                            #                            logger.debug(row_frm3_ln[1][1:-2])
                            #                            logger.debug('--------')
                            except AttributeError:
                                pass
                            break
                # cable data impedance matrix calculation
                Zabc = np.zeros((3, 3), dtype=complex)
                Z = np.zeros((7, 7), dtype=complex)
                Yabc = np.zeros((3, 3), dtype=complex)
                Pabc = np.zeros((3, 3), dtype=complex)
                Freq_Coeff = 0.00158836 * 60 + 0.00202237 * 60j
                # 60Hz Freq
                Freq_addit = math.log(100 / 60) / 2.0 + 7.6786
                # earth resistivity 100 and freq 60
                Cap_Freq = complex(0, (2.0 * math.pi * 60))
                As = np.zeros((3, 3), dtype=complex)
                a1 = complex(-0.5, 0.8660)
                As[0][0] = 1
                As[0][1] = 1
                As[0][2] = 1
                As[1][0] = 1
                As[1][1] = a1 * a1
                As[1][2] = a1
                As[2][0] = 1
                As[2][1] = a1
                As[2][2] = a1 * a1
                As1 = np.linalg.inv(As)
                iter_ug = iter
                row_ug = all_rows[iter_ug]
                while True:
                    iter_ug += 1
                    row_ug = all_rows[iter_ug]
                    if row_ug[:7] == "$CMPCHN":
                        row_ug = row_ug.strip()
                        row_ug1 = row_ug.split()
                        if (
                            int(entries[5][:-1]) == 43
                            or int(entries[5][:-1]) == 44
                            or int(entries[5][:-1]) == 45
                            or int(entries[5][:-1]) == 46
                        ):
                            if (
                                PTLINESPC_TMUTSPC[int(row_ug1[4][:-1])] == 0.0
                                or PTLINESPC_TMUTSPC[int(row_ug1[4][:-1])] == 1.0
                            ):
                                cond_dia1 = (
                                    float(PTCABCOND_DRADCONDSUL[int(row_ug1[5][:-1])])
                                    * 2
                                )
                                cond_dia2 = (
                                    float(PTCABCOND_DRADCONDSUL[int(row_ug1[5][:-1])])
                                    * 2
                                )
                                cond_dia3 = (
                                    float(PTCABCOND_DRADCONDSUL[int(row_ug1[5][:-1])])
                                    * 2
                                )
                                cond_res1 = (
                                    float(PTCABCOND_DROHMPRLUL[int(row_ug1[5][:-1])])
                                    * 5.28
                                )  # LUL TO MILE
                                cond_res2 = (
                                    float(PTCABCOND_DROHMPRLUL[int(row_ug1[5][:-1])])
                                    * 5.28
                                )  # LUL TO MILE
                                cond_res3 = (
                                    float(PTCABCOND_DROHMPRLUL[int(row_ug1[5][:-1])])
                                    * 5.28
                                )  # LUL TO MILE
                                XA = float(PTLINESPC_DXPH1ORR1[int(row_ug1[4][:-1])])
                                XB = float(PTLINESPC_DXPH2ORR0[int(row_ug1[4][:-1])])
                                XC = float(PTLINESPC_DXPH3ORY0[int(row_ug1[4][:-1])])
                                XN = float(PTLINESPC_DXNEU[int(row_ug1[4][:-1])])
                                permA = float(
                                    PTINSULIDX_DRELATIVEPERMIT[
                                        int(PTCABCOND_IINSUL[int(row_ug1[5][:-1])])
                                    ]
                                )
                                if row_ug1[6] == "-1,":
                                    cond_dia7 = 0.0
                                    cond_res7 = 0.0  # LUL TO MILE
                                else:
                                    cond_dia7 = (
                                        float(
                                            PTCABCOND_DRADCONDSUL[int(row_ug1[6][:-1])]
                                        )
                                        / 12
                                    )
                                    cond_res7 = (
                                        float(
                                            PTCABCOND_DROHMPRLUL[int(row_ug1[6][:-1])]
                                        )
                                        * 5.28
                                    )  # LUL TO MILE
                                if (
                                    PTCABCOND_TCONCENTNEU[int(row_ug1[5][:-1])] == 1.0
                                ):  # CONCENTRIC NEUTRAL
                                    out_dia1 = float(
                                        PTCABCOND_DDIANEUSTRNDSUL[int(row_ug1[5][:-1])]
                                    )
                                    out_dia2 = float(
                                        PTCABCOND_DDIANEUSTRNDSUL[int(row_ug1[5][:-1])]
                                    )
                                    out_dia3 = float(
                                        PTCABCOND_DDIANEUSTRNDSUL[int(row_ug1[5][:-1])]
                                    )
                                    GMR1 = (
                                        float(PTCABCOND_DGMRSUL[int(row_ug1[5][:-1])])
                                        / 12
                                    )
                                    GMR2 = (
                                        float(PTCABCOND_DGMRSUL[int(row_ug1[5][:-1])])
                                        / 12
                                    )
                                    GMR3 = (
                                        float(PTCABCOND_DGMRSUL[int(row_ug1[5][:-1])])
                                        / 12
                                    )
                                    GMR4C = (
                                        float(
                                            PTCABCOND_DNEUSTRNDGMRSUL[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                        / 12
                                    )
                                    GMR5C = (
                                        float(
                                            PTCABCOND_DNEUSTRNDGMRSUL[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                        / 12
                                    )
                                    GMR6C = (
                                        float(
                                            PTCABCOND_DNEUSTRNDGMRSUL[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                        / 12
                                    )
                                    GMR4S = 0
                                    GMR5S = 0
                                    GMR6S = 0
                                    cond_dia4 = (
                                        float(
                                            PTCABCOND_DRADSTRNDSUL[int(row_ug1[5][:-1])]
                                        )
                                        * 2
                                    )
                                    cond_dia5 = (
                                        float(
                                            PTCABCOND_DRADSTRNDSUL[int(row_ug1[5][:-1])]
                                        )
                                        * 2
                                    )
                                    cond_dia6 = (
                                        float(
                                            PTCABCOND_DRADSTRNDSUL[int(row_ug1[5][:-1])]
                                        )
                                        * 2
                                    )
                                    cond_res4 = (
                                        float(
                                            PTCABCOND_DNEUSTRNDROHM[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                        * 5.28
                                    )
                                    cond_res5 = (
                                        float(
                                            PTCABCOND_DNEUSTRNDROHM[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                        * 5.28
                                    )
                                    cond_res6 = (
                                        float(
                                            PTCABCOND_DNEUSTRNDROHM[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                        * 5.28
                                    )
                                    cond_res4S = 0
                                    cond_res5S = 0
                                    cond_res6S = 0
                                    sheild_thick1 = 0
                                    sheild_thick2 = 0
                                    sheild_thick3 = 0
                                    sheild_thick4 = 0
                                    sheild_dia1 = 0
                                    sheild_dia2 = 0
                                    sheild_dia3 = 0
                                    sheild_dia4 = 0
                                    nue_strands4 = float(
                                        PTCABCOND_SNUMNEUSTRND[int(row_ug1[5][:-1])]
                                    )
                                    nue_strands5 = float(
                                        PTCABCOND_SNUMNEUSTRND[int(row_ug1[5][:-1])]
                                    )
                                    nue_strands6 = float(
                                        PTCABCOND_SNUMNEUSTRND[int(row_ug1[5][:-1])]
                                    )
                                    R14 = (out_dia1 - cond_dia4) / 24
                                    R25 = (out_dia2 - cond_dia5) / 24
                                    R36 = (out_dia3 - cond_dia6) / 24
                                    D14 = R14
                                    D25 = R25
                                    D36 = R36
                                    Rcn4 = cond_res4 / nue_strands4
                                    Rcn5 = cond_res5 / nue_strands5
                                    Rcn6 = cond_res6 / nue_strands6
                                    GMRcn4 = pow(
                                        GMR4C
                                        * nue_strands4
                                        * pow(R14, nue_strands4 - 1),
                                        1 / nue_strands4,
                                    )
                                    GMRcn5 = pow(
                                        GMR5C
                                        * nue_strands5
                                        * pow(R25, nue_strands5 - 1),
                                        1 / nue_strands5,
                                    )
                                    GMRcn6 = pow(
                                        GMR6C
                                        * nue_strands6
                                        * pow(R36, nue_strands6 - 1),
                                        1 / nue_strands6,
                                    )
                                    if row_ug1[6] == "-1,":
                                        GMR7 = 0.0
                                        D17 = 0
                                        D27 = 0
                                        D37 = 0
                                    else:
                                        GMR7 = (
                                            float(
                                                PTCABCOND_DGMRSUL[int(row_ug1[6][:-1])]
                                            )
                                            / 12
                                        )
                                        D17 = abs(XN - XA)
                                        D27 = abs(XN - XB)
                                        D37 = abs(XN - XC)
                                elif (
                                    PTCABCOND_TCONCENTNEU[int(row_ug1[5][:-1])] == 0.0
                                ):  # TAPE SHEILD
                                    out_dia1 = float(
                                        PTCABCOND_DCONDJACKETSUL[int(row_ug1[5][:-1])]
                                    )
                                    out_dia2 = float(
                                        PTCABCOND_DCONDJACKETSUL[int(row_ug1[5][:-1])]
                                    )
                                    out_dia3 = float(
                                        PTCABCOND_DCONDJACKETSUL[int(row_ug1[5][:-1])]
                                    )
                                    GMR1 = (
                                        float(PTCABCOND_DGMRSUL[int(row_ug1[5][:-1])])
                                        / 12
                                    )
                                    GMR2 = (
                                        float(PTCABCOND_DGMRSUL[int(row_ug1[5][:-1])])
                                        / 12
                                    )
                                    GMR3 = (
                                        float(PTCABCOND_DGMRSUL[int(row_ug1[5][:-1])])
                                        / 12
                                    )
                                    GMR4C = 0
                                    GMR5C = 0
                                    GMR6C = 0
                                    Tape_Thick = float(
                                        PTCABCOND_DDIANEUSTRNDSUL[int(row_ug1[5][:-1])]
                                    )
                                    GMR4S = (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        + Tape_Thick
                                    ) / 24.0  # recheck this
                                    GMR5S = (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        + Tape_Thick
                                    ) / 24.0  # recheck this
                                    GMR6S = (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        + Tape_Thick
                                    ) / 24.0  # recheck this
                                    cond_dia4 = 0
                                    cond_dia5 = 0
                                    cond_dia6 = 0
                                    cond_res4 = 0
                                    cond_res5 = 0
                                    cond_res6 = 0
                                    cond_res4S = (
                                        (7.9385e8)
                                        * 0.3048
                                        * float(
                                            PTCABCOND_DNEUSTRNDROHM[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                    ) / (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        * Tape_Thick
                                        * 1000
                                    )
                                    cond_res5S = (
                                        (7.9385e8)
                                        * 0.3048
                                        * float(
                                            PTCABCOND_DNEUSTRNDROHM[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                    ) / (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        * Tape_Thick
                                        * 1000
                                    )
                                    cond_res6S = (
                                        (7.9385e8)
                                        * 0.3048
                                        * float(
                                            PTCABCOND_DNEUSTRNDROHM[
                                                int(row_ug1[5][:-1])
                                            ]
                                        )
                                    ) / (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        * Tape_Thick
                                        * 1000
                                    )
                                    sheild_thick1 = Tape_Thick
                                    sheild_thick2 = Tape_Thick
                                    sheild_thick3 = Tape_Thick
                                    sheild_dia1 = (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        + 2 * Tape_Thick
                                    )
                                    # recheck this
                                    sheild_dia2 = (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        + 2 * Tape_Thick
                                    )
                                    # recheck this
                                    sheild_dia3 = (
                                        float(PTCABCOND_DINSULSUL[int(row_ug1[5][:-1])])
                                        + 2 * Tape_Thick
                                    )
                                    # recheck this
                                    nue_strands4 = float(
                                        PTCABCOND_SNUMNEUSTRND[int(row_ug1[5][:-1])]
                                    )
                                    nue_strands5 = float(
                                        PTCABCOND_SNUMNEUSTRND[int(row_ug1[5][:-1])]
                                    )
                                    nue_strands6 = float(
                                        PTCABCOND_SNUMNEUSTRND[int(row_ug1[5][:-1])]
                                    )
                                    R14 = (sheild_dia1 - sheild_thick1) / 2
                                    R25 = (sheild_dia2 - sheild_thick2) / 2
                                    R36 = (sheild_dia3 - sheild_thick3) / 2
                                    D14 = GMR4S
                                    D25 = GMR5S
                                    D36 = GMR6S
                                    # GMR4S =
                                    if row_ug1[6] == "-1,":
                                        GMR7 = 0.0
                                        sheild_thick4 = 0
                                        cond_res7 = 0
                                        D17 = 0
                                        D27 = 0
                                        D37 = 0
                                    else:
                                        GMR7 = (
                                            float(
                                                PTCABCOND_DGMRSUL[int(row_ug1[6][:-1])]
                                            )
                                            / 12
                                        )
                                        sheild_thick4 = float(
                                            PTCABCOND_DDIANEUSTRNDSUL[
                                                int(row_ug1[6][:-1])
                                            ]
                                        )
                                        sheild_dia4 = float(
                                            PTCABCOND_DINSULSUL[int(row_ug1[6][:-1])]
                                        ) + float(
                                            PTCABCOND_DDIANEUSTRNDSUL[
                                                int(row_ug1[6][:-1])
                                            ]
                                        )
                                        # recheck this
                                        cond_res7 = (
                                            float(
                                                PTCABCOND_DROHMPRLUL[
                                                    int(row_ug1[6][:-1])
                                                ]
                                            )
                                            * 5.28
                                        )
                                        D17 = abs(XN - XA)
                                        D27 = abs(XN - XB)
                                        D37 = abs(XN - XC)
                                # 1 = phase conductor #1
                                # 2 = phase conductor #2
                                # 3 = phase conductor #3
                                # 4 = neutral of conductor #1
                                # 5 = neutral of conductor #2
                                # 6 = neutral of conductor #3
                                # 7 = additional neutral conductor (if present)
                                D12 = abs(XB - XA)
                                D13 = abs(XC - XA)
                                D23 = abs(XC - XB)
                                if ph_w == "BC":
                                    out_dia1 = 0
                                    GMR1 = 0
                                    GMR4C = 0
                                    GMR4S = 0
                                    cond_dia1 = 0
                                    cond_dia4 = 0
                                    cond_res1 = 0
                                    cond_res4 = 0
                                    cond_res4S = 0
                                    sheild_thick1 = 0
                                    sheild_dia1 = 0
                                    nue_strands4 = 0
                                    D12 = 0
                                    D13 = 0
                                    D14 = 0
                                    D17 = 0
                                    Rcn4 = 0
                                    GMRcn4 = 0
                                if ph_w == "AC":
                                    out_dia2 = 0
                                    GMR2 = 0
                                    GMR5C = 0
                                    GMR5S = 0
                                    cond_dia2 = 0
                                    cond_dia5 = 0
                                    cond_res2 = 0
                                    cond_res5 = 0
                                    cond_res5S = 0
                                    sheild_thick2 = 0
                                    sheild_dia2 = 0
                                    D12 = 0
                                    D23 = 0
                                    D25 = 0
                                    D27 = 0
                                    Rcn5 = 0
                                    GMRcn5 = 0
                                if ph_w == "C":
                                    out_dia1 = 0
                                    out_dia2 = 0
                                    GMR1 = 0
                                    GMR2 = 0
                                    GMR4C = 0
                                    GMR5C = 0
                                    GMR4S = 0
                                    GMR5S = 0
                                    cond_dia1 = 0
                                    cond_dia2 = 0
                                    cond_dia4 = 0
                                    cond_dia5 = 0
                                    cond_res1 = 0
                                    cond_res2 = 0
                                    cond_res4 = 0
                                    cond_res5 = 0
                                    cond_res4S = 0
                                    cond_res5S = 0
                                    sheild_thick1 = 0
                                    sheild_dia1 = 0
                                    sheild_thick2 = 0
                                    sheild_dia2 = 0
                                    nue_strands4 = 0
                                    nue_strands5 = 0
                                    D12 = 0
                                    D13 = 0
                                    D14 = 0
                                    D17 = 0
                                    D23 = 0
                                    D25 = 0
                                    D27 = 0
                                    Rcn4 = 0
                                    Rcn5 = 0
                                    GMRcn4 = 0
                                    GMRcn5 = 0
                                if ph_w == "AB":
                                    out_dia3 = 0
                                    GMR3 = 0
                                    GMR6C = 0
                                    GMR6S = 0
                                    cond_dia3 = 0
                                    cond_dia6 = 0
                                    cond_res3 = 0
                                    cond_res6 = 0
                                    cond_res6S = 0
                                    sheild_thick3 = 0
                                    sheild_dia3 = 0
                                    nue_strands6 = 0
                                    D13 = 0
                                    D23 = 0
                                    D36 = 0
                                    D37 = 0
                                    Rcn6 = 0
                                    GMRcn6 = 0
                                if ph_w == "B":
                                    out_dia1 = 0
                                    out_dia3 = 0
                                    GMR1 = 0
                                    GMR3 = 0
                                    GMR4C = 0
                                    GMR6C = 0
                                    GMR4S = 0
                                    GMR6S = 0
                                    cond_dia1 = 0
                                    cond_dia3 = 0
                                    cond_dia4 = 0
                                    cond_dia6 = 0
                                    cond_res1 = 0
                                    cond_res3 = 0
                                    cond_res4 = 0
                                    cond_res6 = 0
                                    cond_res4S = 0
                                    cond_res6S = 0
                                    sheild_thick1 = 0
                                    sheild_dia1 = 0
                                    sheild_thick3 = 0
                                    sheild_dia3 = 0
                                    nue_strands4 = 0
                                    nue_strands6 = 0
                                    D12 = 0
                                    D13 = 0
                                    D14 = 0
                                    D17 = 0
                                    D23 = 0
                                    D36 = 0
                                    D37 = 0
                                    Rcn4 = 0
                                    Rcn6 = 0
                                    GMRcn4 = 0
                                    GMRcn6 = 0
                                if ph_w == "A":
                                    out_dia2 = 0
                                    out_dia3 = 0
                                    GMR2 = 0
                                    GMR3 = 0
                                    GMR5C = 0
                                    GMR6C = 0
                                    GMR5S = 0
                                    GMR6S = 0
                                    cond_dia2 = 0
                                    cond_dia3 = 0
                                    cond_dia5 = 0
                                    cond_dia6 = 0
                                    cond_res2 = 0
                                    cond_res3 = 0
                                    cond_res5 = 0
                                    cond_res6 = 0
                                    cond_res5S = 0
                                    cond_res6S = 0
                                    sheild_thick2 = 0
                                    sheild_dia2 = 0
                                    sheild_thick3 = 0
                                    sheild_dia3 = 0
                                    nue_strands5 = 0
                                    nue_strands6 = 0
                                    D12 = 0
                                    D13 = 0
                                    D23 = 0
                                    D25 = 0
                                    D27 = 0
                                    D36 = 0
                                    D37 = 0
                                    Rcn5 = 0
                                    Rcn6 = 0
                                    GMRcn5 = 0
                                    GMRcn6 = 0  # IF END
                                D15 = D12
                                D16 = D13
                                D21 = D12
                                D24 = D21
                                D26 = D23
                                D31 = D13
                                D32 = D23
                                D34 = D31
                                D35 = D32
                                D41 = D14
                                D42 = D24
                                D43 = D34
                                D45 = D12
                                D46 = D13
                                D47 = D17
                                D51 = D15
                                D52 = D25
                                D53 = D35
                                D54 = D45
                                D56 = D23
                                D57 = D27
                                D61 = D16
                                D62 = D26
                                D63 = D36
                                D64 = D46
                                D65 = D56
                                D67 = D37
                                D71 = D17
                                D72 = D27
                                D73 = D37
                                D74 = D17
                                D75 = D27
                                D76 = D37
                                GMR = np.zeros((7, 1), dtype=float)
                                GMR[0] = GMR1
                                GMR[1] = GMR2
                                GMR[2] = GMR3
                                GMR[6] = GMR7
                                cond_res = np.zeros((6, 1), dtype=float)
                                cond_res[0] = cond_res1
                                cond_res[1] = cond_res2
                                cond_res[2] = cond_res3
                                cond_res[3] = cond_res4
                                cond_res[4] = cond_res5
                                cond_res[5] = cond_res6
                                GMRc = np.zeros((6, 1), dtype=float)
                                GMRc[3] = GMRcn4
                                GMRc[4] = GMRcn5
                                GMRc[5] = GMRcn6
                                Rc = np.zeros((6, 1), dtype=float)
                                Rc[3] = Rcn4
                                Rc[4] = Rcn5
                                Rc[5] = Rcn6
                                dis = [
                                    [0.0, D12, D13, D14, D15, D16, D17],
                                    [D21, 0.0, D23, D24, D25, D26, D27],
                                    [D31, D32, 0.0, D34, D35, D36, D37],
                                    [D41, D42, D43, 0.0, D45, D46, D47],
                                    [D51, D52, D53, D54, 0.0, D56, D57],
                                    [D61, D62, D63, D64, D65, 0.0, D67],
                                    [D71, D72, D73, D74, D75, D76, 0.0],
                                ]
                                if (
                                    PTCABCOND_TCONCENTNEU[int(row_ug1[5][:-1])] == 1.0
                                ):  # Concentric Neutral
                                    for i_cn in range(7):
                                        for j_cn in range(7):
                                            if i_cn == j_cn:
                                                if i_cn > 2 and i_cn != 6:
                                                    if GMRc[i_cn] == 0.0:
                                                        Z[i_cn][j_cn] = complex(
                                                            0.0, 0.0
                                                        )
                                                    else:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real + Rc[i_cn],
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(
                                                                    1.0 / GMRc[i_cn]
                                                                )
                                                                + Freq_addit
                                                            ),
                                                        )
                                                else:
                                                    if GMR[i_cn] == 0.0:
                                                        Z[i_cn][j_cn] = complex(
                                                            0.0, 0.0
                                                        )
                                                    else:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real
                                                            + cond_res[i_cn],
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(
                                                                    1.0 / GMR[i_cn]
                                                                )
                                                                + Freq_addit
                                                            ),
                                                        )
                                            else:
                                                if dis[i_cn][j_cn] == 0.0:
                                                    Z[i_cn][j_cn] = complex(0.0, 0.0)
                                                else:
                                                    Z[i_cn][j_cn] = complex(
                                                        Freq_Coeff.real,
                                                        Freq_Coeff.imag
                                                        * (
                                                            math.log(
                                                                1.0 / dis[i_cn][j_cn]
                                                            )
                                                            + Freq_addit
                                                        ),
                                                    )
                                    zijcn = np.matrix(
                                        [
                                            [Z[0][0], Z[0][1], Z[0][2]],
                                            [Z[1][0], Z[1][1], Z[1][2]],
                                            [Z[2][0], Z[2][1], Z[2][2]],
                                        ]
                                    )
                                    zincn = np.matrix(
                                        [
                                            [Z[0][3], Z[0][4], Z[0][5]],
                                            [Z[1][3], Z[1][4], Z[1][5]],
                                            [Z[2][3], Z[2][4], Z[2][5]],
                                        ]
                                    )
                                    znjcn = np.matrix(
                                        [
                                            [Z[3][0], Z[3][1], Z[3][2]],
                                            [Z[4][0], Z[4][1], Z[4][2]],
                                            [Z[5][0], Z[5][1], Z[5][2]],
                                        ]
                                    )
                                    znncn = np.matrix(
                                        [
                                            [Z[3][3], Z[3][4], Z[3][5]],
                                            [Z[4][3], Z[4][4], Z[4][5]],
                                            [Z[5][3], Z[5][4], Z[5][5]],
                                        ]
                                    )
                                    if "A" not in ph_w:
                                        znncn[0][0] = complex(1.0)
                                    if "B" not in ph_w:
                                        znncn[1][1] = complex(1.0)
                                    if "C" not in ph_w:
                                        znncn[2][2] = complex(1.0)
                                    zabc = zijcn - zincn * np.linalg.inv(znncn) * znjcn
                                    Zabc = zabc
                                    Z012 = As1 * zabc * As
                                    # capacitance calculation
                                    if "A" in ph_w:
                                        if (
                                            cond_dia1 == 0
                                            or R14 == 0
                                            or nue_strands4 == 0
                                        ):
                                            can = 0
                                        else:
                                            den_aph = math.log(
                                                R14 / (cond_dia1 / 24.0)
                                            ) - (1.0 / nue_strands4) * math.log(
                                                (nue_strands4) * cond_dia4 / 24.0 / R14
                                            )
                                            if den_aph == 0:
                                                can = 0
                                            else:
                                                can = (
                                                    2.0 * math.pi * 0.01420 * permA
                                                ) / den_aph
                                    else:
                                        can = 0
                                    if "B" in ph_w:
                                        if (
                                            cond_dia2 == 0
                                            or R25 == 0
                                            or nue_strands5 == 0
                                        ):
                                            cbn = 0
                                        else:
                                            den_bph = math.log(
                                                R25 / (cond_dia2 / 24.0)
                                            ) - (1.0 / nue_strands5) * math.log(
                                                (nue_strands5) * cond_dia5 / 24.0 / R25
                                            )
                                            if den_bph == 0:
                                                cbn = 0
                                            else:
                                                cbn = (
                                                    2.0 * math.pi * 0.01420 * permA
                                                ) / den_bph
                                    else:
                                        cbn = 0
                                    if "C" in ph_w:
                                        if (
                                            cond_dia3 == 0
                                            or R36 == 0
                                            or nue_strands6 == 0
                                        ):
                                            ccn = 0
                                        else:
                                            den_cph = math.log(
                                                R36 / (cond_dia3 / 24.0)
                                            ) - (1.0 / nue_strands6) * math.log(
                                                (nue_strands6) * cond_dia6 / 24.0 / R36
                                            )
                                            if den_cph == 0:
                                                ccn = 0
                                            else:
                                                ccn = (
                                                    2.0 * math.pi * 0.01420 * permA
                                                ) / den_cph
                                    else:
                                        ccn = 0
                                    Yabc[0][0] = can * Cap_Freq
                                    Yabc[1][1] = cbn * Cap_Freq
                                    Yabc[2][2] = ccn * Cap_Freq
                                    Y012 = As1 * Yabc * As
                                else:  # Tape sheild
                                    GMRS = np.zeros((6, 1), dtype=float)
                                    GMRS[3] = GMR4S
                                    GMRS[4] = GMR5S
                                    GMRS[5] = GMR6S
                                    shld_res = np.zeros((6, 1), dtype=float)
                                    shld_res[3] = cond_res4S
                                    shld_res[4] = cond_res5S
                                    shld_res[5] = cond_res6S
                                    for i_cn in range(7):
                                        for j_cn in range(7):
                                            if i_cn == j_cn:
                                                if i_cn > 2 and i_cn != 6:
                                                    if GMRS[i_cn] == 0.0:
                                                        Z[i_cn][j_cn] = complex(0.0)
                                                    else:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real
                                                            + shld_res[i_cn],
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(
                                                                    1.0 / GMRS[i_cn]
                                                                )
                                                                + Freq_addit
                                                            ),
                                                        )
                                                elif i_cn == 6:
                                                    if "A" in ph_w:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real
                                                            + cond_res4S,
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(1.0 / GMR4S)
                                                                + Freq_addit
                                                            ),
                                                        )
                                                    elif "B" in ph_w:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real
                                                            + cond_res5S,
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(1.0 / GMR5S)
                                                                + Freq_addit
                                                            ),
                                                        )
                                                    elif "C" in ph_w:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real
                                                            + cond_res6S,
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(1.0 / GMR6S)
                                                                + Freq_addit
                                                            ),
                                                        )
                                                else:
                                                    if GMRS == 0:
                                                        Z[i_cn][j_cn] = complex(0.0)
                                                    else:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real
                                                            + shld_res[i_cn],
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(
                                                                    1.0 / GMRS[i_cn]
                                                                )
                                                                + Freq_addit
                                                            ),
                                                        )
                                            else:
                                                if (
                                                    (i_cn == 0 and j_cn == 3)
                                                    or (i_cn == 1 and j_cn == 4)
                                                    or (i_cn == 2 and j_cn == 5)
                                                ):
                                                    if GMRS == 0:
                                                        Z[i_cn][j_cn] = complex(0.0)
                                                    else:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real,
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(
                                                                    1.0 / GMRS[i_cn]
                                                                )
                                                                + Freq_addit
                                                            ),
                                                        )
                                                else:
                                                    if dis[i_cn][j_cn] == 0:
                                                        Z[i_cn][j_cn] = complex(0.0)
                                                    else:
                                                        Z[i_cn][j_cn] = complex(
                                                            Freq_Coeff.real,
                                                            Freq_Coeff.imag
                                                            * (
                                                                math.log(
                                                                    1.0
                                                                    / dis[i_cn][j_cn]
                                                                )
                                                                + Freq_addit
                                                            ),
                                                        )
                                    zijts = np.matrix(
                                        [
                                            [Z[0][0], Z[0][1], Z[0][2]],
                                            [Z[1][0], Z[1][1], Z[1][2]],
                                            [Z[2][0], Z[2][1], Z[2][2]],
                                        ]
                                    )
                                    zints = np.matrix(
                                        [
                                            [Z[0][3], Z[0][4], Z[0][5], Z[0][6]],
                                            [Z[1][3], Z[1][4], Z[1][5], Z[1][6]],
                                            [Z[2][3], Z[2][4], Z[2][5], Z[2][6]],
                                        ]
                                    )
                                    znjts = np.matrix(
                                        [
                                            [Z[3][0], Z[3][1], Z[3][2]],
                                            [Z[4][0], Z[4][1], Z[4][2]],
                                            [Z[5][0], Z[5][1], Z[5][2]],
                                            [Z[6][0], Z[6][1], Z[6][2]],
                                        ]
                                    )
                                    znnts = np.matrix(
                                        [
                                            [Z[3][3], Z[3][4], Z[3][5], Z[3][6]],
                                            [Z[4][3], Z[4][4], Z[4][5], Z[4][6]],
                                            [Z[5][3], Z[5][4], Z[5][5], Z[5][6]],
                                            [Z[6][3], Z[6][4], Z[6][5], Z[6][6]],
                                        ]
                                    )
                                    if "A" not in ph_w:
                                        znnts[0][0] = complex(1.0)
                                    if "B" not in ph_w:
                                        znnts[1][1] = complex(1.0)
                                    if "C" not in ph_w:
                                        znnts[2][2] = complex(1.0)
                                    zabc = zijts - zints * np.linalg.inv(znnts) * znjts
                                    Zabc = zabc
                                    Zabc = Zabc / 1609.34
                                    Z012 = As1 * zabc * As
                                    if "A" in ph_w:
                                        if cond_dia1 == 0 or R14 == 0:
                                            can = 0
                                        else:
                                            den_aph = math.log(R14 / (cond_dia1 / 2.0))
                                            if den_aph == 0:
                                                can = 0
                                            else:
                                                can = (
                                                    2.0 * math.pi * 0.01420 * permA
                                                ) / den_aph
                                    else:
                                        can = 0
                                    if "B" in ph_w:
                                        if cond_dia2 == 0 or R25 == 0:
                                            cbn = 0
                                        else:
                                            den_bph = math.log(R25 / (cond_dia2 / 2.0))
                                            if den_bph == 0:
                                                cbn = 0
                                            else:
                                                cbn = (
                                                    2.0 * math.pi * 0.01420 * permA
                                                ) / den_bph
                                    else:
                                        cbn = 0
                                    if "C" in ph_w:
                                        if cond_dia3 == 0 or R36 == 0:
                                            ccn = 0
                                        else:
                                            den_cph = math.log(R36 / (cond_dia3 / 2.0))
                                            if den_cph == 0:
                                                ccn = 0
                                            else:
                                                ccn = (
                                                    2.0 * math.pi * 0.01420 * permA
                                                ) / den_cph
                                    else:
                                        ccn = 0
                                        Yabc[0][0] = can * Cap_Freq
                                        Yabc[1][1] = cbn * Cap_Freq
                                        Yabc[2][2] = ccn * Cap_Freq
                            else:  # if sequence impedance componets are defined #expand this part
                                Z012 = Yabc
                                R1 = float(PTLINESPC_DXPH1ORR1[int(entries[6][:-1])])
                                X1 = float(PTLINESPC_DYPH1ORX1[int(entries[6][:-1])])
                                R0 = float(PTLINESPC_DXPH2ORR0[int(entries[6][:-1])])
                                X0 = float(PTLINESPC_DYPH2ORX0[int(entries[6][:-1])])
                                Y1 = float(PTLINESPC_DYPH3ORY1[int(entries[6][:-1])])
                                Y0 = float(PTLINESPC_DXPH3ORY0[int(entries[6][:-1])])
                                if "A" in ph_w:
                                    Zabc[0][0] = ((complex(R1, X1)) / 1.25) / 0.151515
                                    Yabc[0][0] = ((complex(0, Y1)) / 1.25) / 0.151515
                                if "B" in ph_w:
                                    Zabc[1][1] = ((complex(R1, X1)) / 1.25) / 0.151515
                                    Yabc[1][1] = ((complex(0, Y1)) / 1.25) / 0.151515
                                if "C" in ph_w:
                                    Zabc[2][2] = ((complex(R1, X1)) / 1.25) / 0.151515
                                    Yabc[2][2] = ((complex(0, Y1)) / 1.25) / 0.151515
                        elif (
                            int(entries[5][:-1]) == 35
                            or int(entries[5][:-1]) == 36
                            or int(entries[5][:-1]) == 37
                            or int(entries[5][:-1]) == 38
                        ):
                            DAB = 0.0
                            DBC = 0.0
                            DAC = 0.0
                            DAN = 0.0
                            DBN = 0.0
                            DCN = 0.0
                            GMRA_OH = 0.0
                            GMRB_OH = 0.0
                            GMRC_OH = 0.0
                            GMRN_OH = 0.0
                            RESA_OH = 0.0
                            RESB_OH = 0.0
                            RESC_OH = 0.0
                            RESN_OH = 0.0
                            ZAA = 0.0
                            ZAB = 0.0
                            ZAC = 0.0
                            ZAN = 0.0
                            ZBB = 0.0
                            ZBC = 0.0
                            ZBN = 0.0
                            ZCC = 0.0
                            ZCN = 0.0
                            ZNN = 0.0
                            DAAP = 0.0
                            DABP = 0.0
                            DACP = 0.0
                            DANP = 0.0
                            DBBP = 0.0
                            DBCP = 0.0
                            DBNP = 0.0
                            DCCP = 0.0
                            DCNP = 0.0
                            DNNP = 0.0
                            DIAA = 0.0
                            DIAB = 0.0
                            DIAC = 0.0
                            DIAN = 0.0
                            DAE = 0.0
                            DBE = 0.0
                            DCE = 0.0
                            GMRA_OH = (
                                float(PTLINECOND_DGMRSUL[int(row_ug1[5][:-1])]) / 12.0
                            )
                            GMRB_OH = (
                                float(PTLINECOND_DGMRSUL[int(row_ug1[5][:-1])]) / 12.0
                            )
                            GMRC_OH = (
                                float(PTLINECOND_DGMRSUL[int(row_ug1[5][:-1])]) / 12.0
                            )
                            RESA_OH = (
                                float(PTLINECOND_DROHMPRLUL[int(row_ug1[5][:-1])])
                                * 5.28
                            )
                            RESB_OH = (
                                float(PTLINECOND_DROHMPRLUL[int(row_ug1[5][:-1])])
                                * 5.28
                            )
                            RESC_OH = (
                                float(PTLINECOND_DROHMPRLUL[int(row_ug1[5][:-1])])
                                * 5.28
                            )
                            DIAA = (
                                float(PTLINECOND_DRADCONDSUL[int(row_ug1[5][:-1])]) * 2
                            )
                            DIAB = (
                                float(PTLINECOND_DRADCONDSUL[int(row_ug1[5][:-1])]) * 2
                            )
                            DIAC = (
                                float(PTLINECOND_DRADCONDSUL[int(row_ug1[5][:-1])]) * 2
                            )
                            if (
                                PTLINESPC_TMUTSPC[int(row_ug1[4][:-1])] == 0.0
                                or PTLINESPC_TMUTSPC[int(row_ug1[4][:-1])] == 1.0
                            ):
                                X1 = float(PTLINESPC_DXPH1ORR1[int(row_ug1[4][:-1])])
                                X2 = float(PTLINESPC_DXPH2ORR0[int(row_ug1[4][:-1])])
                                X3 = float(PTLINESPC_DXPH3ORY0[int(row_ug1[4][:-1])])
                                Y1 = float(PTLINESPC_DYPH1ORX1[int(row_ug1[4][:-1])])
                                Y2 = float(PTLINESPC_DYPH2ORX0[int(row_ug1[4][:-1])])
                                Y3 = float(PTLINESPC_DYPH3ORY1[int(row_ug1[4][:-1])])
                                PH1 = ""
                                PH2 = ""
                                PH3 = ""
                                if int(row_ug1[9][:-1]) == 0:
                                    PH1 = "A"
                                elif int(row_ug1[9][:-1]) == 1:
                                    PH1 = "B"
                                elif int(row_ug1[9][:-1]) == 2:
                                    PH1 = "C"
                                if int(row_ug1[10][:-1]) == 0:
                                    PH2 = "A"
                                elif int(row_ug1[10][:-1]) == 1:
                                    PH2 = "B"
                                elif int(row_ug1[10][:-1]) == 2:
                                    PH2 = "C"
                                if int(row_ug1[11][:-1]) == 0:
                                    PH3 = "A"
                                elif int(row_ug1[11][:-1]) == 1:
                                    PH3 = "B"
                                elif int(row_ug1[11][:-1]) == 2:
                                    PH3 = "C"
                                PH_SEQ = PH1 + PH2 + PH3
                                if len(ph_w) == 2:
                                    X3 = X2
                                    Y3 = Y2
                                if len(ph_w) == 1:
                                    X2 = X1
                                    Y2 = Y1
                                    X3 = X1
                                    Y3 = Y1
                                if int(row_ug1[9][:-1]) == 0:
                                    XA = X1
                                    YA = Y1
                                elif int(row_ug1[9][:-1]) == 1:
                                    XB = X1
                                    YB = Y1
                                elif int(row_ug1[9][:-1]) == 2:
                                    XC = X1
                                    YC = Y1
                                if int(row_ug1[10][:-1]) == 0:
                                    XA = X2
                                    YA = Y2
                                elif int(row_ug1[10][:-1]) == 1:
                                    XB = X2
                                    YB = Y2
                                elif int(row_ug1[10][:-1]) == 2:
                                    XC = X2
                                    YC = Y2
                                if int(row_ug1[11][:-1]) == 0:
                                    XA = X3
                                    YA = Y3
                                elif int(row_ug1[11][:-1]) == 1:
                                    XB = X3
                                    YB = Y3
                                elif int(row_ug1[11][:-1]) == 2:
                                    XC = X3
                                    YC = Y3
                                if int(row_ug1[6][:-1]) == -1:
                                    XN = 0.0
                                    YN = 0.0
                                else:
                                    XN = float(PTLINESPC_DXNEU[int(row_ug1[4][:-1])])
                                    YN = float(PTLINESPC_DYNEU[int(row_ug1[4][:-1])])
                                DAB = pow((pow(XB - XA, 2) + pow(YB - YA, 2)), 0.5)
                                DAC = pow((pow(XC - XA, 2) + pow(YC - YA, 2)), 0.5)
                                DBC = pow((pow(XC - XB, 2) + pow(YC - YB, 2)), 0.5)
                                DAE = YA
                                DBE = YB
                                DCE = YC
                                DNE = YN
                                DAN = pow((pow(XN - XA, 2) + pow(YN - YA, 2)), 0.5)
                                DBN = pow((pow(XN - XB, 2) + pow(YN - YB, 2)), 0.5)
                                DCN = pow((pow(XN - XC, 2) + pow(YN - YC, 2)), 0.5)
                            if int(row_ug1[6][:-1]) == -1:
                                GMRN_OH = 0
                                RESN_OH = 0
                                DIAN = 0
                            else:
                                GMRN_OH = (
                                    float(PTLINECOND_DGMRSUL[int(row_ug1[6][:-1])])
                                    / 12.0
                                )
                                RESN_OH = (
                                    float(PTLINECOND_DROHMPRLUL[int(row_ug1[6][:-1])])
                                    * 5.28
                                )
                                DIAN = (
                                    float(PTLINECOND_DRADCONDSUL[int(row_ug1[6][:-1])])
                                    * 2
                                )
                            if "A" in ph_w:
                                if GMRA_OH > 0.0 and RESA_OH > 0.0:
                                    ZAA = complex(
                                        RESA_OH + Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / GMRA_OH) + Freq_addit),
                                    )
                                else:
                                    ZAA = 0.0
                                if "B" in ph_w and DAB > 0.0:
                                    ZAB = complex(
                                        Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / DAB) + Freq_addit),
                                    )
                                else:
                                    ZAB = 0.0
                                if "C" in ph_w and DAC > 0.0:
                                    ZAC = complex(
                                        Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / DAC) + Freq_addit),
                                    )
                                else:
                                    ZAC = 0.0
                                if int(row_ug1[6][:-1]) != -1 and DAN > 0.0:
                                    ZAN = complex(
                                        Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / DAN) + Freq_addit),
                                    )
                                else:
                                    ZAN = 0.0
                                if (DIAA > 0.0) and (DAE > 0.0):
                                    DAAP = 2.0 * DAE
                                    PAA = 11.176611 * math.log(DAAP / DIAA * 24.0)
                                    if "B" in ph_w:
                                        DABP = pow(
                                            (pow(XB - XA, 2) + pow(-YB - YA, 2)), 0.5
                                        )
                                        if DAB != 0:
                                            PAB = 11.176611 * math.log(DABP / DAB)
                                        else:
                                            PAB = 0.0
                                    else:
                                        PAB = 0.0
                                    if "C" in ph_w:
                                        DACP = pow(
                                            (pow(XC - XA, 2) + pow(-YC - YA, 2)), 0.5
                                        )
                                        if DAC != 0:
                                            PAC = 11.176611 * math.log(DACP / DAC)
                                        else:
                                            PAC = 0.0
                                    else:
                                        PAC = 0.0
                                    if int(row_ug1[6][:-1]) != -1:
                                        DANP = pow(
                                            (pow(XN - XA, 2) + pow(-YN - YA, 2)), 0.5
                                        )
                                        if DAN != 0:
                                            PAN = 11.176611 * math.log(DANP / DAN)
                                        else:
                                            PAN = 0.0
                                    else:
                                        PAN = 0.0
                                else:
                                    PAA = 0.0
                                    PAB = 0.0
                                    PAC = 0.0
                                    PAN = 0.0
                            else:
                                PAA = 0.0
                                PAB = 0.0
                                PAC = 0.0
                                PAN = 0.0
                                ZAA = 0.0
                                ZAB = 0.0
                                ZAC = 0.0
                                ZAN = 0.0
                            if "B" in ph_w:
                                if GMRB_OH > 0.0 and RESB_OH > 0.0:
                                    ZBB = complex(
                                        RESB_OH + Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / GMRB_OH) + Freq_addit),
                                    )
                                else:
                                    ZBB = 0.0
                                if "C" in ph_w and DBC > 0.0:
                                    ZBC = complex(
                                        Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / DBC) + Freq_addit),
                                    )
                                else:
                                    ZBC = 0.0
                                if int(row_ug1[6][:-1]) != -1 and DBN > 0.0:
                                    ZBN = complex(
                                        Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / DBN) + Freq_addit),
                                    )
                                else:
                                    ZBN = 0.0
                                if (DIAB > 0.0) and (DBE > 0.0):
                                    DBBP = 2.0 * DBE
                                    PBB = 11.176611 * math.log(DBBP / DIAB * 24.0)
                                    if "C" in ph_w:
                                        DBCP = pow(
                                            (pow(XC - XB, 2) + pow(-YC - YB, 2)), 0.5
                                        )
                                        if DBC != 0:
                                            PBC = 11.176611 * math.log(DBCP / DBC)
                                        else:
                                            PBC = 0.0
                                    else:
                                        PBC = 0.0
                                    if int(row_ug1[6][:-1]) != -1:
                                        DBNP = pow(
                                            (pow(XN - XB, 2) + pow(-YN - YB, 2)), 0.5
                                        )
                                        if DBN != 0:
                                            PBN = 11.176611 * math.log(DBNP / DBN)
                                        else:
                                            PBN = 0.0
                                    else:
                                        PBN = 0.0
                                else:
                                    PBB = 0.0
                                    PBC = 0.0
                                    PBN = 0.0
                            else:
                                PBB = 0.0
                                PBC = 0.0
                                PBN = 0.0
                                ZBB = 0.0
                                ZBC = 0.0
                                ZBN = 0.0
                            if "C" in ph_w:
                                if GMRC_OH > 0.0 and RESC_OH > 0.0:
                                    ZCC = complex(
                                        RESC_OH + Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / GMRC_OH) + Freq_addit),
                                    )
                                else:
                                    ZCC = 0.0
                                if int(row_ug1[6][:-1]) != -1 and DCN > 0.0:
                                    ZCN = complex(
                                        Freq_Coeff.real,
                                        Freq_Coeff.imag
                                        * (math.log(1.0 / DCN) + Freq_addit),
                                    )
                                else:
                                    ZCN = 0.0
                                if (DIAC > 0.0) and (DCE > 0.0):
                                    DCCP = 2.0 * DCE
                                    PCC = 11.176611 * math.log(DCCP / DIAC * 24.0)
                                    if int(row_ug1[6][:-1]) != -1:
                                        DCNP = pow(
                                            (pow(XN - XC, 2) + pow(-YN - YC, 2)), 0.5
                                        )
                                        if DCN != 0:
                                            PCN = 11.176611 * math.log(DCNP / DCN)
                                        else:
                                            PCN = 0.0
                                    else:
                                        PCN = 0.0
                                else:
                                    PCC = 0.0
                                    PCN = 0.0
                            else:
                                PCC = 0.0
                                PCN = 0.0
                                ZCC = 0.0
                                ZCN = 0.0
                            ZNN_INV = complex(0, 0)
                            if (
                                int(row_ug1[6][:-1]) != -1
                                and GMRN_OH > 0.0
                                and RESN_OH > 0.0
                            ):
                                ZNN = complex(
                                    RESN_OH + Freq_Coeff.real,
                                    Freq_Coeff.imag
                                    * (math.log(1.0 / GMRN_OH) + Freq_addit),
                                )
                                ZNN_INV = 1 / ZNN
                                if (DIAN > 0.0) and (DNE > 0.0):
                                    DNNP = 2.0 * DNE
                                    PNN = 11.176611 * math.log(DNNP / DIAN * 24.0)
                                else:
                                    PNN = 0.0
                            else:
                                PNN = 0.0
                                ZNN_INV = complex(0, 0)
                            Zabc[0][0] = ZAA - ZAN * ZAN * ZNN_INV
                            Zabc[0][1] = ZAB - ZAN * ZBN * ZNN_INV
                            Zabc[0][2] = ZAC - ZAN * ZCN * ZNN_INV
                            Zabc[1][0] = ZAB - ZBN * ZAN * ZNN_INV
                            Zabc[1][1] = ZBB - ZBN * ZBN * ZNN_INV
                            Zabc[1][2] = ZBC - ZBN * ZCN * ZNN_INV
                            Zabc[2][0] = ZAC - ZCN * ZAN * ZNN_INV
                            Zabc[2][1] = ZBC - ZCN * ZBN * ZNN_INV
                            Zabc[2][2] = ZCC - ZCN * ZCN * ZNN_INV
                            if PNN != 0.0:
                                Pabc[0][0] = PAA - PAN * PAN / PNN
                                Pabc[0][1] = PAB - PAN * PBN / PNN
                                Pabc[1][0] = PAB - PAN * PBN / PNN
                                Pabc[0][2] = PAC - PAN * PCN / PNN
                                Pabc[2][0] = PAC - PAN * PCN / PNN
                                Pabc[1][1] = PBB - PBN * PBN / PNN
                                Pabc[1][2] = PBC - PBN * PCN / PNN
                                Pabc[2][1] = PBC - PBN * PCN / PNN
                                Pabc[2][2] = PCC - PCN * PCN / PNN
                            else:
                                Pabc[0][0] = PAA
                                Pabc[0][1] = PAB
                                Pabc[1][0] = PAB
                                Pabc[0][2] = PAC
                                Pabc[2][0] = PAC
                                Pabc[1][1] = PBB
                                Pabc[1][2] = PBC
                                Pabc[2][1] = PBC
                                Pabc[2][2] = PCC
                            if "A" in ph_w and "B" not in ph_w and "C" not in ph_w:
                                Yabc[0][0] = complex(1.0) / Pabc[0][0] * Cap_Freq
                            elif "A" not in ph_w and "B" in ph_w and "C" not in ph_w:
                                Yabc[1][1] = complex(1.0) / Pabc[1][1] * Cap_Freq
                            elif "A" not in ph_w and "B" not in ph_w and "C" in ph_w:
                                Yabc[2][2] = complex(1.0) / Pabc[2][2] * Cap_Freq
                            elif "A" in ph_w and "B" not in ph_w and "C" in ph_w:
                                DV = Pabc[0][0] * Pabc[2][2] - Pabc[0][2] * Pabc[2][0]
                                Yabc[0][0] = Pabc[2][2] / DV * Cap_Freq
                                Yabc[0][2] = Pabc[0][2] * -1.0 / DV * Cap_Freq
                                Yabc[2][0] = Pabc[2][0] * -1.0 / DV * Cap_Freq
                                Yabc[2][2] = Pabc[0][0] / DV * Cap_Freq
                            elif "A" in ph_w and "B" in ph_w and "C" not in ph_w:
                                DV = Pabc[0][0] * Pabc[1][1] - Pabc[0][1] * Pabc[1][0]
                                Yabc[0][0] = Pabc[1][1] / DV * Cap_Freq
                                Yabc[0][1] = Pabc[0][1] * -1.0 / DV * Cap_Freq
                                Yabc[1][0] = Pabc[1][0] * -1.0 / DV * Cap_Freq
                                Yabc[1][1] = Pabc[0][0] / DV * Cap_Freq
                            elif "A" not in ph_w and "B" in ph_w and "C" in ph_w:
                                DV = Pabc[1][1] * Pabc[2][2] - Pabc[1][2] * Pabc[2][1]
                                Yabc[1][1] = Pabc[2][2] / DV * Cap_Freq
                                Yabc[1][2] = Pabc[1][2] * -1.0 / DV * Cap_Freq
                                Yabc[2][1] = Pabc[2][1] * -1.0 / DV * Cap_Freq
                                Yabc[2][2] = Pabc[1][1] / DV * Cap_Freq
                            elif "A" in ph_w and "B" in ph_w and "C" in ph_w:
                                DV = (
                                    Pabc[0][0] * Pabc[1][1] * Pabc[2][2]
                                    - Pabc[0][0] * Pabc[1][2] * Pabc[2][1]
                                    - Pabc[0][1] * Pabc[1][0] * Pabc[2][2]
                                    + Pabc[0][1] * Pabc[2][0] * Pabc[1][2]
                                    + Pabc[1][0] * Pabc[0][2] * Pabc[2][1]
                                    - Pabc[0][2] * Pabc[1][1] * Pabc[2][0]
                                )
                                Yabc[0][0] = (
                                    (Pabc[1][1] * Pabc[2][2] - Pabc[1][2] * Pabc[2][1])
                                    / DV
                                    * Cap_Freq
                                )
                                Yabc[0][1] = (
                                    (Pabc[0][2] * Pabc[2][1] - Pabc[0][1] * Pabc[2][2])
                                    / DV
                                    * Cap_Freq
                                )
                                Yabc[0][2] = (
                                    (Pabc[0][1] * Pabc[1][2] - Pabc[0][2] * Pabc[1][1])
                                    / DV
                                    * Cap_Freq
                                )
                                Yabc[1][0] = (
                                    (Pabc[2][0] * Pabc[1][2] - Pabc[1][0] * Pabc[2][2])
                                    / DV
                                    * Cap_Freq
                                )
                                Yabc[1][1] = (
                                    (Pabc[0][0] * Pabc[2][2] - Pabc[0][2] * Pabc[2][0])
                                    / DV
                                    * Cap_Freq
                                )
                                Yabc[1][2] = (
                                    (Pabc[1][0] * Pabc[0][2] - Pabc[0][0] * Pabc[1][2])
                                    / DV
                                    * Cap_Freq
                                )
                                Yabc[2][0] = (
                                    (Pabc[1][0] * Pabc[2][1] - Pabc[1][1] * Pabc[2][0])
                                    / DV
                                    * Cap_Freq
                                )
                                Yabc[2][1] = (
                                    (Pabc[0][1] * Pabc[2][0] - Pabc[0][0] * Pabc[2][1])
                                    / DV
                                    * Cap_Freq
                                )
                                Yabc[2][2] = (
                                    (Pabc[0][0] * Pabc[1][1] - Pabc[0][1] * Pabc[1][0])
                                    / DV
                                    * Cap_Freq
                                )
                    if row_ug[:13] == "$CMP_NEWDATA1":
                        break
                Yabc = (Yabc.imag) / 1609.34
                Zabc = Zabc / 1609.34
                if "A" in ph_w and "B" not in ph_w and "C" not in ph_w:
                    Zabc_red = np.zeros((1, 1), dtype=complex)
                    Yabc_red = np.zeros((1, 1), dtype=float)
                    Zabc_red[0][0] = Zabc[0][0]
                    Yabc_red[0][0] = Yabc[0][0]
                elif "A" not in ph_w and "B" in ph_w and "C" not in ph_w:
                    Zabc_red = np.zeros((1, 1), dtype=complex)
                    Yabc_red = np.zeros((1, 1), dtype=float)
                    Zabc_red[0][0] = Zabc[1][1]
                    Yabc_red[0][0] = Yabc[1][1]
                elif "A" not in ph_w and "B" not in ph_w and "C" in ph_w:
                    Zabc_red = np.zeros((1, 1), dtype=complex)
                    Yabc_red = np.zeros((1, 1), dtype=float)
                    Zabc_red[0][0] = Zabc[2][2]
                    Yabc_red[0][0] = Yabc[2][2]
                elif "A" in ph_w and "B" not in ph_w and "C" in ph_w:
                    Zabc_red = np.zeros((2, 2), dtype=complex)
                    Yabc_red = np.zeros((2, 2), dtype=float)
                    Zabc_red[0][0] = Zabc[0][0]
                    Zabc_red[0][1] = Zabc[0][2]
                    Zabc_red[1][0] = Zabc[2][0]
                    Zabc_red[1][1] = Zabc[2][2]
                    Yabc_red[0][0] = Yabc[0][0]
                    Yabc_red[0][1] = Yabc[0][2]
                    Yabc_red[1][0] = Yabc[2][0]
                    Yabc_red[1][1] = Yabc[2][2]
                elif "A" in ph_w and "B" in ph_w and "C" not in ph_w:
                    Zabc_red = np.zeros((2, 2), dtype=complex)
                    Yabc_red = np.zeros((2, 2), dtype=float)
                    Zabc_red[0][0] = Zabc[0][0]
                    Zabc_red[0][1] = Zabc[0][1]
                    Zabc_red[1][0] = Zabc[1][0]
                    Zabc_red[1][1] = Zabc[1][1]
                    Yabc_red[0][0] = Yabc[0][0]
                    Yabc_red[0][1] = Yabc[0][1]
                    Yabc_red[1][0] = Yabc[1][0]
                    Yabc_red[1][1] = Yabc[1][1]
                elif "A" not in ph_w and "B" in ph_w and "C" in ph_w:
                    Zabc_red = np.zeros((2, 2), dtype=complex)
                    Yabc_red = np.zeros((2, 2), dtype=float)
                    Zabc_red[0][0] = Zabc[1][1]
                    Zabc_red[0][1] = Zabc[1][2]
                    Zabc_red[1][0] = Zabc[2][1]
                    Zabc_red[1][1] = Zabc[2][2]
                    Yabc_red[0][0] = Yabc[1][1]
                    Yabc_red[0][1] = Yabc[1][2]
                    Yabc_red[1][0] = Yabc[2][1]
                    Yabc_red[1][1] = Yabc[2][2]
                elif "A" in ph_w and "B" in ph_w and "C" in ph_w:
                    Zabc_red = Zabc
                    Yabc_red = Yabc

                #                    logger.debug(ph_w)
                #                    logger.debug(Yabc)
                #                    logger.debug('----------------------')
                #                    logger.debug(Yabc_red)
                Yabc_red = Yabc_red * 1000 / (Cap_Freq.imag)  # multiply 1000 to nF
                #                    logger.debug('--------------')
                #                    logger.debug(Yabc_red)
                if (
                    np.mean(Zabc_red.real) == 0.0
                    and np.mean(Zabc_red.imag) == 0.0
                    and np.mean(Yabc_red) == 0.0
                ):
                    api_line.impedance_matrix = None
                    api_line.capacitance_matrix = None
                else:
                    if (
                        int(entries[5][:-1]) == 35
                        or int(entries[5][:-1]) == 36
                        or int(entries[5][:-1]) == 37
                        or int(entries[5][:-1]) == 38
                    ):
                        1
                        api_line.capacitance_matrix = Yabc_red.tolist()
                    else:
                        api_line.capacitance_matrix = Yabc_red.tolist()
                    #                api_line.capacitance_matrix = None
                    api_line.impedance_matrix = Zabc_red.tolist()
                    api_line.units = "mi"
            # load
            if entries[0] == "$CMP," and entries[5] == "115,":
                if entries[7] == "7,":
                    ph_ld = "ABC"
                elif entries[7] == "6,":
                    ph_ld = "BC"
                elif entries[7] == "5,":
                    ph_ld = "AC"
                elif entries[7] == "4,":
                    ph_ld = "C"
                elif entries[7] == "3,":
                    ph_ld = "AB"
                elif entries[7] == "2,":
                    ph_ld = "B"
                else:
                    ph_ld = "A"
                for ild, pld in enumerate(ph_ld):
                    api_load = Load(model)
                    iter_ld = iter
                    row_ld = all_rows[iter_ld]
                    row_ld = row_ld.strip()
                    row_ld1 = row_ld.split()
                    frm_ld = entries[32]
                    iter_frm_ld = -1
                    tr = 32
                    while True:
                        iter_frm_ld += 1
                        row_frm_ld = all_rows[iter_frm_ld]
                        row_frm_ld = row_frm_ld.strip()
                        row_frm1_ld = row_frm_ld.split()
                        if row_frm1_ld[0] == "$CMP," and row_frm1_ld[1] == frm_ld:
                            row_frm2_ld = all_rows[iter_frm_ld + 1]
                            row_frm2_ld = row_frm2_ld.strip()
                            row_frm3_ld = row_frm2_ld.split()
                            if row_frm1_ld[18] == "513,":
                                try:
                                    api_load.connecting_element = row_frm3_ld[1][1:-2]
                                    load_node = row_frm3_ld[1][1:-2]
                                except AttributeError:
                                    pass
                                break
                            else:
                                tr -= 1
                                frm_ld = entries[tr]
                                iter_frm_ld = -1
                    iter_ld_n = iter
                    row_ld_n = all_rows[iter_ld_n]
                    while True:
                        iter_ld_n += 1
                        row_ld_n = all_rows[iter_ld_n]
                        if row_ld_n[:13] == "$CMPSERIALNUM":
                            row_ld_n = row_ld_n.strip()
                            row_ld1_n = row_ld_n.split()
                            try:
                                api_load.name = row_ld1_n[1][1:-2] + "_" + pld
                            except AttributeError:
                                pass
                        if row_ld_n[:7] == "$CMPCHN":
                            row_ld_n = row_ld_n.strip()
                            row_ld1_n = row_ld_n.split()
                            phase_loads = PhaseLoad(model)
                            if pld == "A":
                                phase_loads.p = float(row_ld1_n[21][:-1]) * 1000
                                phase_loads.q = float(row_ld1_n[22][:-1]) * 1000
                                phase_loads.phase = "A"
                            if pld == "B":
                                phase_loads.p = float(row_ld1_n[23][:-1]) * 1000
                                phase_loads.q = float(row_ld1_n[24][:-1]) * 1000
                                phase_loads.phase = "B"
                            if pld == "C":
                                phase_loads.p = float(row_ld1_n[25][:-1]) * 1000
                                phase_loads.q = float(row_ld1_n[26][:-1]) * 1000
                                phase_loads.phase = "C"
                            api_load.phase_loads.append(phase_loads)
                            try:
                                if row_ld1_n[17][:-1] == "1.000000":
                                    api_load.connection_type = "D"
                                    api_load.nominal_voltage = node_volt_dict[load_node]
                                else:
                                    api_load.connection_type = "Y"
                                    api_load.nominal_voltage = (
                                        node_volt_dict[load_node]
                                    ) / pow(3, 0.5)
                                if int(row_ld1_n[37][:-1]) == 1:
                                    api_load.vmin = float(row_ld1_n[39][:-1])
                                    api_load.vmax = float(row_ld1_n[38][:-1])
                                else:
                                    api_load.vmin = 0.95
                                    api_load.vmax = 1.05
                            except AttributeError:
                                pass
                        if row_ld_n[:13] == "$CMP_NEWDATA1":
                            break
