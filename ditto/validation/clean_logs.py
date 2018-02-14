import os
from glob import glob
import argparse

def main():
    '''This module is designed for cleaning log files that might accumulate in the validation folder.

**Usage:**

There are two ways to use this module:

- Remove all log files:

$ python clean_logs.py

- Remove only a subset of the log files:

$ python clean_logs.py -f ./logs/reader/opendss

This will remove all opendss reader log files for example.

$ python clean_logs.py -f ./logs/writer

This will remove all writer log files.

.. note:: Names of removed files are printed when they are deleted.

.. todo:: Add time capabilities like 'delete all log files older than yesterday'

Author: Nicolas Gensollen. November 2017.

'''
    #Parse the arguments
    parser=argparse.ArgumentParser()

    #Feeder list
    parser.add_argument('-f', action='append', dest='folder_list', default=[])

    results=parser.parse_args()

    #If nothing is provided, clean everything...
    if results.folder_list==[]:
        remove_log_and_return_subfolders('./logs/')
    else:
        [remove_log_and_return_subfolders(folder) for folder in results.folder_list]




def remove_log_and_return_subfolders(path):
    '''Remove log files with the following strategy:
- List *.log in the current folder and remove them
- List all subfolders and repeat

'''
    log_files=glob(path.strip('/')+'/*.log')
    for log_file in log_files:
        os.remove(log_file)
        print('-->cleaned:: {}'.format(log_file))

    subfolders=[path.strip('/')+'/'+x for x in os.listdir(path) if '.' not in x]
    if len(subfolders)==0:
        return
    else:
        return [remove_log_and_return_subfolders(folder) for folder in subfolders]

if __name__ == '__main__':
    main()
