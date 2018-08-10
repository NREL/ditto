from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map


class GridLABDBase(object):

    _properties = []

    def __init__(self, *args, **kwargs):

        for p in self._build_properties():
            self._properties = self._properties + p

        for k, v in kwargs.items():
            self[k] = v

    def _build_properties(self):
        for c in self.__class__.mro():
            if c != self.__class__ and c != object:
                yield c._properties

    def __getitem__(self, k):
        try:
            return getattr(self, "_{}".format(k))
        except AttributeError as e:
            raise AttributeError(
                "{} not found in {}".format(k, self.__class__.__name__)
            )

    def __setitem__(self, k, v):
        if k not in [p["name"] for p in self._properties]:
            raise AttributeError(
                "Unable to set {} with {} on {}".format(k, v, self.__class__.__name__)
            )
        return setattr(self, "_{}".format(k), v)
