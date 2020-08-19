"""Defines the simulation engines supported by DiTTo."""

import enum

class SimulationEngine(enum.Enum):
    CSV = "csv"
    CYME = "cyme"
    DEMO = "demo"
    DEW = "dew"
    GRIDLABD = "gridlabd"
    JSON = "json"
    OPENDSS = "opendss"
    SYNERGI = "synergi"
    WINDMILL = "windmill"
    WINDMILL_ASCII = "windmill_ascii"
