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
    URL = "https://github.com/kdheepak/mdbtools/releases/download/download/mdbtools-win.tar.gz"
elif platform.system() == "Darwin":
    URL = "https://github.com/kdheepak/mdbtools/releases/download/download/mdbtools-osx.tar.gz"
else:
    URL = "https://github.com/kdheepak/mdbtools/releases/download/download/mdbtools-linux.tar.gz"


def download_mdbtools(url):
    urlretrieve(url, tar_file_name)
    with tarfile.open(tar_file_name) as tf:
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tf, mdb_dir)
