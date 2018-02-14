# -*- coding: utf-8 -*-
"""
EDD DEW TO DiTTo Conversion

Created on Mon Aug 20 20:18:01 2017

@author: Abilash Thakallapelli

Developed based on EDD DEW Version V10.62.0
"""
import os
from read import Reader
from ditto.store import Store
from ditto.writers.opendss.write import Writer

dew_models_dir = os.path.join('C:/Users/athakall/Desktop/DiTTo-develop - Copy/ditto/readers/DEW/Models')
dew_database_dir = os.path.join('C:/Users/athakall/Desktop/DiTTo-develop - Copy/ditto/readers/DEW/DataBase')

modelfile = 'IEEE-13.dew'  #IEEE 13Bus System
#modelfile = 'IEEE-123.dew' #IEEE 123Bus System

#database read
databasename = 'DataBase.xlsx'
inputfile = open(os.path.join(dew_models_dir,modelfile),'r')
databasepath = os.path.join(dew_database_dir,databasename)
m = Store()
reader = Reader()
reader.parse(m, inputfile, databasepath)
writer=Writer(linecodes_flag=True, output_path='C:/Users/athakall/Desktop/DiTTo-develop - Copy/ditto/readers/DEW/Models/IEEE_13_node_output/')
writer.write(m, verbose=True)