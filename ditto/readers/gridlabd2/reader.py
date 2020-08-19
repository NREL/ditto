"""Converts a GridlabD file to a DiTTo model."""

import logging

from ditto.models.base import Unicode
from ditto.models.capacitor import Capacitor
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.node import Node
from ditto.models.phase_capacitor import PhaseCapacitor
from ditto.models.phase_load import PhaseLoad
from ditto.models.phase_winding import PhaseWinding
from ditto.models.power_source import PowerSource
from ditto.models.powertransformer import PowerTransformer
from ditto.models.regulator import Regulator
from ditto.models.winding import Winding
from ditto.models.wire import Wire

from ditto.readers.reader_interface import ReaderInterface
import ditto.readers.gridlabd2.datamodel as datamodel


logger = logging.getLogger(__name__)


class GridlabdReader(ReaderInterface):
    """Converts a GridlabD file to a DiTTo model."""

    def __init__(self):
        """Gridlabd reader constructor."""
        self._gld_objects = {}
        self._api_objects = {}

        self._gld_type_converters = {
            datamodel.ModuleTape: self._convert_ModuleTape,
            datamodel.Recorder: self._convert_Recorder,
            datamodel.Collector: self._convert_Collector,
            datamodel.group_recorder: self._convert_group_recorder,
            datamodel.Histogram: self._convert_Histogram,
            datamodel.Player: self._convert_Player,
            datamodel.Shaper: self._convert_Shaper,
            datamodel.ViolationRecorder: self._convert_ViolationRecorder,
            datamodel.CsvReader: self._convert_CsvReader,
            datamodel.ModuleClimate: self._convert_ModuleClimate,
            datamodel.Weather: self._convert_Weather,
            datamodel.ModuleResidential: self._convert_ModuleResidential,
            datamodel.Load: self._convert_Load,
            datamodel.Loadshape: self._convert_Loadshape,
            datamodel.Enduse: self._convert_Enduse,
            datamodel.ResidentialEnduse: self._convert_ResidentialEnduse,
            datamodel.DryerState: self._convert_DryerState,
            datamodel.HousePanel: self._convert_HousePanel,
            datamodel.ModulePowerFlow: self._convert_ModulePowerFlow,
            datamodel.Node: self._convert_Node,
            datamodel.PowerFlowObject: self._convert_PowerFlowObject,
            datamodel.CurrDump: self._convert_CurrDump,
            datamodel.Emissions: self._convert_Emissions,
            datamodel.FaultCheck: self._convert_FaultCheck,
            datamodel.FrequencyGenerator: self._convert_FrequencyGenerator,
            datamodel.ImpedanceDump: self._convert_ImpedanceDump,
            datamodel.Line: self._convert_Line,
            datamodel.LineConfiguration: self._convert_LineConfiguration,
            datamodel.LineSpacing: self._convert_LineSpacing,
            datamodel.LoadTracker: self._convert_LoadTracker,
            datamodel.Meter: self._convert_Meter,
            datamodel.OverheadLine: self._convert_OverheadLine,
            datamodel.OverheadLineConductor: self._convert_OverheadLineConductor,
            datamodel.PowerMetrics: self._convert_PowerMetrics,
            datamodel.PowerFlowLibrary: self._convert_PowerFlowLibrary,
            datamodel.Recloser: self._convert_Recloser,
            datamodel.Regulator: self._convert_Regulator,
            datamodel.RegulatorConfiguration: self._convert_RegulatorConfiguration,
            datamodel.Restoration: self._convert_Restoration,
            datamodel.Sectionalizer: self._convert_Sectionalizer,
            datamodel.SeriesReactor: self._convert_SeriesReactor,
            datamodel.Switch: self._convert_Switch,
            datamodel.Transformer: self._convert_Transformer,
            datamodel.TransformerConfiguration: self._convert_TransformerConfiguration,
            datamodel.TriplexLine: self._convert_TriplexLine,
            datamodel.TriplexLineConductor: self._convert_TriplexLineConductor,
            datamodel.TriplexLineConfiguration: self._convert_TriplexLineConfiguration,
            datamodel.TriplexNode: self._convert_TriplexNode,
            datamodel.TriplexLoad: self._convert_TriplexLoad,
            datamodel.TriplexMeter: self._convert_TriplexMeter,
            datamodel.UndergroundLine: self._convert_UndergroundLine,
            datamodel.UndergroundLineConductor: self._convert_UndergroundLineConductor,
            datamodel.VoltVarControl: self._convert_VoltVarControl,
            datamodel.VoltDump: self._convert_VoltDump,
            datamodel.ModuleMarket: self._convert_ModuleMarket,
            datamodel.Auction: self._convert_Auction,
            datamodel.Controller: self._convert_Controller,
            datamodel.DoubleController: self._convert_DoubleController,
            datamodel.GeneratorController: self._convert_GeneratorController,
            datamodel.PassiveController: self._convert_PassiveController,
            datamodel.StubBidder: self._convert_StubBidder,
            datamodel.StubAuction: self._convert_StubAuction,
            datamodel.SupervisoryControl: self._convert_SupervisoryControl,
            datamodel.ModuleReliability: self._convert_ModuleReliability,
            datamodel.Metrics: self._convert_Metrics,
            datamodel.EventGen: self._convert_EventGen,
            datamodel.ModuleGenerators: self._convert_ModuleGenerators,
            datamodel.Battery: self._convert_Battery,
            datamodel.CentralDGControl: self._convert_CentralDGControl,
            datamodel.DCDCConverter: self._convert_DCDCConverter,
            datamodel.DieselDG: self._convert_DieselDG,
            datamodel.EnergyStorage: self._convert_EnergyStorage,
            datamodel.Inverter: self._convert_Inverter,
            datamodel.MicroTurbine: self._convert_MicroTurbine,
            datamodel.PowerElectronics: self._convert_PowerElectronics,
            datamodel.Rectifier: self._convert_Rectifier,
            datamodel.Solar: self._convert_Solar,
            datamodel.WindTurbDG: self._convert_WindTurbDG,
            datamodel.ModuleConnection: self._convert_ModuleConnection,
            datamodel.Json: self._convert_Json,
            datamodel.Native: self._convert_Native,
            datamodel.ModuleCommercial: self._convert_ModuleCommercial,
            datamodel.MultiZone: self._convert_MultiZone,
            datamodel.Office: self._convert_Office,
        }

    def list_capacitors(self):
        return []

    def list_feeders(self):
        return []

    def list_lines(self):
        return []

    def list_loads(self):
        return []

    def list_meters(self):
        return []

    def list_nodes(self):
        return []

    def list_phase_capacitors(self):
        return []

    def list_phase_loads(self):
        return []

    def list_phase_reactors(self):
        return []

    def list_phase_storage(self):
        return []

    def list_phase_winding(self):
        return []

    def list_photovoltaics(self):
        return []

    def list_power_sources(self):
        return []

    def list_reactors(self):
        return []

    def list_regulators(self):
        return []

    def list_storage(self):
        return []

    def list_transformers(self):
        return []

    def list_windings(self):
        return []

    def list_wires(self):
        return []

    def read_dataset(self, path, model):
        self._gld_objects = datamodel.parse_file(path)
        for obj in self._gld_objects.values():
            func = self._gld_type_converters.get(type(obj))
            if func is None:
                raise InvalidConfiguration(f"no converter for {type(obj)}")
            func(obj, model)

    def _convert_OverheadLine(self, line, model):
        api_line = Line(model)
        api_line.line_type = "overhead"
        api_line.name = line.name
        api_line.length = line.length * 0.3048
        api_line.from_element = line.from_
        api_line.to_element = line.to


    def _convert_ModuleTape(self, obj, model):
        pass

    def _convert_Recorder(self, obj, model):
        pass

    def _convert_Collector(self, obj, model):
        pass

    def _convert_group_recorder(self, obj, model):
        pass

    def _convert_Histogram(self, obj, model):
        pass

    def _convert_Player(self, obj, model):
        pass

    def _convert_Shaper(self, obj, model):
        pass

    def _convert_ViolationRecorder(self, obj, model):
        pass

    def _convert_CsvReader(self, obj, model):
        pass

    def _convert_ModuleClimate(self, obj, model):
        pass

    def _convert_Weather(self, obj, model):
        pass

    def _convert_ModuleResidential(self, obj, model):
        pass

    def _convert_Load(self, obj, model):
        pass

    def _convert_Loadshape(self, obj, model):
        pass

    def _convert_Enduse(self, obj, model):
        pass

    def _convert_ResidentialEnduse(self, obj, model):
        pass

    def _convert_DryerState(self, obj, model):
        pass

    def _convert_HousePanel(self, obj, model):
        pass

    def _convert_ModulePowerFlow(self, obj, model):
        pass

    def _convert_Node(self, obj, model):
        pass

    def _convert_PowerFlowObject(self, obj, model):
        pass

    def _convert_CurrDump(self, obj, model):
        pass

    def _convert_Emissions(self, obj, model):
        pass

    def _convert_FaultCheck(self, obj, model):
        pass

    def _convert_FrequencyGenerator(self, obj, model):
        pass

    def _convert_ImpedanceDump(self, obj, model):
        pass

    def _convert_Line(self, obj, model):
        pass

    def _convert_LineConfiguration(self, obj, model):
        pass

    def _convert_LineSpacing(self, obj, model):
        pass

    def _convert_LoadTracker(self, obj, model):
        pass

    def _convert_Meter(self, obj, model):
        pass

    def _convert_OverheadLineConductor(self, obj, model):
        pass

    def _convert_PowerMetrics(self, obj, model):
        pass

    def _convert_PowerFlowLibrary(self, obj, model):
        pass

    def _convert_Recloser(self, obj, model):
        pass

    def _convert_Regulator(self, obj, model):
        pass

    def _convert_RegulatorConfiguration(self, obj, model):
        pass

    def _convert_Restoration(self, obj, model):
        pass

    def _convert_Sectionalizer(self, obj, model):
        pass

    def _convert_SeriesReactor(self, obj, model):
        pass

    def _convert_Switch(self, obj, model):
        pass

    def _convert_Transformer(self, obj, model):
        pass

    def _convert_TransformerConfiguration(self, obj, model):
        pass

    def _convert_TriplexLine(self, obj, model):
        pass

    def _convert_TriplexLineConductor(self, obj, model):
        pass

    def _convert_TriplexLineConfiguration(self, obj, model):
        pass

    def _convert_TriplexNode(self, obj, model):
        pass

    def _convert_TriplexLoad(self, obj, model):
        pass

    def _convert_TriplexMeter(self, obj, model):
        pass

    def _convert_UndergroundLine(self, obj, model):
        pass

    def _convert_UndergroundLineConductor(self, obj, model):
        pass

    def _convert_VoltVarControl(self, obj, model):
        pass

    def _convert_VoltDump(self, obj, model):
        pass

    def _convert_ModuleMarket(self, obj, model):
        pass

    def _convert_Auction(self, obj, model):
        pass

    def _convert_Controller(self, obj, model):
        pass

    def _convert_DoubleController(self, obj, model):
        pass

    def _convert_GeneratorController(self, obj, model):
        pass

    def _convert_PassiveController(self, obj, model):
        pass

    def _convert_StubBidder(self, obj, model):
        pass

    def _convert_StubAuction(self, obj, model):
        pass

    def _convert_SupervisoryControl(self, obj, model):
        pass

    def _convert_ModuleReliability(self, obj, model):
        pass

    def _convert_Metrics(self, obj, model):
        pass

    def _convert_EventGen(self, obj, model):
        pass

    def _convert_ModuleGenerators(self, obj, model):
        pass

    def _convert_Battery(self, obj, model):
        pass

    def _convert_CentralDGControl(self, obj, model):
        pass

    def _convert_DCDCConverter(self, obj, model):
        pass

    def _convert_DieselDG(self, obj, model):
        pass

    def _convert_EnergyStorage(self, obj, model):
        pass

    def _convert_Inverter(self, obj, model):
        pass

    def _convert_MicroTurbine(self, obj, model):
        pass

    def _convert_PowerElectronics(self, obj, model):
        pass

    def _convert_Rectifier(self, obj, model):
        pass

    def _convert_Solar(self, obj, model):
        pass

    def _convert_WindTurbDG(self, obj, model):
        pass

    def _convert_ModuleConnection(self, obj, model):
        pass

    def _convert_Json(self, obj, model):
        pass

    def _convert_Native(self, obj, model):
        pass

    def _convert_ModuleCommercial(self, obj, model):
        pass

    def _convert_MultiZone(self, obj, model):
        pass

    def _convert_Office(self, obj, model):
        pass
