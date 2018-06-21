# -*- coding: utf-8 -*-
"""
ditto.core.compat

This module handles compatibility issues between Python 2 and Python 3.
"""

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map
import types
import sys

# Syntax sugar.
_ver = sys.version_info

#: Python 2.x?
is_py2 = _ver[0] == 2

#: Python 3.x?
is_py3 = _ver[0] == 3

if is_py2:

    def ModuleType(m):
        return types.ModuleType(m.encode("utf-8"))


else:

    def ModuleType(m):
        return types.ModuleType(m)


def common_str(string):
    if not sys.version_info >= (3, 0):
        return string.encode("utf-8")
    else:
        return string
