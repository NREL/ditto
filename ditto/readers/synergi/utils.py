# -*- coding: utf-8 -*-
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
    URL = "https://github.com/kdheepak/mdbtools/releases/download/download/mdbtools-windows.tar.gz"
elif platform.system() == "Darwin":
    URL = "https://github.com/JuliaBinaryWrappers/mdbtools_jll.jl/releases/download/mdbtools-v0.8.2%2B0/mdbtools.v0.8.2.x86_64-apple-darwin14.tar.gz"
else:
    URL = "https://github.com/JuliaBinaryWrappers/mdbtools_jll.jl/releases/download/mdbtools-v0.8.2%2B0/mdbtools.v0.8.2.x86_64-linux-musl.tar.gz"


def download_mdbtools(url):
    urlretrieve(url, tar_file_name)
    with tarfile.open(tar_file_name) as tf:
        tf.extractall(mdb_dir)
