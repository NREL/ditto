# coding: utf8

###### Read  in the synergi database #######
from .db_parser import DbParser

# Python import
import math
import sys
import os
import json
import numpy as np
import logging
import time
import operator

# Ditto imports #

from ditto.readers.abstract_reader import AbstractReader
from ditto.store import Store
from ditto.models.node import Node
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
from ditto.models.power_source import PowerSource
from ditto.models.position import Position

from ditto.models.base import Unicode

from ditto.models.recorder import Recorder

logger = logging.getLogger(__name__)


class Reader:
    """
    Synergi Reader class.
    """

    register_names = ["synergi", "Synergi", "syn"]

    def __init__(self, **kwargs):
        """Constructor for the Synergi reader."""

        self.input_file = None
        if "input_file" in kwargs:
            self.input_file = kwargs["input_file"]
        else:
            mdb_files = [f for f in os.listdir(".") if f.endswith(".mdb")]
            if len(mdb_files) == 1:
                self.input_file = mdb_files[0]

    def parse(self, model):
        """
        Synergi --> DiTTo parse method.
        """
        ProjectFiles = {"Synegi Circuit Database": self.input_file}
        SynergiData = DbParser(ProjectFiles)

        ############ Get the data in #################################################

        ## Feeder ID ##########
        ## This is used to separate different feeders ##
        FeederId = SynergiData.SynergiDictionary["InstFeeders"]["FeederId"]

        ## Node ###########
        NodeID = SynergiData.SynergiDictionary["Node"]["NodeId"]

        ###### Transformer ##################
        TransformerId = SynergiData.SynergiDictionary["InstPrimaryTransformers"][
            "UniqueDeviceId"
        ]
        TransformerSectionId = SynergiData.SynergiDictionary["InstPrimaryTransformers"][
            "SectionId"
        ]
        TransformerType = SynergiData.SynergiDictionary["InstPrimaryTransformers"][
            "TransformerType"
        ]

        ## Substration Transformers ##
        SubstationTransformerV = SynergiData.SynergiDictionary[
            "InstSubstationTransformers"
        ]["NominalKvll"]

        ## Transformer Setting ##
        TransformerTypesinStock = SynergiData.SynergiDictionary["DevTransformers"][
            "TransformerName"
        ]
        HighSideRatedKv = SynergiData.SynergiDictionary["DevTransformers"][
            "HighSideRatedKv"
        ]
        LowSideRatedKv = SynergiData.SynergiDictionary["DevTransformers"][
            "LowSideRatedKv"
        ]
        TransformerRatedKva = SynergiData.SynergiDictionary["DevTransformers"][
            "TransformerRatedKva"
        ]
        PercentImpedance = SynergiData.SynergiDictionary["DevTransformers"][
            "PercentImpedance"
        ]
        PercentResistance = SynergiData.SynergiDictionary["DevTransformers"][
            "PercentResistance"
        ]
        HighVoltageConnectionCode = SynergiData.SynergiDictionary["DevTransformers"][
            "HighVoltageConnectionCode"
        ]
        LowVoltageConnectionCode = SynergiData.SynergiDictionary["DevTransformers"][
            "LowVoltageConnectionCode"
        ]

        ########## Line #####################
        LineID = SynergiData.SynergiDictionary["InstSection"]["SectionId"]
        LineLength = SynergiData.SynergiDictionary["InstSection"]["SectionLength_MUL"]
        PhaseConductorID = SynergiData.SynergiDictionary["InstSection"][
            "PhaseConductorId"
        ]
        NeutralConductorID = SynergiData.SynergiDictionary["InstSection"][
            "NeutralConductorId"
        ]
        SectionPhases = SynergiData.SynergiDictionary["InstSection"]["SectionPhases"]
        LineFeederId = SynergiData.SynergiDictionary["InstSection"]["FeederId"]
        FromNodeId = SynergiData.SynergiDictionary["InstSection"]["FromNodeId"]
        ToNodeId = SynergiData.SynergiDictionary["InstSection"]["ToNodeId"]
        IsFromEndOpen = SynergiData.SynergiDictionary["InstSection"]["IsFromEndOpen"]
        IsToEndOpen = SynergiData.SynergiDictionary["InstSection"]["IsToEndOpen"]

        ## Wires ###########
        CableGMR = SynergiData.SynergiDictionary["DevConductors"]["CableGMR_MUL"]
        CableDiamOutside = SynergiData.SynergiDictionary["DevConductors"][
            "CableDiamOutside_SUL"
        ]
        CableResistance = SynergiData.SynergiDictionary["DevConductors"][
            "CableResistance_PerLUL"
        ]
        ConductorName = SynergiData.SynergiDictionary["DevConductors"]["ConductorName"]
        PosSequenceResistance_PerLUL = SynergiData.SynergiDictionary["DevConductors"][
            "PosSequenceResistance_PerLUL"
        ]
        PosSequenceReactance_PerLUL = SynergiData.SynergiDictionary["DevConductors"][
            "PosSequenceReactance_PerLUL"
        ]
        ZeroSequenceResistance_PerLUL = SynergiData.SynergiDictionary["DevConductors"][
            "ZeroSequenceResistance_PerLUL"
        ]
        ZeroSequenceReactance_PerLUL = SynergiData.SynergiDictionary["DevConductors"][
            "ZeroSequenceReactance_PerLUL"
        ]

        ## Loads #############
        LoadName = SynergiData.SynergiDictionary["Loads"]["SectionId"]
        Phase1Kw = SynergiData.SynergiDictionary["Loads"]["Phase1Kw"]
        Phase2Kw = SynergiData.SynergiDictionary["Loads"]["Phase2Kw"]
        Phase3Kw = SynergiData.SynergiDictionary["Loads"]["Phase3Kw"]
        Phase1Kvar = SynergiData.SynergiDictionary["Loads"]["Phase1Kvar"]
        Phase2Kvar = SynergiData.SynergiDictionary["Loads"]["Phase2Kvar"]
        Phase3Kvar = SynergiData.SynergiDictionary["Loads"]["Phase3Kvar"]

        ## Capacitors ################
        CapacitorName = SynergiData.SynergiDictionary["InstCapacitors"][
            "UniqueDeviceId"
        ]
        CapacitorVoltage = SynergiData.SynergiDictionary["InstCapacitors"]["RatedKv"]
        CapacitorConnectionType = SynergiData.SynergiDictionary["InstCapacitors"][
            "ConnectionType"
        ]
        CapacitorTimeDelaySec = SynergiData.SynergiDictionary["InstCapacitors"][
            "TimeDelaySec"
        ]
        CapacitorPrimaryControlMode = SynergiData.SynergiDictionary["InstCapacitors"][
            "PrimaryControlMode"
        ]
        CapacitorModule1CapSwitchCloseValue = SynergiData.SynergiDictionary[
            "InstCapacitors"
        ]["Module1CapSwitchCloseValue"]
        CapacitorModule1CapSwitchTripValue = SynergiData.SynergiDictionary[
            "InstCapacitors"
        ]["Module1CapSwitchTripValue"]
        CapacitorPTRatio = SynergiData.SynergiDictionary["InstCapacitors"][
            "CapacitorPTRatio"
        ]
        CapacitorCTRating = SynergiData.SynergiDictionary["InstCapacitors"][
            "CapacitorCTRating"
        ]
        CapacitorSectionId = SynergiData.SynergiDictionary["InstCapacitors"][
            "SectionId"
        ]

        CapacitorFixedKvarPhase1 = SynergiData.SynergiDictionary["InstCapacitors"][
            "FixedKvarPhase1"
        ]
        CapacitorFixedKvarPhase2 = SynergiData.SynergiDictionary["InstCapacitors"][
            "FixedKvarPhase2"
        ]
        CapacitorFixedKvarPhase3 = SynergiData.SynergiDictionary["InstCapacitors"][
            "FixedKvarPhase3"
        ]

        ## Regulators ###################
        RegulatorId = SynergiData.SynergiDictionary["InstRegulators"]["UniqueDeviceId"]
        RegulatorTimeDelay = SynergiData.SynergiDictionary["InstRegulators"][
            "TimeDelaySec"
        ]
        RegulatorTapLimiterHighSetting = SynergiData.SynergiDictionary[
            "InstRegulators"
        ]["TapLimiterHighSetting"]
        RegulatorTapLimiterLowSetting = SynergiData.SynergiDictionary["InstRegulators"][
            "TapLimiterLowSetting"
        ]
        RegulatorTapLimiterLowSetting = SynergiData.SynergiDictionary["InstRegulators"][
            "TapLimiterLowSetting"
        ]
        RegulatrorForwardBWDialPhase1 = SynergiData.SynergiDictionary["InstRegulators"][
            "ForwardBWDialPhase1"
        ]
        RegulatrorForwardBWDialPhase2 = SynergiData.SynergiDictionary["InstRegulators"][
            "ForwardBWDialPhase2"
        ]
        RegulatrorForwardBWDialPhase3 = SynergiData.SynergiDictionary["InstRegulators"][
            "ForwardBWDialPhase3"
        ]
        RegulatrorForwardVoltageSettingPhase1 = SynergiData.SynergiDictionary[
            "InstRegulators"
        ]["ForwardVoltageSettingPhase1"]
        RegulatrorForwardVoltageSettingPhase1 = SynergiData.SynergiDictionary[
            "InstRegulators"
        ]["ForwardVoltageSettingPhase1"]
        RegulatrorForwardVoltageSettingPhase2 = SynergiData.SynergiDictionary[
            "InstRegulators"
        ]["ForwardVoltageSettingPhase2"]
        RegulatrorForwardVoltageSettingPhase3 = SynergiData.SynergiDictionary[
            "InstRegulators"
        ]["ForwardVoltageSettingPhase3"]
        RegulatrorSectionId = SynergiData.SynergiDictionary["InstRegulators"][
            "SectionId"
        ]
        RegulagorPhases = SynergiData.SynergiDictionary["InstRegulators"][
            "ConnectedPhases"
        ]
        RegulatorTypes = SynergiData.SynergiDictionary["InstRegulators"][
            "RegulatorType"
        ]

        RegulatrorNames = SynergiData.SynergiDictionary["DevRegulators"][
            "RegulatorName"
        ]
        RegulatorPTRatio = SynergiData.SynergiDictionary["DevRegulators"]["PTRatio"]
        RegulatorCTRating = SynergiData.SynergiDictionary["DevRegulators"]["CTRating"]

        RegulatorNearFromNode = SynergiData.SynergiDictionary["InstRegulators"][
            "NearFromNode"
        ]

        ##### PV ##################################
        PVUniqueDeviceId = SynergiData.SynergiDictionary["InstLargeCust"][
            "UniqueDeviceId"
        ]
        PVSectionId = SynergiData.SynergiDictionary["InstLargeCust"]["SectionId"]
        PVGenType = SynergiData.SynergiDictionary["InstLargeCust"]["GenType"]
        PVGenPhase1Kw = SynergiData.SynergiDictionary["InstLargeCust"]["GenPhase1Kw"]
        PVGenPhase2Kw = SynergiData.SynergiDictionary["InstLargeCust"]["GenPhase2Kw"]
        PVGenPhase3Kw = SynergiData.SynergiDictionary["InstLargeCust"]["GenPhase3Kw"]

        ######################### Converting to Ditto #################################################

        ## Feeder ID###########
        NFeeder = len(FeederId)

        ######## Converting Node into Ditto##############
        # N = len(NodeID)
        ## Delete the blank spaces in the phases

        SectionPhases01 = []
        tt = 0
        for obj in SectionPhases:
            SectionPhases_thisline = list(SectionPhases[tt])
            SectionPhases_thisline1 = [
                s.encode("ascii") for s in SectionPhases_thisline
            ]
            SectionPhases_thisline2 = filter(str.strip, SectionPhases_thisline1)
            SectionPhases01.append(SectionPhases_thisline2)
            tt = tt + 1

        ## Get the good lines
        i = 0
        NodeIDgood = []
        for obj in LineID:
            if IsToEndOpen[i] == 0 and IsFromEndOpen[i] == 0:
                FromNodeID1 = FromNodeId[i]
                FromNodeID2 = [s.encode("ascii") for s in FromNodeID1]
                FromNodeID3 = "".join(FromNodeID2)
                ToNodeID1 = ToNodeId[i]
                ToNodeID2 = [s.encode("ascii") for s in ToNodeID1]
                ToNodeID3 = "".join(ToNodeID2)
                NodeIDgood.append(FromNodeID3)
                NodeIDgood.append(ToNodeID3)
            i = i + 1

        # Convert NodeID to ascii code
        i = 0
        NodeID3 = []
        for obj in NodeID:
            NodeID1 = NodeID[i]
            NodeID2 = [s.encode("ascii") for s in NodeID1]
            NodeID3.append("".join(NodeID2))
            i = i + 1

        i = 0
        for obj in NodeID:

            ## Find out if this node is a necessary node
            t = 0
            NodeFlag = 1
            # for obj in NodeIDgood:
            #
            #     if NodeID3[i]==NodeIDgood[t]:
            #         NodeFlag=1
            #         break
            #     t=t+1

            if NodeFlag == 1:

                api_node = Node(model)
                api_node.name = NodeID[i].lower()
                # print(NodeID[i])

                if NodeID[i] == "mikilua 2 tsf":
                    api_node.bustype = "SWING"

                ## Search the nodes in FromNodeID
                tt = 0
                CountFrom = []
                for obj in FromNodeId:
                    Flag = NodeID[i] == FromNodeId[tt]
                    if Flag == True:
                        CountFrom.append(tt)
                    tt = tt + 1

                ## Search in the nodes in ToNodeID
                tt = 0
                CountTo = []
                for obj in ToNodeId:
                    Flag = NodeID[i] == ToNodeId[tt]
                    if Flag == True:
                        CountTo.append(tt)
                    tt = tt + 1

                PotentialNodePhases = []
                ttt = 0
                if CountFrom:
                    for obj in CountFrom:
                        PotentialNodePhases.append(SectionPhases01[CountFrom[ttt]])
                        tt = tt + 1
                        ttt = ttt + 1

                if CountTo:
                    ttt = 0
                    for obj in CountTo:
                        PotentialNodePhases.append(SectionPhases01[CountTo[ttt]])
                        ttt = ttt + 1

                PhaseLength = []
                tt = 0
                for obj in PotentialNodePhases:
                    PhaseLength.append(len(PotentialNodePhases[tt]))
                    tt = tt + 1

                index, value = max(enumerate(PhaseLength), key=operator.itemgetter(1))

                # SectionPhases_thisline = list(PotentialNodePhases[index])
                # SectionPhases_thisline1 = [s.encode('ascii') for s in SectionPhases_thisline]
                # SectionPhases_thisline2 = filter(str.strip, SectionPhases_thisline1)

                # SectionPhases_thisline = [s.decode('utf-8') for s in SectionPhases_thisline2]
                api_node.phases = PotentialNodePhases[index]

                ########### Creat Recorder in  Ditto##############################################

                recorderphases = list(PotentialNodePhases[index])

                api_recorder = Recorder(model)
                api_recorder.name = "recorder" + NodeID[i].lower()
                api_recorder.parent = NodeID[i].lower()
                api_recorder.property = "voltage_" + recorderphases[0] + "[kV]"
                api_recorder.file = "n" + NodeID[i] + ".csv"
                api_recorder.interval = 50

            i = i + 1

        ########### Converting Line into Ditto##############################################
        i = 0
        for obj in LineID:

            ## Exclude the line with regulators
            # ii=0
            LineFlag = 0
            # for obj in RegulatrorSectionId:
            #     if LineID[i]==RegulatrorSectionId[ii]:
            #         LineFlag=1
            #         break
            #     ii=ii+1

            ## Exclude the line with transformers
            # ii = 0
            # for obj in TransformerSectionId:
            #     if LineID[i] == TransformerSectionId[ii]:
            #         LineFlag = 1
            #         break
            #     ii = ii + 1

            if LineFlag == 0:
                #   if IsToEndOpen[i] ==0 and IsFromEndOpen[i]==0:
                api_line = Line(model)
                api_line.name = LineID[i].lower()
                api_line.length = LineLength[i]
                api_line.from_element = FromNodeId[i].lower()
                api_line.to_element = ToNodeId[i].lower()

                ### Line Phases##################
                SectionPhases_thisline = list(SectionPhases[i])
                SectionPhases_thisline1 = [
                    s.encode("ascii") for s in SectionPhases_thisline
                ]
                SectionPhases_thisline2 = filter(str.strip, SectionPhases_thisline1)

                SectionPhases_thisline = [
                    s.decode("utf-8") for s in SectionPhases_thisline2
                ]
                NPhase = len(SectionPhases_thisline)

                ## The wires belong to this line
                t = 0
                wires = []
                for obj in SectionPhases_thisline:
                    api_wire = Wire(model)
                    api_wire.phase = SectionPhases_thisline[t]
                    wires.append(api_wire)
                    t = t + 1

                ## Calculating the impedance matrix of this line

                PhaseConductorIDthisline = PhaseConductorID[i]

                tt = 0
                Count = 0
                for obj in ConductorName:
                    Flag = PhaseConductorIDthisline == ConductorName[tt]
                    if Flag == True:
                        Count = tt
                    tt = tt + 1

                r1 = PosSequenceResistance_PerLUL[Count]
                x1 = PosSequenceReactance_PerLUL[Count]
                r0 = ZeroSequenceResistance_PerLUL[Count]
                x0 = ZeroSequenceReactance_PerLUL[Count]

                # In this case, we build the impedance matrix from Z+ and Z0 in the following way:
                #         __________________________
                #        | Z0+2*Z+  Z0-Z+   Z0-Z+   |
                # Z= 1/3 | Z0-Z+    Z0+2*Z+ Z0-Z+   |
                #        | Z0-Z+    Z0-Z+   Z0+2*Z+ |
                #         --------------------------

                coeff = 10 ** -3
                if NPhase == 2:
                    impedance_matrix = [[coeff * complex(float(r0), float(x0))]]
                if NPhase == 3:

                    b1 = float(r0) - float(r1)
                    b2 = float(x0) - float(x1)

                    if b1 < 0:
                        b1 = -b1
                    if b1 == 0:
                        b1 = float(r1)
                    if b2 < 0:
                        b2 = -b2
                    if b2 == 0:
                        b2 = float(x1)

                    b = coeff * complex(b1, b2)

                    a = coeff * complex(
                        (2 * float(r1) + float(r0)), (2 * float(x1) + float(x0))
                    )

                    impedance_matrix = [[a, b], [b, a]]

                if NPhase == 4:
                    a = coeff * complex(
                        (2 * float(r1) + float(r0)), (2 * float(x1) + float(x0))
                    )
                    b1 = float(r0) - float(r1)
                    b2 = float(x0) - float(x1)

                    if b1 < 0:
                        b1 = -b1
                    if b1 == 0:
                        b1 = float(r1)
                    if b2 < 0:
                        b2 = -b2
                    if b2 == 0:
                        b2 = float(x1)

                    b = coeff * complex(b1, b2)

                    impedance_matrix = [[a, b, b], [b, a, b], [b, b, a]]

                api_line.wires = wires
                api_line.impedance_matrix = impedance_matrix
            i = i + 1

        ######### Converting transformer  into Ditto###############
        #         i=0
        #         for obj in TransformerId:
        #
        #             api_transformer=PowerTransformer(model)
        #             api_transformer.name=TransformerId[i]
        #
        #             TransformerTypethisone = TransformerType[i]
        #             TransformerSectionIdthisone=TransformerSectionId[i]
        #
        #             TransformerTypethisone01 = TransformerTypethisone.encode('ascii')
        #             TransformerSectionIdthisone01 = TransformerSectionIdthisone.encode('ascii')
        #
        #
        #             # Find out the from and to elements
        #             tt = 0
        #             Count = 0
        #             for obj in LineID:
        #                 Flag = (TransformerSectionId[i] == LineID[tt])
        #                 if Flag == True:
        #                     Count = tt
        #                 tt = tt + 1
        #             api_transformer.to_element = ToNodeId[Count]
        #             api_transformer.from_element = FromNodeId[Count]
        #
        #             ## Phase of the transformer
        #             api_transformer.phases = SectionPhases[Count]
        #
        #             tt = 0
        #             Count = 0
        #             for obj in TransformerTypesinStock:
        #                 Flag = (TransformerType[i] == TransformerTypesinStock[tt])
        #                 if Flag == True:
        #                     Count = tt
        #                 tt=tt+1
        #
        #             TransformerRatedKvathisone=TransformerRatedKva[Count]
        #             api_transformer.powerrating=TransformerRatedKvathisone*1000
        #             api_transformer.primaryvoltage=HighSideRatedKv[Count]*1000
        #             api_transformer.secondaryvoltage=LowSideRatedKv[Count]*1000
        #
        #
        #             HighSideRatedKvthisone = HighSideRatedKv[Count]
        #             PercentImpedancethisone = PercentImpedance[Count]
        #             PercentResistancethisone = PercentResistance[Count]
        #
        #             ## Calculate the impedance of this transformer
        #             Resistancethisone = (HighSideRatedKvthisone ** 2/TransformerRatedKvathisone*1000)*PercentResistancethisone/100
        #             Reactancethisone = (HighSideRatedKvthisone ** 2 / TransformerRatedKvathisone * 1000) * (PercentImpedancethisone-PercentResistancethisone)/100
        #
        #             transformerimpedance=complex(Resistancethisone, Reactancethisone)
        # #            api_transformer.impedance=repr(transformerimpedance)[1:-1]
        #             api_transformer.impedance = transformerimpedance
        #
        #             ## Connection type of the transformer
        #             api_transformer.connectiontype = HighVoltageConnectionCode[Count]+LowVoltageConnectionCode[Count]
        #
        #             i=i+1
        ######### Convert load into Ditto ##############
        N = len(LoadName)
        i = 0
        for obj in LoadName:
            api_load = Load(model)
            api_load.name = "Load" + LoadName[i]

            tt = 0
            Count = 0
            for obj in LineID:
                Flag = LoadName[i] == LineID[tt]
                if Flag == True:
                    Count = tt
                tt = tt + 1

            api_load.connecting_element = ToNodeId[Count].lower()

            ## Load at each phase
            PLoad = [Phase1Kw[i], Phase2Kw[i], Phase3Kw[i]]
            PLoad1 = []
            for obj in PLoad:
                PLoad1.append(obj * 1000)
            QLoad = [Phase1Kvar[i], Phase2Kvar[i], Phase3Kvar[i]]
            QLoad1 = []
            for obj in QLoad:
                QLoad1.append(obj * 1000)
            t = 0
            loads = []
            PhasesthisLoad = ["A", "B", "C"]
            for obj in PhasesthisLoad:
                phase_loads = PhaseLoad(model)
                phase_loads.phase = PhasesthisLoad[t]
                phase_loads.p = PLoad1[t]
                phase_loads.q = QLoad1[t]
                loads.append(phase_loads)
                t = t + 1
            api_load.phase_loads = loads
            i = i + 1

        ####### Convert the capacitor data into Ditto ##########

        i = 0
        for obj in CapacitorName:
            api_cap = Capacitor(model)
            api_cap.name = CapacitorName[i]
            api_cap.nominal_voltage = CapacitorVoltage[i] * 1000
            api_cap.connection_type = CapacitorConnectionType[i]
            api_cap.delay = CapacitorTimeDelaySec[i]
            api_cap.mode = "VOLT"
            api_cap.low = CapacitorModule1CapSwitchCloseValue[i]
            api_cap.high = CapacitorModule1CapSwitchTripValue[i]
            api_cap.pt_ratio = CapacitorPTRatio[i]
            api_cap.ct_ratio = CapacitorCTRating[i]

            ## Find out the connecting bus
            tt = 0
            Count = 0
            for obj in LineID:
                Flag = CapacitorSectionId[i] == LineID[tt]
                if Flag == True:
                    Count = tt
                tt = tt + 1

            api_cap.connecting_element = ToNodeId[Count]

            QCap = [
                float(CapacitorFixedKvarPhase1[i]),
                float(CapacitorFixedKvarPhase2[i]),
                float(CapacitorFixedKvarPhase3[i]),
            ]

            t = 0
            Caps = []
            PhasesthisCap = ["A", "B", "C"]
            for obj in PhasesthisCap:
                phase_caps = PhaseCapacitor(model)
                phase_caps.phase = PhasesthisCap[t]
                phase_caps.var = QCap[t] * 1000
                Caps.append(phase_caps)
                t = t + 1
            api_cap.phase_capacitors = Caps

            i = i + 1

        ########## Convert regulator into Ditto #########
        # i = 0
        # for obj in RegulatorId:
        #     api_regulator = Regulator(model)
        #     api_regulator.name = RegulatorId[i]
        #     api_regulator.delay= RegulatorTimeDelay[i]
        #     api_regulator.highstep = int(RegulatorTapLimiterHighSetting[i])
        #     api_regulator.lowstep=-int(RegulatorTapLimiterLowSetting[i])
        #
        #     ## Regulator phases
        #     RegulagorPhases_this = list(RegulagorPhases[i])
        #     RegulagorPhases_this01 = [s.encode('ascii') for s in RegulagorPhases_this]
        #     RegulagorPhases_this02 = filter(str.strip, RegulagorPhases_this01)
        #     api_regulator.phases=''.join(RegulagorPhases_this02)
        #     #api_regulator.pt_phase=RegulagorPhases[i]
        #
        #     Flag=(RegulagorPhases[i]=='A')
        #     if Flag==True:
        #         api_regulator.bandwidth = RegulatrorForwardBWDialPhase1[i]
        #         api_regulator.bandcenter = RegulatrorForwardVoltageSettingPhase1[i]
        #
        #     Flag = (RegulagorPhases[i] == 'B')
        #     if Flag == True:
        #         api_regulator.bandwidth = RegulatrorForwardBWDialPhase2[i]
        #         api_regulator.bandcenter = RegulatrorForwardVoltageSettingPhase2[i]
        #
        #     Flag = (RegulagorPhases[i] == 'C')
        #     if Flag == True:
        #         api_regulator.bandwidth = RegulatrorForwardBWDialPhase3[i]
        #         api_regulator.bandcenter = RegulatrorForwardVoltageSettingPhase3[i]
        #
        #     RegulatorTypethisone=RegulatorTypes[i]
        #
        #     ## Find out pt ratio and ct rating
        #     tt = 0
        #     Count = 0
        #     for obj in RegulatrorNames :
        #         Flag = (RegulatorTypethisone == RegulatrorNames[tt])
        #         if Flag == True:
        #             Count = tt
        #         tt = tt + 1
        #
        #     api_regulator.pt_ratio=RegulatorPTRatio[Count]
        #     api_regulator.ct_ratio=RegulatorCTRating[Count]
        #
        #
        #     ## Find out the from and to elements
        #     tt = 0
        #     Count = 0
        #     for obj in LineID:
        #         Flag = (RegulatrorSectionId[i] == LineID[tt])
        #         if Flag == True:
        #             Count = tt
        #         tt = tt + 1
        #
        #     if RegulatorNearFromNode[i]==0:
        #         RegualatorFromNodeID=ToNodeId[Count]+'_1'
        #         RegualatorToNodeID = ToNodeId[Count]
        #         DummyNodeID=ToNodeId[Count]+'_1'
        #
        #     if RegulatorNearFromNode[i]==1:
        #         RegualatorFromNodeID = FromNodeId[Count]
        #         RegualatorToNodeID = FromNodeId[Count]+'_1'
        #         DummyNodeID = FromNodeId[Count]+'_1'
        #
        #     api_regulator.from_element = RegualatorFromNodeID
        #     api_regulator.to_element = RegualatorToNodeID
        #
        #     ## Create the dummy node connecting the regulators
        #     api_node = Node(model)
        #     api_node.name = DummyNodeID
        #     api_node.phases=SectionPhases01[Count]
        #
        #
        #     ## Create a line to put regulator in lines
        #     api_line = Line(model)
        #     api_line.name = LineID[Count]
        #     api_line.length = LineLength[Count] * 0.3048
        #     api_line.from_element = FromNodeId[Count]
        #     api_line.to_element = ToNodeId[Count]
        #
        #     ### Line Phases##################
        #     SectionPhases_thisline = SectionPhases01[Count]
        #     NPhase = len(SectionPhases_thisline)
        #
        #     ## The wires belong to this line
        #     t = 0
        #     wires = []
        #     for obj in SectionPhases_thisline:
        #         api_wire = Wire(model)
        #         api_wire.phase = SectionPhases_thisline[t]
        #         wires.append(api_wire)
        #         t = t + 1
        #
        #     ## Calculating the impedance matrix of this line
        #
        #     PhaseConductorIDthisline = PhaseConductorID[Count]
        #
        #     tt = 0
        #     Count_Conductor = 0
        #     for obj in ConductorName:
        #         Flag = (PhaseConductorIDthisline == ConductorName[tt])
        #         if Flag == True:
        #             Count_Conductor = tt
        #         tt = tt + 1
        #
        #     r1 = PosSequenceResistance_PerLUL[Count_Conductor]
        #     x1 = PosSequenceReactance_PerLUL[Count_Conductor]
        #     r0 = ZeroSequenceResistance_PerLUL[Count_Conductor]
        #     x0 = ZeroSequenceReactance_PerLUL[Count_Conductor]
        #
        #     coeff = 10 ** -3
        #     if NPhase == 2:
        #         impedance_matrix = [[coeff * complex(float(r0), float(x0))]]
        #     if NPhase == 3:
        #         a = coeff * complex(2 * float(r1) + float(r0),
        #                             2 * float(x1) + float(x0))
        #
        #         b1 = float(r0) - float(r1)
        #         b2 = float(x0) - float(x1)
        #
        #         if b1 < 0:
        #             b1 = -b1
        #         if b1 == 0:
        #             b1 = float(r1)
        #         if b2 < 0:
        #             b2 = -b2
        #         if b2 == 0:
        #             b2 = float(x1)
        #
        #         b = coeff * complex(b1, b2)
        #         impedance_matrix = [[a, b], [b, a]]
        #
        #     if NPhase == 4:
        #         a = coeff * complex(2 * float(r1) + float(r0),
        #                             2 * float(x1) + float(x0))
        #
        #         b1 = float(r0) - float(r1)
        #         b2 = float(x0) - float(x1)
        #
        #         if b1 < 0:
        #             b1 = -b1
        #         if b1 == 0:
        #             b1 = float(r1)
        #         if b2 < 0:
        #             b2 = -b2
        #         if b2 == 0:
        #             b2 = float(x1)
        #
        #         b = coeff * complex(b1, b2)
        #
        #         impedance_matrix = [[a, b, b], [b, a, b], [b, b, a]]
        #
        #     api_line.wires = wires
        #     api_line.impedance_matrix = impedance_matrix
        #     i = i + 1

        ##### Convert PV to Ditto###################################

        i = 0
        for obj in PVUniqueDeviceId:
            Flag = PVGenType[i] == "PhotoVoltaic"
            if Flag == True:
                api_PV = PowerSource(model)
                api_PV.name = PVUniqueDeviceId[i]
                if PVGenPhase1Kw[i] != 0:
                    api_PV.phases = ["A"]
                    api_PV.rated_power = PVGenPhase1Kw[i]
                if PVGenPhase1Kw[i] != 0:
                    api_PV.phases = ["B"]
                    api_PV.rated_power = PVGenPhase2Kw[i]
                if PVGenPhase1Kw[i] != 0:
                    api_PV.phases = ["C"]
                    api_PV.rated_power = PVGenPhase3Kw[i]
            ## Find out the from and to elements
            tt = 0
            Count = 0
            for obj in LineID:
                Flag = PVSectionId[i] == LineID[tt]
                if Flag == True:
                    Count = tt
                tt = tt + 1
            api_PV.connecting_element = ToNodeId[Count]
