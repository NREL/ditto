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
from ditto.models.photovoltaic import Photovoltaic
from ditto.models.position import Position
from ditto.models.base import Unicode

from ditto.readers.synergi.length_units import convert_length_unit, SynergiValueType

logger = logging.getLogger(__name__)


def create_mapping(keys, values, remove_spaces=False):
    """
    Helper function for parse.
    Creates a mapping using given keys and values.
    """
    if len(keys) != len(values):
        raise ValueError(
            "create_mapping expects keys and values to have the same length."
        )
    if len(keys) != len(np.unique(keys)):
        raise ValueError("create_mapping expects unique keys.")
    if remove_spaces:
        return {k: v.replace(" ", "_") for k, v in zip(keys, values)}
    else:
        return {k: v for k, v in zip(keys, values)}


class Reader(AbstractReader):
    """
    Synergi Reader class.

    **Usage:**
    - With only one MDB database holding everything:
        >>> r = Reader(input_file="path_to_your_mdb_file")
        >>> r.parse(m)

    - With an additional MDB database for the Warehouse:
        >>> r = Reader(input_file="path_to_your_mdb_file", warehouse="path_to_your_warehouse_mdb_file")
        >>> r.parse(m)

    **Authors:**
    - Xiangqi Zhu
    - Nicolas Gensollen
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

        # Can provide a ware house database seperated from the main database
        if "warehouse" in kwargs:
            self.ware_house_input_file = kwargs["warehouse"]
        else:
            self.ware_house_input_file = "warehouse.mdb"

        self.SynergiData = None

    def get_data(self, key1, key2):
        """
        Helper function for parse.

        **Inputs:**
        - key1: <string>. Name of the table.
        - key2: <string>. Name of the column.

        **Output:**
        None but update the SynergiData.SynergiDictionary attribute of the Reader.
        """
        if (
            key1 in self.SynergiData.SynergiDictionary
            and key2 in self.SynergiData.SynergiDictionary[key1]
        ):
            return self.SynergiData.SynergiDictionary[key1][key2]
        else:
            print("Could not retrieve data for <{k1}><{k2}>.".format(k1=key1, k2=key2))
            return None

    def parse(self, model):
        """
        Synergi --> DiTTo parse method.
        """
        if self.ware_house_input_file is not None:
            self.ware_house_input_file = os.path.join(
                os.path.dirname(self.input_file), self.ware_house_input_file
            )
            self.SynergiData = DbParser(
                self.input_file, warehouse=self.ware_house_input_file
            )
        else:
            self.SynergiData = DbParser(self.input_file)

        ####################################################################################
        ####################################################################################
        ######                                                                        ######
        ######                         PARSING THE DATA                               ######
        ######                                                                        ######
        ####################################################################################
        ####################################################################################

        print("--> Parsing the data from the database...")

        ## Feeder ID ##########
        ## This is used to separate different feeders ##
        FeederId = self.get_data("InstFeeders", "FeederId")
        NominalKvll_src = self.get_data("InstFeeders", "NominalKvll")
        ConnectionType_src = self.get_data("InstFeeders", "ConnectionType")
        BusVoltageLevel = self.get_data("InstFeeders", "BusVoltageLevel")
        PosSequenceResistance_src = self.get_data(
            "InstFeeders", "PosSequenceResistance"
        )
        PosSequenceReactance_src = self.get_data("InstFeeders", "PosSequenceReactance")
        ZeroSequenceResistance_src = self.get_data(
            "InstFeeders", "ZeroSequenceResistance"
        )
        ZeroSequenceReactance_src = self.get_data(
            "InstFeeders", "ZeroSequenceReactance"
        )
        ByPhVoltDegPh1 = self.get_data("InstFeeders", "ByPhVoltDegPh1")

        ## Node ###########
        NodeID = self.get_data("Node", "NodeId")
        NodeX = self.get_data("Node", "X")
        NodeY = self.get_data("Node", "Y")

        ## Preferences ########
        LengthUnits = self.get_data("SAI_Equ_Control", "LengthUnits")
        if LengthUnits is not None and len(LengthUnits) == 1:
            LengthUnits = LengthUnits[0]

        ###### Transformer ##################
        TransformerId = self.get_data("InstPrimaryTransformers", "UniqueDeviceId")
        TransformerSectionId = self.get_data("InstPrimaryTransformers", "SectionId")
        TransformerType = self.get_data("InstPrimaryTransformers", "TransformerType")

        DTranId = self.get_data("InstDTrans", "DTranId")
        DTransformerSectionId = self.get_data("InstDTrans", "SectionId")
        HighSideConnCode = self.get_data("InstDTrans", "HighSideConnCode")
        LowSideConnCode = self.get_data("InstDTrans", "LowSideConnCode")
        ConnPhases = self.get_data("InstDTrans", "ConnPhases")

        ## Substration Transformers ##
        SubstationTransformerV = self.get_data(
            "InstSubstationTransformers", "NominalKvll"
        )

        ## Transformer Setting ##
        # import pdb;pdb.set_trace()
        TransformerTypesinStock = self.get_data("DevTransformers", "TransformerName")
        HighSideRatedKv = self.get_data("DevTransformers", "HighSideRatedKv")
        LowSideRatedKv = self.get_data("DevTransformers", "LowSideRatedKv")
        TransformerRatedKva = self.get_data("DevTransformers", "TransformerRatedKva")
        EmergencyKvaRating = self.get_data("DevTransformers", "EmergencyKvaRating")
        IsThreePhaseUnit = self.get_data("DevTransformers", "IsThreePhaseUnit")
        NoLoadLosses = self.get_data("DevTransformers", "NoLoadLosses")
        PTRatio = self.get_data("DevTransformers", "PTRatio")
        EnableTertiary = self.get_data("DevTransformers", "EnableTertiary")
        TertiaryKva = self.get_data("DevTransformers", "TertiaryKva")
        TertiaryRatedKv = self.get_data("DevTransformers", "TertiaryRatedKv")
        PercentImpedance = self.get_data("DevTransformers", "PercentImpedance")
        PercentResistance = self.get_data("DevTransformers", "PercentResistance")
        ConnectedPhases = self.get_data("InstPrimaryTransformers", "ConnectedPhases")

        # NOTE: When the same information is given in the database and in the warehouse,
        # both are stored and the priority will be given to the information from the
        # network over the one form the warehouse
        #
        # TODO: Check that this is indeed how Synergi works...
        #
        # High side connection code from network
        HighVoltageConnectionCode_N = self.get_data(
            "InstPrimaryTransformers", "HighSideConnectionCode"
        )
        # High side connection code from warehouse
        HighVoltageConnectionCode_W = self.get_data(
            "DevTransformers", "HighVoltageConnectionCode"
        )

        # Low side connection code from network
        LowVoltageConnectionCode_N = self.get_data(
            "InstPrimaryTransformers", "LowSideConnectionCode"
        )
        # Low side connection code from warehouse
        LowVoltageConnectionCode_W = self.get_data(
            "DevTransformers", "LowVoltageConnectionCode"
        )

        # Tertiary connection code from network
        TertConnectCode = self.get_data("InstPrimaryTransformers", "TertConnectCode")
        # Tertiary connection code from warehouse
        TertiaryConnectionCode = self.get_data(
            "DevTransformers", "TertiaryConnectionCode"
        )

        ########## Line #####################
        LineID = self.get_data("InstSection", "SectionId")
        # FeederId = self.get_data("InstSection", "FeederId")
        LineLength = self.get_data("InstSection", "SectionLength_MUL")
        LineHeight = self.get_data("InstSection", "AveHeightAboveGround_MUL")
        PhaseConductorID = self.get_data("InstSection", "PhaseConductorId")
        PhaseConductor2Id = self.get_data("InstSection", "PhaseConductor2Id")
        PhaseConductor3Id = self.get_data("InstSection", "PhaseConductor3Id")
        NeutralConductorID = self.get_data("InstSection", "NeutralConductorId")
        ConfigurationId = self.get_data("InstSection", "ConfigurationId")
        SectionPhases = self.get_data("InstSection", "SectionPhases")
        LineFeederId = self.get_data("InstSection", "FeederId")
        FromNodeId = self.get_data("InstSection", "FromNodeId")
        ToNodeId = self.get_data("InstSection", "ToNodeId")
        IsFromEndOpen = self.get_data("InstSection", "IsFromEndOpen")
        IsToEndOpen = self.get_data("InstSection", "IsToEndOpen")
        AmpRating = self.get_data("InstSection", "AmpRating")
        AveHeightAboveGround_MUL = self.get_data(
            "InstSection", "AveHeightAboveGround_MUL"
        )

        # Create mapping between section IDs and Feeder Ids
        self.section_feeder_mapping = create_mapping(
            LineID, LineFeederId, remove_spaces=True
        )

        self.section_phase_mapping = create_mapping(LineID, SectionPhases)

        self.section_from_to_mapping = {}
        for idx, section in enumerate(LineID):
            self.section_from_to_mapping[section] = (FromNodeId[idx], ToNodeId[idx])

        ## Reclosers #######
        recloser_sectionID = self.get_data("InstReclosers", "SectionId")
        recloser_deviceID = self.get_data("InstReclosers", "UniqueDeviceId")
        recloser_rating = self.get_data("InstReclosers", "AmpRating")
        RecloserIsOpen = self.get_data("InstReclosers", "RecloserIsOpen")
        recloser_interrupting_rating = self.get_data(
            "InstReclosers", "InterruptRatingAmps"
        )

        ## Switches ########
        switch_sectionID = self.get_data("InstSwitches", "SectionId")
        switch_deviceID = self.get_data("InstSwitches", "UniqueDeviceId")
        SwitchType = self.get_data("InstSwitches", "SwitchType")
        SwitchIsOpen = self.get_data("InstSwitches", "SwitchIsOpen")
        SwitchName = self.get_data("DevSwitches", "SwitchName")
        Switch_index_map = {}
        for i in range(len(SwitchName)):
            Switch_index_map[SwitchName[i]] = i

        ContinuousCurrentRating_switch = self.get_data(
            "DevSwitches", "ContinuousCurrentRating"
        )
        EmergencyCurrentRating_switch = self.get_data(
            "DevSwitches", "EmergencyCurrentRating"
        )

        ## Fuses #########
        fuse_sectionID = self.get_data("InstFuses", "SectionId")
        fuse_deviceID = self.get_data("InstFuses", "UniqueDeviceId")
        fuse_rating = self.get_data("InstFuses", "AmpRating")
        fuse_blow_rating = self.get_data("InstFuses", "CutoffAmps")
        fuse_connected_phases = self.get_data("InstFuses", "ConnectedPhases")
        fuse_is_open = self.get_data("InstFuses", "FuseIsOpen")

        ## Protective devices ############
        protective_device_sectionID = self.get_data(
            "InstProtectiveDevices", "SectionId"
        )
        protective_device_deviceID = self.get_data(
            "InstProtectiveDevices", "UniqueDeviceId"
        )
        protective_device_connected_phases = self.get_data(
            "InstProtectiveDevices", "ConnectedPhases"
        )
        ProtectiveDeviceTypeName = self.get_data(
            "DevProtectiveDevices", "ProtectiveDeviceTypeName"
        )
        ProtectiveDeviceType = self.get_data(
            "DevProtectiveDevices", "ProtectiveDeviceType"
        )
        protective_device_ContinuousCurrentRating = self.get_data(
            "DevProtectiveDevices", "ContinuousCurrentRating"
        )
        protective_device_EmergencyCurrentRating = self.get_data(
            "DevProtectiveDevices", "EmergencyCurrentRating"
        )
        protective_device_InterruptCurrentRating = self.get_data(
            "DevProtectiveDevices", "InterruptCurrentRating"
        )

        ## Configuration ########
        ConfigName = self.get_data("DevConfig", "ConfigName")
        Position1_X_MUL = self.get_data("DevConfig", "Position1_X_MUL")
        Position1_Y_MUL = self.get_data("DevConfig", "Position1_Y_MUL")
        Position2_X_MUL = self.get_data("DevConfig", "Position2_X_MUL")
        Position2_Y_MUL = self.get_data("DevConfig", "Position2_Y_MUL")
        Position3_X_MUL = self.get_data("DevConfig", "Position3_X_MUL")
        Position3_Y_MUL = self.get_data("DevConfig", "Position3_Y_MUL")
        Neutral_X_MUL = self.get_data("DevConfig", "Neutral_X_MUL")
        Neutral_Y_MUL = self.get_data("DevConfig", "Neutral_Y_MUL")

        config_mapping = {}
        for idx, conf in enumerate(ConfigName):
            config_mapping[conf] = {
                "Position1_X_MUL": Position1_X_MUL[idx],
                "Position1_Y_MUL": Position1_Y_MUL[idx],
                "Position2_X_MUL": Position2_X_MUL[idx],
                "Position2_Y_MUL": Position2_Y_MUL[idx],
                "Position3_X_MUL": Position3_X_MUL[idx],
                "Position3_Y_MUL": Position3_Y_MUL[idx],
                "Neutral_X_MUL": Neutral_X_MUL[idx],
                "Neutral_Y_MUL": Neutral_Y_MUL[idx],
            }

        ## Wires ###########
        CableGMR = self.get_data("DevConductors", "CableGMR_MUL")
        CableDiamConductor = self.get_data("DevConductors", "CableDiamConductor_SUL")
        CableResistance = self.get_data("DevConductors", "CableResistance_PerLUL")
        ConductorName = self.get_data("DevConductors", "ConductorName")
        PosSequenceResistance_PerLUL = self.get_data(
            "DevConductors", "PosSequenceResistance_PerLUL"
        )
        PosSequenceReactance_PerLUL = self.get_data(
            "DevConductors", "PosSequenceReactance_PerLUL"
        )
        ZeroSequenceResistance_PerLUL = self.get_data(
            "DevConductors", "ZeroSequenceResistance_PerLUL"
        )
        ZeroSequenceReactance_PerLUL = self.get_data(
            "DevConductors", "ZeroSequenceReactance_PerLUL"
        )
        ContinuousCurrentRating = self.get_data(
            "DevConductors", "ContinuousCurrentRating"
        )
        InterruptCurrentRating = self.get_data(
            "DevConductors", "InterruptCurrentRating"
        )

        ### Concentric Neutral Data ###
        CableConNeutStrandDiameter_SUL = self.get_data(
            "DevConductors", "CableConNeutStrandDiameter_SUL"
        )
        CableConNeutResistance_PerLUL = self.get_data(
            "DevConductors", "CableConNeutResistance_PerLUL"
        )
        CableConNeutStrandCount = self.get_data(
            "DevConductors", "CableConNeutStrandCount"
        )
        CableDiamOutside = self.get_data("DevConductors", "CableDiamOutside_SUL")
        CableDiamOverInsul = self.get_data("DevConductors", "CableDiamOverInsul_SUL")

        conductor_mapping = {}
        for idx, cond in enumerate(ConductorName):
            conductor_mapping[cond] = {
                "CableGMR": CableGMR[idx],
                "CableDiamConductor": CableDiamConductor[idx],
                "CableResistance": CableResistance[idx],
                "PosSequenceResistance_PerLUL": PosSequenceResistance_PerLUL[idx],
                "PosSequenceReactance_PerLUL": PosSequenceReactance_PerLUL[idx],
                "ZeroSequenceResistance_PerLUL": ZeroSequenceResistance_PerLUL[idx],
                "ZeroSequenceReactance_PerLUL": ZeroSequenceReactance_PerLUL[idx],
                "ContinuousCurrentRating": ContinuousCurrentRating[idx],
                "InterruptCurrentRating": InterruptCurrentRating[idx],
                "CableConNeutStrandDiameter_SUL": CableConNeutStrandDiameter_SUL[idx],
                "CableConNeutResistance_PerLUL": CableConNeutResistance_PerLUL[idx],
                "CableConNeutStrandCount": CableConNeutStrandCount[idx],
                "CableDiamOutside": CableDiamOutside[idx],
                "CableDiamOverInsul": CableDiamOverInsul[idx],
            }

        ## Loads #############
        LoadName = self.get_data("Loads", "SectionId")
        Phase1Kw = self.get_data("Loads", "Phase1Kw")
        Phase2Kw = self.get_data("Loads", "Phase2Kw")
        Phase3Kw = self.get_data("Loads", "Phase3Kw")
        Phase1Kvar = self.get_data("Loads", "Phase1Kvar")
        Phase2Kvar = self.get_data("Loads", "Phase2Kvar")
        Phase3Kvar = self.get_data("Loads", "Phase3Kvar")

        Phase1Kva = self.get_data("Loads", "Phase1Kva")
        Phase2Kva = self.get_data("Loads", "Phase2Kva")
        Phase3Kva = self.get_data("Loads", "Phase3Kva")

        ## Capacitors ################
        CapacitorSectionID = self.get_data("InstCapacitors", "SectionId")
        CapacitorName = self.get_data("InstCapacitors", "UniqueDeviceId")
        CapacitorVoltage = self.get_data("InstCapacitors", "RatedKv")
        CapacitorConnectionType = self.get_data("InstCapacitors", "ConnectionType")
        CapacitorTimeDelaySec = self.get_data("InstCapacitors", "TimeDelaySec")
        CapacitorPrimaryControlMode = self.get_data(
            "InstCapacitors", "PrimaryControlMode"
        )
        CapacitorModule1CapSwitchCloseValue = self.get_data(
            "InstCapacitors", "Module1CapSwitchCloseValue"
        )
        CapacitorModule1CapSwitchTripValue = self.get_data(
            "InstCapacitors", "Module1CapSwitchTripValue"
        )
        CapacitorPTRatio = self.get_data("InstCapacitors", "CapacitorPTRatio")
        CapacitorCTRating = self.get_data("InstCapacitors", "CapacitorCTRating")
        CapacitorSectionId = self.get_data("InstCapacitors", "SectionId")
        CapacitorFixedKvarPhase1 = self.get_data("InstCapacitors", "FixedKvarPhase1")
        CapacitorFixedKvarPhase2 = self.get_data("InstCapacitors", "FixedKvarPhase2")
        CapacitorFixedKvarPhase3 = self.get_data("InstCapacitors", "FixedKvarPhase3")
        MeteringPhase = self.get_data("InstCapacitors", "MeteringPhase")
        CapacitorConnectedPhases = self.get_data("InstCapacitors", "ConnectedPhases")

        ## Regulators ###################
        RegulatorId = self.get_data("InstRegulators", "UniqueDeviceId")
        RegulatorTimeDelay = self.get_data("InstRegulators", "TimeDelaySec")
        RegulatorTapLimiterHighSetting = self.get_data(
            "InstRegulators", "TapLimiterHighSetting"
        )
        RegulatorTapLimiterLowSetting = self.get_data(
            "InstRegulators", "TapLimiterLowSetting"
        )
        RegulatorTapLimiterLowSetting = self.get_data(
            "InstRegulators", "TapLimiterLowSetting"
        )
        RegulatrorForwardBWDialPhase1 = self.get_data(
            "InstRegulators", "ForwardBWDialPhase1"
        )
        RegulatrorForwardBWDialPhase2 = self.get_data(
            "InstRegulators", "ForwardBWDialPhase2"
        )
        RegulatrorForwardBWDialPhase3 = self.get_data(
            "InstRegulators", "ForwardBWDialPhase3"
        )
        RegulatrorForwardVoltageSettingPhase1 = self.get_data(
            "InstRegulators", "ForwardVoltageSettingPhase1"
        )
        RegulatrorForwardVoltageSettingPhase1 = self.get_data(
            "InstRegulators", "ForwardVoltageSettingPhase1"
        )
        RegulatrorForwardVoltageSettingPhase2 = self.get_data(
            "InstRegulators", "ForwardVoltageSettingPhase2"
        )
        RegulatrorForwardVoltageSettingPhase3 = self.get_data(
            "InstRegulators", "ForwardVoltageSettingPhase3"
        )
        RegulatorSectionId = self.get_data("InstRegulators", "SectionId")
        RegulagorPhases = self.get_data("InstRegulators", "ConnectedPhases")
        RegulatorTypes = self.get_data("InstRegulators", "RegulatorType")
        RegulatorNames = self.get_data("DevRegulators", "RegulatorName")
        RegulatorPTRatio = self.get_data("DevRegulators", "PTRatio")
        RegulatorCTRating = self.get_data("DevRegulators", "CTRating")
        RegulatorNearFromNode = self.get_data("InstRegulators", "NearFromNode")

        RegulatorRatedVoltage = self.get_data("DevRegulators", "RegulatorRatedVoltage")
        RegulatorRatedKva = self.get_data("DevRegulators", "RegulatorRatedKva")
        RegulatorNoLoadLosses = self.get_data("DevRegulators", "NoLoadLosses")
        RegulatorConnectionCode = self.get_data("DevRegulators", "ConnectionCode")

        ##### PV ##################################
        PVUniqueDeviceId = self.get_data("InstLargeCust", "UniqueDeviceId")
        PVSectionId = self.get_data("InstLargeCust", "SectionId")
        PVGenType = self.get_data("InstLargeCust", "GenType")
        PVGenPhase1Kw = self.get_data("InstLargeCust", "GenPhase1Kw")
        PVGenPhase2Kw = self.get_data("InstLargeCust", "GenPhase2Kw")
        PVGenPhase3Kw = self.get_data("InstLargeCust", "GenPhase3Kw")
        PVGenPhase1Kvar = self.get_data("InstLargeCust", "GenPhase1Kvar")
        PVGenPhase2Kvar = self.get_data("InstLargeCust", "GenPhase2Kvar")
        PVGenPhase3Kvar = self.get_data("InstLargeCust", "GenPhase3Kvar")

        ## Generators ###############################
        GeneratorSectionID = self.get_data("InstGenerators", "SectionId")
        GeneratorID = self.get_data("InstGenerators", "UniqueDeviceId")
        GeneratorConnectedPhases = self.get_data("InstGenerators", "ConnectedPhases")
        GeneratorMeteringPhase = self.get_data("InstGenerators", "MeteringPhase")
        GeneratorType = self.get_data("InstGenerators", "GeneratorType")
        GeneratorVoltageSetting = self.get_data("InstGenerators", "VoltageSetting")
        GeneratorPF = self.get_data("InstGenerators", "PQPowerFactorPercentage")
        GenPhase1Kw = self.get_data("InstGenerators", "GenPhase1Kw")
        GenPhase1Kvar = self.get_data("InstGenerators", "GenPhase1Kvar")
        GenPhase2Kw = self.get_data("InstGenerators", "GenPhase2Kw")
        GenPhase2Kvar = self.get_data("InstGenerators", "GenPhase2Kvar")
        GenPhase3Kw = self.get_data("InstGenerators", "GenPhase3Kw")
        GenPhase3Kvar = self.get_data("InstGenerators", "GenPhase3Kvar")

        GeneratorName = self.get_data("DevGenerators", "GeneratorName")
        GeneratorTypeDev = self.get_data("DevGenerators", "GeneratorType")
        GeneratorKvRating = self.get_data("DevGenerators", "KvRating")
        GeneratorKwRating = self.get_data("DevGenerators", "KwRating")
        GeneratorPercentPFRating = self.get_data("DevGenerators", "PercentPFRating")

        ####################################################################################
        ####################################################################################
        ######                                                                        ######
        ######                       CONVERTING TO DITTO                              ######
        ######                                                                        ######
        ####################################################################################
        ####################################################################################

        print("--> Converting to DiTTo objects...")

        ####################################################################################
        #                                                                                  #
        #                                   SOURCES                                        #
        #                                                                                  #
        ####################################################################################
        #
        print("--> Parsing Sources...")
        for i, obj in enumerate(FeederId):

            # Create a DiTTo PowerSource object
            api_source = PowerSource(model)

            # Set the name
            api_source.name = obj.lower().replace(" ", "_") + "_src"

            # Set the nominal voltage
            api_source.nominal_voltage = NominalKvll_src[i] * 10 ** 3  # DiTTo in volts

            # Set the per unit
            api_source.per_unit = (
                BusVoltageLevel[i] / 120.0
            )  # This value should already be in volts

            # Set the phases
            # TODO: Change this. I couln't find where this is defined
            api_source.phases.append("A")
            api_source.phases.append("B")
            api_source.phases.append("C")

            # Set the sourcebus flag to True
            api_source.is_sourcebus = 1

            # Set the connection type
            api_source.connection_type = ConnectionType_src[i][:1]

            # Set the angle of the first phase
            api_source.phase_angle = ByPhVoltDegPh1[i]

            # Set the positive sequence impedance of the source
            api_source.positive_sequence_impedance = complex(
                PosSequenceResistance_src[i], PosSequenceReactance_src[i]
            )

            # Set the zero sequence impedance of the source
            api_source.zero_sequence_impedance = complex(
                ZeroSequenceResistance_src[i], ZeroSequenceReactance_src[i]
            )

            # Set the connecting element of the source
            api_source.connecting_element = obj.lower().replace(" ", "_")

        ####################################################################################
        #                                                                                  #
        #                                     NODES                                        #
        #                                                                                  #
        ####################################################################################
        #
        print("--> Parsing Nodes...")
        for i, obj in enumerate(NodeID):

            # Create a DiTTo Node object
            api_node = Node(model)

            # Set the name
            api_node.name = obj.lower().replace(" ", "_")

            # Set the feeder name if in mapping
            if obj in self.section_feeder_mapping:
                api_node.feeder_name = self.section_feeder_mapping[obj]

            # Set the Position of the Node
            # Create a Position object
            #
            pos = Position(model)

            # Set the coordinates
            pos.long = NodeY[i]
            pos.lat = NodeX[i]

            # Add the Position to the node's positions
            api_node.positions.append(pos)

            # Look for the phases at this node
            phases = set()
            for section, t in self.section_from_to_mapping.items():
                if obj == t[0] or obj == t[1]:
                    phases.add(self.section_phase_mapping[section])

            # Convert to a list and sort to have the phases in the A, B, C order
            phases = sorted(list(phases))

            # Set the phases for this node.
            for phase in phases:
                api_node.phases.append(phase)

        ####################################################################################
        #                                                                                  #
        #                                     LINES                                        #
        #                                                                                  #
        ####################################################################################
        #
        print("--> Parsing Lines...")
        for i, obj in enumerate(LineID):

            ## Do not parse sections with regulators or Transformers to Lines
            if obj in RegulatorSectionId or obj in TransformerSectionId:
                continue

            # Create a DiTTo Line object
            api_line = Line(model)

            # Set the name as the SectionID
            # Since this could contain spaces, replace them with "_"
            #
            api_line.name = obj.lower().replace(" ", "_")

            # Set the feeder_name if it exists in the mapping
            if obj in self.section_feeder_mapping:
                api_line.feeder_name = self.section_feeder_mapping[obj]

            # Cache configuration
            if ConfigurationId is not None:
                if (
                    isinstance(ConfigurationId[i], str)
                    and len(ConfigurationId[i]) > 0
                    and ConfigurationId[i] in config_mapping
                ):
                    config = config_mapping[ConfigurationId[i]]
                else:
                    config = {}

            # Assumes MUL is medium unit length and this is feets
            # Converts to meters then
            #
            api_line.length = convert_length_unit(
                LineLength[i], SynergiValueType.MUL, LengthUnits
            )
            if LineHeight[i] < 0:
                api_line.line_type = "underground"
            else:
                api_line.line_type = "overhead"

            # From element
            # Replace spaces with "_"
            #
            api_line.from_element = FromNodeId[i].lower().replace(" ", "_")

            # To element
            # Replace spaces with "_"
            #
            api_line.to_element = ToNodeId[i].lower().replace(" ", "_")

            # Switching devices and network protection devices
            # Set ratings to Nones
            #
            eqt_rating = None
            eqt_interrupting_rating = None
            eqt_open = None

            # Recloser
            if recloser_sectionID is not None and obj in recloser_sectionID.values:
                idd = np.argwhere(recloser_sectionID.values == obj).flatten()

                # Set the is_recloser flag to True
                api_line.is_recloser = 1

                # Get the interrupting rating (to be used in the wires)
                if len(idd) == 1:
                    eqt_interrupting_rating = recloser_interrupting_rating[idd[0]]
                    eqt_rating = recloser_rating[idd[0]]
                    eqt_open = RecloserIsOpen[idd[0]]

            # Switch
            if switch_sectionID is not None and obj in switch_sectionID.values:
                idd_db = np.argwhere(switch_sectionID.values == obj).flatten()

                # Set the is_switch flag to True
                api_line.is_switch = 1

                # Get the current ratings (to be used in the wires)
                if len(idd_db) == 1:
                    idd_warehouse = Switch_index_map[SwitchType[idd_db[0]]]
                    eqt_rating = ContinuousCurrentRating_switch[idd_warehouse]
                    eqt_interrupting_rating = EmergencyCurrentRating_switch[
                        idd_warehouse
                    ]
                    eqt_open = SwitchIsOpen[idd_db[0]]

            # Fuse
            if fuse_sectionID is not None and obj in fuse_sectionID.values:
                idd = np.argwhere(fuse_sectionID.values == obj).flatten()

                # Set the is_fuse flag to True
                api_line.is_fuse = 1

                # Get the current ratings (to be used in the wires)
                if len(idd) == 1:
                    eqt_rating = fuse_rating[idd[0]]
                    eqt_interrupting_rating = fuse_blow_rating[idd[0]]
                    eqt_open = fuse_is_open[idd[0]]

            # Protection Devices
            if (
                protective_device_sectionID is not None
                and obj in protective_device_sectionID.values
            ):
                idd = np.argwhere(protective_device_sectionID.values == obj).flatten()

                # Get the type of protector
                if len(idd) == 1:

                    if (
                        protective_device_deviceID[idd[0]]
                        in ProtectiveDeviceTypeName.values
                    ):
                        eqt_id = np.argwhere(
                            ProtectiveDeviceTypeName.values
                            == protective_device_deviceID[idd[0]]
                        ).flatten()

                        if len(eqt_id) == 1:

                            # Get the type
                            protect_type = ProtectiveDeviceType[eqt_id].lower()

                            # Try to map this type to one supported by DiTTo
                            if "fuse" in protect_type:
                                api_line.is_fuse = 1
                            elif "sectionalizer" in protect_type:
                                api_line.is_sectionalizer = 1
                            elif "breaker" in protect_type:
                                api_line.is_breaker = 1
                            elif "recloser" in protect_type:
                                api_line.is_recloser = 1
                            # If nothing more specific was found, map to a network protector
                            else:
                                api_line.is_network_protector = 1

                            eqt_rating = ContinuousCurrentRating[eqt_id]
                            eqt_interrupting_rating = InterruptCurrentRating[eqt_id]

            ### Line Phases##################
            #
            # Phases are given as a string "A B C N"
            # Convert this string to a list of characters
            #
            SectionPhases_thisline1 = list(SectionPhases[i])

            # Remove the spaces from the list
            SectionPhases_thisline = [s for s in SectionPhases_thisline1 if s != " "]

            # Get the number of phases as the length of this list
            # Warning: Neutral will be included in this number
            #
            NPhase = len(SectionPhases_thisline)

            ############################################################
            # BEGINING OF WIRES SECTION
            ############################################################

            # Create the Wire DiTTo objects
            for idx, phase in enumerate(SectionPhases_thisline):

                # Create a Wire DiTTo object
                api_wire = Wire(model)

                # Set the phase
                api_wire.phase = phase

                # Is_recloser
                if api_line.is_recloser == 1:

                    # Set the flag to True if the line has been identified as a Recloser
                    api_wire.is_recloser = 1

                    # Set the ampacity
                    api_wire.ampacity = float(
                        eqt_rating
                    )  # Value should already be in amps

                    # Set the interrupting rating
                    api_wire.emergency_ampacity = float(
                        eqt_interrupting_rating
                    )  # Value should already be in amps

                    api_wire.interrupting_rating = float(
                        eqt_interrupting_rating
                    )  # Value should already be in amps

                    # Set the is_open flag
                    api_wire.is_open = int(eqt_open)

                # Is_switch
                if api_line.is_switch == 1:

                    # Set the flag to True if the line has been identified as a Switch
                    api_wire.is_switch = 1

                    # Set the ampacity
                    api_wire.ampacity = float(
                        eqt_rating
                    )  # Value should already be in amps

                    # Set the emergency ampacity
                    api_wire.emergency_ampacity = float(
                        eqt_interrupting_rating
                    )  # Value should already be in amps

                    # Set the is_open flag
                    api_wire.is_open = int(eqt_open)

                # Is_fuse
                if api_line.is_fuse == 1:

                    # Set the flag to True if the line has been identified as a Fuse
                    api_wire.is_fuse = 1

                    # Set the ampacity
                    api_wire.ampacity = float(
                        eqt_rating
                    )  # Value should already be in amps

                    # Set the emergency ampacity
                    api_wire.emergency_ampacity = float(
                        eqt_interrupting_rating
                    )  # Value should already be in amps

                    # Set the interrupting_rating
                    api_wire.interrupting_rating = float(
                        eqt_interrupting_rating
                    )  # Value should already be in amps

                    # Set the is_open flag
                    api_wire.is_open = int(eqt_open)

                # Is_sectionalizer
                if api_line.is_sectionalizer == 1:

                    # Set the flag to True if the line has been identified as a sectionalizer
                    api_wire.is_sectionalizer = 1

                    # Set the ampacity
                    api_wire.ampacity = float(
                        eqt_rating
                    )  # Value should already be in amps

                    # Set the emergency ampacity
                    api_wire.emergency_ampacity = float(
                        eqt_interrupting_rating
                    )  # Value should already be in amps

                # Is_network_protector
                if api_line.is_network_protector == 1:

                    # Set the flag to True if the line has been identified as a network protector
                    api_wire.is_network_protector = 1

                    # Set the ampacity
                    api_wire.ampacity = float(
                        eqt_rating
                    )  # Value should already be in amps

                    # Set the emergency ampacity
                    api_wire.emergency_ampacity = float(
                        eqt_interrupting_rating
                    )  # Value should already be in amps

                # The Neutral will be handled seperately
                if phase != "N":
                    # Set the position of the first wire
                    if (
                        idx == 0
                        and phase != "N"
                        and "Position1_X_MUL" in config
                        and "Position1_Y_MUL" in config
                    ):
                        # Set X
                        api_wire.X = convert_length_unit(
                            config["Position1_X_MUL"], SynergiValueType.MUL, LengthUnits
                        )

                        # Set Y
                        # Add the reference height
                        api_wire.Y = convert_length_unit(
                            AveHeightAboveGround_MUL[i] + config["Position1_Y_MUL"],
                            SynergiValueType.MUL,
                            LengthUnits,
                        )

                    # Set the position of the second wire
                    if (
                        idx == 1
                        and phase != "N"
                        and "Position2_X_MUL" in config
                        and "Position2_Y_MUL" in config
                    ):
                        # Set X
                        api_wire.X = convert_length_unit(
                            config["Position2_X_MUL"], SynergiValueType.MUL, LengthUnits
                        )

                        # Set Y
                        # Add the reference height
                        api_wire.Y = convert_length_unit(
                            AveHeightAboveGround_MUL[i] + config["Position2_Y_MUL"],
                            SynergiValueType.MUL,
                            LengthUnits,
                        )

                    # Set the position of the third wire
                    if (
                        idx == 2
                        and phase != "N"
                        and "Position3_X_MUL" in config
                        and "Position3_Y_MUL" in config
                    ):
                        # Set X
                        api_wire.X = convert_length_unit(
                            config["Position3_X_MUL"], SynergiValueType.MUL, LengthUnits
                        )

                        # Set Y
                        # Add the reference height
                        api_wire.Y = convert_length_unit(
                            AveHeightAboveGround_MUL[i] + config["Position3_Y_MUL"],
                            SynergiValueType.MUL,
                            LengthUnits,
                        )

                    # Set the characteristics of the first wire. Use PhaseConductorID
                    #
                    # Cache the raw nameclass of the conductor in conductor_name_raw
                    # api_wire.nameclass needs to be cleaned from spaces
                    #
                    conductor_name_raw = None

                    if (
                        idx == 0
                        and PhaseConductorID is not None
                        and isinstance(PhaseConductorID[i], str)
                        and len(PhaseConductorID[i]) > 0
                    ):
                        # Set the Nameclass of the Wire
                        # The name can contain spaces. Replace them with "_"
                        #
                        api_wire.nameclass = PhaseConductorID[i].replace(" ", "_")

                        # Cache the conductor name
                        conductor_name_raw = PhaseConductorID[i]

                    # Set the characteristics of the second wire.
                    # If PhaseConductor2Id is provided, use it
                    # Otherwise, assume the phase wires are the same
                    #
                    if idx == 1:
                        if (
                            PhaseConductor2Id is not None
                            and isinstance(PhaseConductor2Id[i], str)
                            and len(PhaseConductor2Id[i]) > 0
                            and PhaseConductor2Id[i].lower() != "unknown"
                        ):
                            # Set the nameclass
                            # Replace spaces with "_"
                            #
                            api_wire.nameclass = PhaseConductor2Id[i].replace(" ", "_")

                            # Cache the conductor name
                            conductor_name_raw = PhaseConductor2Id[i]
                        else:
                            try:
                                api_wire.nameclass = PhaseConductorID[i].replace(
                                    " ", "_"
                                )
                                conductor_name_raw = PhaseConductorID[i]
                            except:
                                pass

                    # Set the characteristics of the third wire in the same way
                    if idx == 2:
                        if (
                            PhaseConductor3Id is not None
                            and isinstance(PhaseConductor3Id[i], str)
                            and len(PhaseConductor3Id[i]) > 0
                            and PhaseConductor3Id[i].lower() != "unknown"
                        ):
                            # Set the nameclass
                            # Replace spaces with "_"
                            #
                            api_wire.nameclass = PhaseConductor3Id[i].replace(" ", "_")

                            # Cache the conductor name
                            conductor_name_raw = PhaseConductor3Id[i]
                        else:
                            try:
                                api_wire.nameclass = PhaseConductorID[i].replace(
                                    " ", "_"
                                )
                                conductor_name_raw = PhaseConductorID[i]
                            except:
                                pass

                if phase == "N":
                    if (
                        NeutralConductorID is not None
                        and isinstance(NeutralConductorID[i], str)
                        and len(NeutralConductorID[i]) > 0
                    ):

                        # Set the nameclass
                        api_wire.nameclass = NeutralConductorID[i].replace(" ", "_")

                        # Cache the conductor name
                        conductor_name_raw = NeutralConductorID[i]

                    # Set the Spacing of the neutral
                    if "Neutral_X_MUL" in config and "Neutral_Y_MUL" in config:

                        # Set X
                        api_wire.X = convert_length_unit(
                            config["Neutral_X_MUL"], SynergiValueType.MUL, LengthUnits
                        )  # DiTTo is in meters

                        # Set Y
                        # Add the reference height
                        api_wire.Y = convert_length_unit(
                            AveHeightAboveGround_MUL[i] + config["Neutral_Y_MUL"],
                            SynergiValueType.MUL,
                            LengthUnits,
                        )

                # Set the characteristics of the wire:
                # - GMR
                # - Diameter
                # - Ampacity
                # - Emergency Ampacity
                # - Resistance
                #
                if (
                    conductor_name_raw is not None
                    and conductor_name_raw in conductor_mapping
                ):
                    # Set the GMR of the conductor
                    # DiTTo is in meters and GMR is assumed to be given in feets
                    #
                    api_wire.gmr = convert_length_unit(
                        conductor_mapping[conductor_name_raw]["CableGMR"],
                        SynergiValueType.MUL,
                        LengthUnits,
                    )

                    # Set the Diameter of the conductor
                    # Diameter is assumed to be given in inches and is converted to meters here
                    #
                    api_wire.diameter = convert_length_unit(
                        conductor_mapping[conductor_name_raw]["CableDiamConductor"],
                        SynergiValueType.SUL,
                        LengthUnits,
                    )

                    # Set the Ampacity of the conductor
                    #
                    # If ampacity is already set (if we have a switch for example), skip that
                    if api_wire.ampacity is None:
                        api_wire.ampacity = conductor_mapping[conductor_name_raw][
                            "ContinuousCurrentRating"
                        ]

                    # Set the Emergency ampacity of the conductor
                    #
                    # If emergency ampacity is already set (if we have a switch for example), skip that
                    if api_wire.emergency_ampacity is None:
                        api_wire.emergency_ampacity = conductor_mapping[
                            conductor_name_raw
                        ]["InterruptCurrentRating"]

                    # Set the resistance of the conductor
                    # Represented in Ohms per meter
                    #
                    if api_line.length is not None:
                        api_wire.resistance = convert_length_unit(
                            conductor_mapping[conductor_name_raw]["CableResistance"],
                            SynergiValueType.Per_LUL,
                            LengthUnits,
                        )

                    # Check outside diameter is greater than conductor diameter before applying concentric neutral settings
                    if (
                        conductor_mapping[conductor_name_raw]["CableDiamOutside"]
                        > conductor_mapping[conductor_name_raw]["CableDiamConductor"]
                    ):
                        api_wire.concentric_neutral_resistance = (
                            conductor_mapping[conductor_name_raw][
                                "CableConNeutResistance_PerLUL"
                            ]
                            / 160934
                        )
                        api_wire.concentric_neutral_diameter = (
                            conductor_mapping[conductor_name_raw][
                                "CableConNeutStrandDiameter_SUL"
                            ]
                            * 0.0254
                        )  # multiplied by short unit length scale
                        api_wire.concentric_neutral_gmr = (
                            conductor_mapping[conductor_name_raw][
                                "CableConNeutStrandDiameter_SUL"
                            ]
                            / 2.0
                            * 0.7788
                            * 0.0254
                        )  # multiplied by short unit length scale. Derived as 0.7788 * radius as per OpenDSS default
                        api_wire.concentric_neutral_outside_diameter = (
                            conductor_mapping[conductor_name_raw]["CableDiamOutside"]
                            * 0.0254
                        )  # multiplied by short unit length scale
                        api_wire.concentric_neutral_nstrand = int(
                            conductor_mapping[conductor_name_raw][
                                "CableConNeutStrandCount"
                            ]
                        )
                        api_wire.insulation_thickness = (
                            (
                                conductor_mapping[conductor_name_raw][
                                    "CableDiamOverInsul"
                                ]
                                - conductor_mapping[conductor_name_raw][
                                    "CableDiamConductor"
                                ]
                            )
                            / 2.0
                            * 0.0254
                        )

                # Add the new Wire to the line's list of wires
                #
                api_line.wires.append(api_wire)

                ############################################################
                # END OF WIRES SECTION
                ############################################################

            ## Calculating the impedance matrix of this line
            #
            # NOTE: If all information about the Wires, characteristics, and spacings are given,
            # using geometries is prefered. This information will be stored in DiTTo and when
            # writing out to another format, geometries will be used instead of linecodes if possible.
            # We still compute the impedance matrix in case this possibility does not exist in the output format

            # Use the Phase Conductor charateristics to build the matrix
            #
            Count = None
            impedance_matrix = None

            if ConductorName is not None:
                for k, cond_obj in enumerate(ConductorName):
                    if PhaseConductorID[i] == cond_obj:
                        Count = k
                        break

            # Get sequence impedances
            #
            if Count is not None:
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

                r0 = (
                    convert_length_unit(r0, SynergiValueType.Per_LUL, LengthUnits) / 3.0
                )
                r1 = (
                    convert_length_unit(r1, SynergiValueType.Per_LUL, LengthUnits) / 3.0
                )
                x0 = (
                    convert_length_unit(x0, SynergiValueType.Per_LUL, LengthUnits) / 3.0
                )
                x1 = (
                    convert_length_unit(x1, SynergiValueType.Per_LUL, LengthUnits) / 3.0
                )

                # One phase case (One phase + neutral)
                #
                if NPhase == 2:
                    impedance_matrix = [
                        [complex(float(r0) + float(r1), float(x0) + float(x1))]
                    ]

                # Two phase case (Two phases + neutral)
                #
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

                    b = complex(b1, b2)

                    a = complex(
                        (2 * float(r1) + float(r0)), (2 * float(x1) + float(x0))
                    )

                    impedance_matrix = [[a, b], [b, a]]

                # Three phases case (Three phases + neutral)
                #
                if NPhase == 4:
                    a = complex(
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

                    b = complex(b1, b2)

                    impedance_matrix = [[a, b, b], [b, a, b], [b, b, a]]

            if impedance_matrix is not None:
                api_line.impedance_matrix = impedance_matrix
            else:
                print("No impedance matrix for line {}".format(api_line.name))

        ####################################################################################
        #                                                                                  #
        #                              TRANSFORMERS                                        #
        #                                                                                  #
        ####################################################################################
        #
        print("--> Parsing Transformers...")
        for i, obj in enumerate(TransformerId):

            # Create a PowerTransformer object
            api_transformer = PowerTransformer(model)

            # Set the name
            # Names can have spaces. Replace them with "_"
            #
            api_transformer.name = obj.replace(" ", "_").lower()

            # Set the feeder_name if it is in the mapping

            if TransformerSectionId[i] in self.section_feeder_mapping:
                api_transformer.feeder_name = self.section_feeder_mapping[
                    TransformerSectionId[i]
                ]
            # If it is not, try to remove the "tran" prefix that might have been added
            else:
                cleaned_id = obj.replace("Tran", "").strip()
                if cleaned_id in self.section_feeder_mapping:
                    api_transformer.feeder_name = self.section_feeder_mapping[
                        cleaned_id
                    ]

            # Find out the from and to elements which are available in the sections
            Count = None
            for k, section in enumerate(LineID):
                if TransformerSectionId[i] == section:
                    Count = k
                    break

            # If no section found, print a warning
            if Count is None:
                print("WARNING: No section found for section {}".format(obj))

            # Set the To element
            if Count is not None:
                api_transformer.to_element = ToNodeId[Count].replace(" ", "_").lower()

            # Set the From element
            if Count is not None:
                api_transformer.from_element = (
                    FromNodeId[Count].replace(" ", "_").lower()
                )

            # Find the transformer equipment from the Warehouse
            Count = None
            if TransformerTypesinStock is not None:
                for k, trans_obj in enumerate(TransformerTypesinStock):
                    if TransformerType[i] == trans_obj:
                        Count = k
                        break

            # If no equipment found, print a warning
            if Count is None:
                print(
                    "WARNING: No transformer equipment found for section {}".format(obj)
                )

            if Count is not None:

                # Set the PT Ratio
                api_transformer.pt_ratio = PTRatio[Count]

                # Set the NoLoadLosses
                api_transformer.noload_loss = NoLoadLosses[Count]

                # Number of windings
                # TODO: IS THIS RIGHT???
                #
                if IsThreePhaseUnit[Count] == 1 and EnableTertiary[Count] == 1:
                    n_windings = 3
                else:
                    n_windings = 2

                # Get the phases
                phases = self.section_phase_mapping[TransformerSectionId[i]]

                ############################################################
                # BEGINING OF WINDING SECTION
                ############################################################
                for winding in range(n_windings):

                    # Create a new Winding object
                    w = Winding(model)

                    # Primary
                    if winding == 0:

                        # Set the Connection_type of the Winding
                        if (
                            HighVoltageConnectionCode_N is not None
                            and len(HighVoltageConnectionCode_N[i]) > 0
                        ):
                            w.connection_type = HighVoltageConnectionCode_N[i][:1]
                        elif HighVoltageConnectionCode_W is not None:
                            w.connection_type = HighVoltageConnectionCode_W[Count][:1]

                        # Set the Nominal voltage of the Winding
                        w.nominal_voltage = (
                            HighSideRatedKv[Count] * 10 ** 3
                        )  # DiTTo in volts

                    # Secondary
                    elif winding == 1:

                        # Set the Connection_type of the Winding
                        if (
                            LowVoltageConnectionCode_N is not None
                            and len(LowVoltageConnectionCode_N[i]) > 0
                        ):
                            w.connection_type = LowVoltageConnectionCode_N[i][:1]
                        elif LowVoltageConnectionCode_W is not None:
                            w.connection_type = LowVoltageConnectionCode_W[Count][:1]

                        # Set the Nominal voltage of the Winding
                        w.nominal_voltage = (
                            LowSideRatedKv[Count] * 10 ** 3
                        )  # DiTTo in volts

                    # Tertiary
                    elif winding == 2:

                        # Set the Connection_type of the Winding
                        if TertConnectCode is not None and len(TertConnectCode[i]) > 0:
                            w.connection_type = TertConnectCode[i][:1]
                        elif TertiaryConnectionCode is not None:
                            w.connection_type = TertiaryConnectionCode[Count][:1]

                        # Set the Nominal voltage of the Winding
                        w.nominal_voltage = (
                            TertiaryRatedKv[Count] * 10 ** 3
                        )  # DiTTo in volts

                    # Set the rated power
                    if winding == 0 or winding == 1:
                        w.rated_power = (
                            TransformerRatedKva[Count]
                            / float(n_windings)
                            * 10
                            ** 3  # TODO: Fix this once the KVA Bug in DiTTo is fixed!!
                        )  # DiTTo in Vars
                    elif winding == 2:
                        w.rated_power = (
                            TertiaryKva * 10 ** 3
                        )  # TODO: Check that this is correct...

                    # Set the emergency power
                    w.emergency_power = (
                        EmergencyKvaRating[Count]
                        / float(n_windings)
                        * 10 ** 3  # TODO: Fix this once the KVA Bug in DiTTo is fixed!!
                    )  # DiTTo in Vars

                    # Create the PhaseWindings
                    for phase in phases:
                        if phase != "N":
                            pw = PhaseWinding(model)
                            pw.phase = phase
                            w.phase_windings.append(pw)

                    # Append the Winding to the Transformer
                    api_transformer.windings.append(w)

        ####################################################################################
        #                                                                                  #
        #                                  LOADS                                           #
        #                                                                                  #
        ####################################################################################
        #
        print("--> Parsing Loads...")
        for i, obj in enumerate(LoadName):

            # Create a Load DiTTo object
            api_load = Load(model)

            # Set the name
            api_load.name = "Load_" + obj.replace(" ", "_").lower()

            # Set the feeder_name if in the mapping
            if obj in self.section_feeder_mapping:
                api_load.feeder_name = self.section_feeder_mapping[obj]

            # Fin the section for this load
            Count = None
            for k, section in enumerate(LineID):
                if obj == section:
                    Count = k
                    break

            # If no section found, print a warning
            if Count is None:
                print("WARNING: No section found for Load {}".format(obj))

            if Count is not None:

                # Set the connecting element
                api_load.connecting_element = ToNodeId[Count].lower().replace(" ", "_")

                # Set P and Q
                # Create a list for P and Q for each phase and convert to Watts and vars
                #

                PLoad = map(
                    lambda x: x * 10 ** 3, [Phase1Kw[i], Phase2Kw[i], Phase3Kw[i]]
                )

                QLoad = map(
                    lambda x: x * 10 ** 3, [Phase1Kvar[i], Phase2Kvar[i], Phase3Kvar[i]]
                )
                # if there is no load information in the kvar and kw, try to get information out from the kva information
                LoadPF = 0.95
                LoadQFactor = (1 - LoadPF ** 2) ** 0.5

                PLoadkva = map(
                    lambda x: x * 10 ** 3,
                    [
                        Phase1Kva[i] * LoadPF,
                        Phase2Kva[i] * LoadPF,
                        Phase3Kva[i] * LoadPF,
                    ],
                )

                QLoadkva = map(
                    lambda x: x * 10 ** 3,
                    [
                        Phase1Kvar[i] * LoadQFactor,
                        Phase2Kvar[i] * LoadQFactor,
                        Phase3Kvar[i] * LoadQFactor,
                    ],
                )

                # Set the Phase Loads
                for P, Q, Pkva, Qkva, phase in zip(
                    PLoad, QLoad, PLoadkva, QLoadkva, ["A", "B", "C"]
                ):

                    # Only create a PhaseLoad is P OR Q is not zero
                    if P != 0 or Q != 0:

                        # Create the PhaseLoad DiTTo object
                        phase_load = PhaseLoad(model)

                        # Set the Phase
                        phase_load.phase = phase

                        # Set P
                        phase_load.p = P

                        # Set Q
                        phase_load.q = Q

                        # Add the PhaseLoad to the list
                        api_load.phase_loads.append(phase_load)

                    elif Pkva != 0 or Qkva != 0:

                        # Create the PhaseLoad DiTTo object
                        phase_load = PhaseLoad(model)

                        # Set the Phase
                        phase_load.phase = phase

                        # Set P
                        phase_load.p = Pkva

                        # Set Q
                        phase_load.q = Qkva

                        # Add the PhaseLoad to the list
                        api_load.phase_loads.append(phase_load)

                    # else:
                    #
                    #     # if there is no load information, place a small load instead of writing zero to the load
                    #     phase_load = PhaseLoad(model)
                    #
                    #     # Set the Phase
                    #     phase_load.phase = phase
                    #
                    #     # Set P
                    #     phase_load.p = 0.01
                    #
                    #     # Set Q
                    #     phase_load.q = 0.01
                    #
                    #     # Add the PhaseLoad to the list
                    #     api_load.phase_loads.append(phase_load)

        ####################################################################################
        #                                                                                  #
        #                              CAPACITORS                                          #
        #                                                                                  #
        ####################################################################################
        #
        print("--> Parsing Capacitors...")
        for i, obj in enumerate(CapacitorName):

            # Create a Capacitor DiTTo object
            api_cap = Capacitor(model)

            # Set the name
            api_cap.name = obj.replace(" ", "_").lower()

            # Set the feeder_name if in the mapping
            if CapacitorSectionID[i] in self.section_feeder_mapping:
                api_cap.feeder_name = self.section_feeder_mapping[CapacitorSectionID[i]]

            # Maps control modes from Synergi format to DiTTo format
            # TODO: Complete the mapping with other control modes
            #
            control_mode_mapping = {"VOLTS": "voltage"}

            # Set the nominal voltage
            # Convert from KV to Volts since DiTTo is in volts
            api_cap.nominal_voltage = CapacitorVoltage[i] * 1000

            # Set the connection of the capacitor
            api_cap.connection_type = CapacitorConnectionType[i][:1]

            # Set the Delay of the capacitor
            api_cap.delay = CapacitorTimeDelaySec[i]

            # Set the control mode of the capacitor
            if CapacitorPrimaryControlMode[i] in control_mode_mapping:
                api_cap.mode = control_mode_mapping[CapacitorPrimaryControlMode[i]]
            # Default sets to voltage
            else:
                api_cap.mode = "voltage"

            # Set the Low Value
            api_cap.low = CapacitorModule1CapSwitchCloseValue[i]

            # Set the High Value
            api_cap.high = CapacitorModule1CapSwitchTripValue[i]

            # Set the PT ratio of the capacitor
            api_cap.pt_ratio = CapacitorPTRatio[i]

            # Set the CT ratio of the capacitor
            api_cap.ct_ratio = CapacitorCTRating[i]

            # Set the Measuring element
            api_cap.measuring_element = "Line." + CapacitorSectionID[i].lower()

            # Set the PT phase
            api_cap.pt_phase = MeteringPhase[i]

            ## Find the connecting bus of the capacitor through the section
            Count = None
            for k, section in enumerate(LineID):
                if CapacitorSectionId[i] == section:
                    Count = k
                    break

            # If no section found, print a warning
            if Count is None:
                print("WARNING: No section found for capacitor {}".format(obj))

            if Count is not None:
                # Set the connecting_element
                api_cap.connecting_element = ToNodeId[Count].lower().replace(" ", "_")

            # Get the KVAR for each phase
            #
            QCap = [
                float(CapacitorFixedKvarPhase1[i]),
                float(CapacitorFixedKvarPhase2[i]),
                float(CapacitorFixedKvarPhase3[i]),
            ]

            # Get the phases of this capacitor
            if len(CapacitorConnectedPhases[i]) > 0:
                PhasesthisCap = CapacitorConnectedPhases[i]
            else:
                PhasesthisCap = ["A", "B", "C"]

            for t, phase in enumerate(PhasesthisCap):

                # Create a PhaseCapacitor DiTTo object
                phase_caps = PhaseCapacitor(model)

                # Set the phase
                phase_caps.phase = phase

                # Set the Var
                phase_caps.var = QCap[t] * 1000

                api_cap.phase_capacitors.append(phase_caps)

        ####################################################################################
        #                                                                                  #
        #                              REGULATORS                                          #
        #                                                                                  #
        ####################################################################################
        #
        print("--> Parsing Regulators...")
        for i, obj in enumerate(RegulatorId):

            # Create a Regulator DiTTo object
            api_regulator = Regulator(model)

            # Set the name
            api_regulator.name = obj.replace(" ", "_").lower()

            # Set the feeder_name if in mapping
            if RegulatorSectionId[i] in self.section_feeder_mapping:
                api_regulator.feeder_name = self.section_feeder_mapping[
                    RegulatorSectionId[i]
                ]
            # Otherwise, try to clean the name by removing "Reg" prefix
            else:
                cleaned_id = RegulatorId[i].replace("Reg", "").strip()
                if cleaned_id in self.section_feeder_mapping:
                    api_regulator.feeder_name = self.section_feeder_mapping[cleaned_id]

            # Set the Delay of the regulator
            api_regulator.delay = RegulatorTimeDelay[i]

            # Set the Highstep of the regulator
            api_regulator.highstep = int(RegulatorTapLimiterHighSetting[i])

            # Set the LowStep of the regulator
            api_regulator.lowstep = -int(RegulatorTapLimiterLowSetting[i])

            # Get the phases
            regulator_phases = list(RegulagorPhases[i])

            # Set the Bandwidth
            # NOTE: DiTTo does not support different values on different phase
            #
            # Remove 0 values
            bandwidths = [
                b
                for b in [
                    RegulatrorForwardBWDialPhase1[i],
                    RegulatrorForwardBWDialPhase2[i],
                    RegulatrorForwardBWDialPhase3[i],
                ]
                if b != 0
            ]
            if len(bandwidths) != 0:
                # If all values are equal, then use one of them
                if len(np.unique(bandwidths)) == 1:
                    api_regulator.bandwidth = bandwidths[0]
                # Otherwise, use the smallest one and print a warning...
                else:
                    bandwidth_min = min(bandwidths)
                    print(
                        "WARNING: DiTTo does not support different bandwidth values on different phase. Got {ba} for A, {bb} for B, and {bc} for C. Using {x}...".format(
                            ba=RegulatrorForwardBWDialPhase1[i],
                            bb=RegulatrorForwardBWDialPhase2[i],
                            bc=RegulatrorForwardBWDialPhase3[i],
                            x=bandwidth_min,
                        )
                    )
                    api_regulator.bandwidth = bandwidth_min

            # Set the bandcenter in the same way as bandwidths
            #
            # Remove 0 values
            bandcenters = [
                b
                for b in [
                    RegulatrorForwardVoltageSettingPhase1[i],
                    RegulatrorForwardVoltageSettingPhase2[i],
                    RegulatrorForwardVoltageSettingPhase3[i],
                ]
                if b != 0
            ]
            if len(bandcenters) != 0:
                # If all values are equal, then use one of them
                if len(np.unique(bandcenters)) == 1:
                    api_regulator.bandcenter = bandcenters[0]
                # Otherwise, use the smallest one and print a warning...
                else:
                    bandcenter_min = min(bandcenters)
                    print(
                        "WARNING: DiTTo does not support different bandcenter values on different phase. Got {ba} for A, {bb} for B, and {bc} for C. Using {x}...".format(
                            ba=RegulatrorForwardVoltageSettingPhase1[i],
                            bb=RegulatrorForwardVoltageSettingPhase2[i],
                            bc=RegulatrorForwardVoltageSettingPhase3[i],
                            x=bandcenter_min,
                        )
                    )
                    api_regulator.bandcenter = bandcenter_min

            # Find the Regulator equipment in the Warehouse
            Count = None
            if RegulatorNames is not None:
                for idx, obj in enumerate(RegulatorNames):
                    if RegulatorTypes[i] == obj:
                        Count = idx

            # If none found, print a warning
            if Count is None:
                print("WARNING: No Regulator found for section {}".format(obj))

            if Count is not None:

                # Set the PT ratio of the Regulator
                api_regulator.pt_ratio = RegulatorPTRatio[Count]

                # Set the CT ratio of the Regulator
                api_regulator.ct_ratio = RegulatorCTRating[Count]

            # Create the Windings
            #
            n_windings = 2
            for winding in range(n_windings):

                # Create a Winding DiTTo object
                w = Winding(model)

                if Count is not None:
                    # Set the Connection of this Winding
                    w.connection_type = RegulatorConnectionCode[Count][:1]

                    # Set the Nominal voltage
                    w.nominal_voltage = RegulatorRatedVoltage[Count]

                    # Set the Rated Power
                    w.rated_power = (
                        RegulatorRatedKva[Count]
                        / float(n_windings)
                        * 10 ** 3  # TODO: Fix this once the KVA Bug in DiTTo is fixed!!
                    )

                # Create the PhaseWindings
                #
                for phase in regulator_phases:

                    if phase != "N":

                        # Create a PhaseWinding DiTTo object
                        pw = PhaseWinding(model)

                        # Set the phase
                        pw.phase = phase

                        # Add PhaseWinding to the winding
                        w.phase_windings.append(pw)

                # Add winding to the regulator
                api_regulator.windings.append(w)

            ## Set the from and to elements through the sections
            Count = None
            for idx, section in enumerate(LineID):
                if RegulatorSectionId[i] == obj:
                    Count = idx

            # If no section found, print a warning
            if Count is None:
                print("WARNING: No section found for regulator {}".format(obj))

            if Count is not None:

                # Set the from element
                api_regulator.from_element = FromNodeId[Count].lower().replace(" ", "_")

                # Set the to element
                api_regulator.to_element = ToNodeId[Count].lower().replace(" ", "_")

        ####################################################################################
        #                                                                                  #
        #                              PV SYSTEMS                                          #
        #                                                                                  #
        ####################################################################################
        #
        print("--> Parsing PV systems...")
        for i, obj in enumerate(PVUniqueDeviceId):

            if PVGenType[i] == "PhotoVoltaic" or PVGenType[i] == "PhotoVoltaic 3P":

                # Create a Photovoltaic object
                api_PV = Photovoltaic(model)

                # Set the name
                api_PV.name = obj.replace(" ", "_").lower()

                # Set feeder name if in mapping
                if PVSectionId[i] in self.section_feeder_mapping:
                    api_PV.feeder_name = self.section_feeder_mapping[PVSectionId[i]]

                # Set the phases and compute rated power
                rated_power_pv = 0
                if PVGenPhase1Kw[i] != 0:
                    api_PV.phases.append("A")
                    rated_power_pv += PVGenPhase1Kw[i]
                if PVGenPhase2Kw[i] != 0:
                    api_PV.phases.append("B")
                    rated_power_pv += PVGenPhase2Kw[i]
                if PVGenPhase3Kw[i] != 0:
                    api_PV.phases.append("C")
                    rated_power_pv += PVGenPhase3Kw[i]

                # Set the rated power
                api_PV.rated_power = rated_power_pv * 10 ** 3  # DiTTo in Watts

                # Set the reactive power
                reactive_rating_pv = 0
                if PVGenPhase1Kvar[i] != 0:
                    api_PV.phases.append("A")
                    reactive_rating_pv += PVGenPhase1Kvar[i]
                if PVGenPhase2Kvar[i] != 0:
                    api_PV.phases.append("B")
                    reactive_rating_pv += PVGenPhase2Kvar[i]
                if PVGenPhase3Kvar[i] != 0:
                    api_PV.phases.append("C")
                    reactive_rating_pv += PVGenPhase3Kvar[i]

                api_PV.reactive_rating = reactive_rating_pv * 10 ** 3  # DiTTo in Watts

                ## Set the from and to elements through the sections
                Count = None
                for k, section in enumerate(LineID):
                    if PVSectionId[i] == section:
                        Count = k
                        break

                # If no section found, print a warning
                if Count is None:
                    print("WARNING: No section found for PV {}".format(obj))
                else:
                    # Set the connecting element
                    api_PV.connecting_element = ToNodeId[Count].replace(" ", "_")

        for idx, obj in enumerate(GeneratorSectionID):
            Count = None
            for k, gen in enumerate(GeneratorName):
                if GeneratorType[idx] == gen:
                    Count = k

            if Count is not None and GeneratorTypeDev[Count] == "PV":

                # Create a Photovoltaic DiTTo object
                api_PV = Photovoltaic(model)

                # Set the PV name
                api_PV.name = GeneratorSectionID[idx].lower().replace(" ", "_")

                # Set the Rated Power
                api_PV.rated_power = GeneratorKwRating[Count] * 10 ** 3

                # Set feeder name if in mapping
                if obj in self.section_feeder_mapping:
                    api_PV.feeder_name = self.section_feeder_mapping[obj]

                # Set the Connecting element
                Count2 = None
                for k2, section in enumerate(LineID):
                    if GeneratorSectionID[idx] == section:
                        Count2 = k

                if Count2 is None:
                    print("WARNING: No section found for PV {}".format(obj))

                if Count2 is not None:

                    # Set the connecting element
                    api_PV.connecting_element = (
                        ToNodeId[Count2].lower().replace(" ", "_")
                    )

                # Set the Nominal voltage
                api_PV.nominal_voltage = GeneratorVoltageSetting[idx] * 10 ** 3

                # Set the Phases
                for phase in GeneratorConnectedPhases[idx].strip():
                    api_PV.phases.append(phase)

                # Set the Power Factor
                api_PV.power_factor = GeneratorPF[idx]
