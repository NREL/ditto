# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

from .read import Reader as SynergiReader

# Downloading mdbtools
import platform
import os
import tarfile
from urllib.request import urlretrieve
import sys

current_dir = os.path.realpath(os.path.dirname(__file__))
tar_file_name = os.path.join(current_dir, "mdbtools.tar.gz")
mdb_dir = os.path.join(current_dir, "mdbtools")

if platform.system() == "Windows":
    url = "https://github.com/kdheepak/mdbtools/releases/download/download/mdbtools-windows.tar.gz"
elif platform.system() == "Darwin":
    url = "https://github.com/kdheepak/mdbtools/releases/download/download/mdbtools-osx.tar.gz"
else:
    url = "https://github.com/kdheepak/mdbtools/releases/download/download/mdbtools-linux.tar.gz"

urlretrieve(url, tar_file_name)
tf = tarfile.open(tar_file_name)
tf.extractall(mdb_dir)
