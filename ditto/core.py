# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from builtins import super, range, zip, round, map

import types


class DiTToBase(object):
    """Base class for all objects in the core"""

    def __init__(self, *args, **kwargs):

        self._register_callbacks(
            kwargs.pop("init_callback", None),
            kwargs.pop("get_callback", None),
            kwargs.pop("set_callback", None),
            kwargs.pop("del_callback", None),
        )

        for k, v in kwargs.items():
            if self._is_property(k):
                setattr(self, k, v)
            else:
                raise AttributeError(
                    'Unable to set "{}" on class {}.'.format(k, self.__class__.__name__)
                )

        try:
            self._callback_init(**kwargs)
        except AttributeError:
            pass

    def _is_property(self, name):
        """Returns True if the object has a property with the specified name."""
        return isinstance(getattr(self.__class__, name, None), PropertyType)

    def iter_properties(self):
        for p in dir(self.__class__):
            if self._is_property(p):
                yield p, getattr(self, p)

    def _register_callbacks(self, c_init=None, c_get=None, c_set=None, c_del=None):

        if c_init is not None:
            self._callback_init = types.MethodType(c_init, self, self.__class__)
        if c_get is not None:
            self._callback_get = types.MethodType(c_get, self, self.__class__)
        if c_set is not None:
            self._callback_set = types.MethodType(c_set, self, self.__class__)
        if c_del is not None:
            self._callback_del = types.MethodType(c_del, self, self.__class__)


class DiTToTypeError(TypeError):
    pass


class PropertyType(object):
    pass
