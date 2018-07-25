from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position


class Recorder(DiTToHasTraits):
    """Inheritance:
        Asset (self._asset)
            -> Location (self._loc)

        ConnectivityNode (self._cn)
    """

    name = Unicode(help="""Name of the recorder  object""")
    parent = Any(help="""Name of the object you want to record""")
    property = Any(help="""What you want to record, e.g. voltage_A[kv]""")
    output_file = Any(help="""the output file name """)
    interval = Float(
        help="""Recording interval in seconds, e.g., if interval=50, then record every 50 seconds"""
    )


def build(self, model, Asset=None, ConnectivityNode=None, Location=None):
    self._model = model
