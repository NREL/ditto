from .base import DiTToHasTraits, Float, Unicode, Any, Int, List, observe, Instance

from .position import Position


class PhaseStorage(DiTToHasTraits):

    phase = Unicode(help="""The phases the device is on.""", default_value=None)
    p = Float(
        help="""Present Watt value (positive denotes power coming out, and negative is charging). In watts.""",
        default_value=None,
    )
    q = Float(help="""Present var value. In vars.""", default_value=None)

    def build(self, model):
        """
        TODO...
        """
        self._model = model
