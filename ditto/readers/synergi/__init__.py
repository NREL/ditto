# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .read import Reader as SynergiReader

from .utils import download_mdbtools, URL

download_mdbtools(URL)  # downloads MDB binaries
