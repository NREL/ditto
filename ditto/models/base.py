# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import warnings
from traitlets.traitlets import (
    ObserveHandler,
    _deprecated_method,
    _CallbackWrapper,
    EventHandler,
)
import traitlets as T

import logging

logger = logging.getLogger(__name__)


class DiTToHasTraits(T.HasTraits):

    response = T.Any(allow_none=True, help="default trait for managing return values")

    def __init__(self, model, *args, **kwargs):
        model.model_store.append(self)
        self.build(model)
        super().__init__(*args, **kwargs)

    def set_name(self, model):
        try:
            name = self.name
            if name in model.model_names:
                warnings.warn("Duplicate name %s being set. Object overwritten." % name)
                logger.debug("Duplicate name %s being set. Object overwritten." % name)
                logger.debug(model.model_names[name], self)
            model.model_names[name] = self
        except AttributeError:
            pass

    def build(self, model):
        raise NotImplementedError(
            "Build function must be implemented by derived classes"
        )

    def notify_access(self, bunch):
        if not isinstance(bunch, T.Bunch):
            # cast to bunch if given a dict
            bunch = T.Bunch(bunch)
        name, type = bunch.name, bunch.type

        callables = []
        callables.extend(self._trait_notifiers.get(name, {}).get(type, []))
        callables.extend(self._trait_notifiers.get(name, {}).get(T.All, []))
        callables.extend(self._trait_notifiers.get(T.All, {}).get(type, []))
        callables.extend(self._trait_notifiers.get(T.All, {}).get(T.All, []))

        # Call them all now
        # Traits catches and logs errors here.  I allow them to raise
        if len(callables) > 1:
            raise TypeError(
                "Maximum number of callables allowed for a single attribute using the 'fetch' event is 1. Please check the documentation of DiTTo"
            )
        for c in callables:
            # Bound methods have an additional 'self' argument.

            if isinstance(c, _CallbackWrapper):
                c = c.__call__
            elif isinstance(c, EventHandler) and c.name is not None:
                c = getattr(self, c.name)

            return c(bunch)


class DiTToTraitType(T.TraitType):

    allow_none = True

    def get(self, obj, cls=None):
        # Call notify_access with event type fetch
        # If and only if one event exists, a return value will be produced
        # This return value is saved as the current value in obj._trait_values
        # Then call super get
        try:
            r = obj.notify_access(
                T.Bunch(
                    name=self.name,
                    value=obj._trait_values[self.name],
                    owner=self,
                    type="fetch",
                )
            )

            old_value = obj._trait_values[self.name]

            if r is not None and r != old_value:
                logger.debug(
                    "Response from callback event 'fetch' on property {} does not match previous value. Overloading existing value {} with new value {}".format(
                        self.name, old_value, r
                    )
                )
                obj._trait_values[self.name] = r
        except KeyError:
            pass

        return super().get(obj, cls=cls)


class Float(T.Float, DiTToTraitType):
    pass


class Complex(T.Complex, DiTToTraitType):
    pass


class Unicode(T.Unicode, DiTToTraitType):
    pass


class Any(T.Any, DiTToTraitType):
    pass


class Int(T.Int, DiTToTraitType):
    pass


class List(T.List, DiTToTraitType):
    pass


class Instance(T.Instance, DiTToTraitType):
    pass


class Bool(T.Bool, DiTToTraitType):
    pass


observe = T.observe
