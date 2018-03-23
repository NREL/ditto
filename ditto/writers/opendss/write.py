# coding: utf8

from __future__ import absolute_import, division, print_function
from builtins import super, range, zip, round, map

import os
import math
import numpy as np
import logging
import pandas as pd
from functools import reduce

#DiTTo imports
from ditto.models.node import Node
from ditto.models.line import Line
from ditto.models.load import Load
from ditto.models.regulator import Regulator
from ditto.models.wire import Wire
from ditto.models.capacitor import Capacitor
from ditto.models.timeseries import Timeseries
from ditto.models.powertransformer import PowerTransformer
from ditto.models.winding import Winding
from ditto.models.storage import Storage
from ditto.models.phase_storage import PhaseStorage
from ditto.models.power_source import PowerSource

from ditto.writers.abstract_writer import abstract_writer

logger = logging.getLogger(__name__)


class Writer(abstract_writer):
    '''DiTTo--->OpenDSS writer class.
Use to write a DiTTo model to OpenDSS format.

:param log_file: Name/path of the log file. Optional. Default='./OpenDSS_writer.log'
:type log_file: str
:param linecodes_flag: Use OpenDSS linecodes rather than lineGeometries. Optional. Default=True
:type linecodes_flag: bool
:param output_path: Path to write the OpenDSS files. Optional. Default='./'
:type output_path: str

**Constructor:**

>>> my_writer=Writer(log_file='./logs/my_log.log', output_path='./feeder_output/')

**Output file names:**

+-----------------+--------------------+
|     Object      |    File name       |
+=================+====================+
|      Buses      |   buscoords.dss    |
+-----------------+--------------------+
|  Transformers   |   Transformers.dss |
+-----------------+--------------------+
|      Loads      |      Loads.dss     |
+-----------------+--------------------+
|   Regulators    |   Regulators.dss   |
+-----------------+--------------------+
|   Capacitors    |   Capacitors.dss   |
+-----------------+--------------------+
|     Lines       |      Lines.dss     |
+-----------------+--------------------+
|     Wires       |    WireData.dss    |
+-----------------+--------------------+
| Line Geometries |  LineGeometry.dss  |
+-----------------+--------------------+
|    Line Codes   |    Linecodes.dss   |
+-----------------+--------------------+
|    Load Shapes  |    Loadshapes.dss  |
+-----------------+--------------------+

author: Nicolas Gensollen. October 2017.

'''
    register_names = ["dss", "opendss", "OpenDSS", "DSS"]

    def __init__(self, **kwargs):
        '''Constructor for the OpenDSS writer.

'''
        self.timeseries_datasets = {}
        self.timeseries_format = {}
        self.all_linecodes = {}
        self.all_wires = {}
        self.all_geometries = {}
        self.compensator = {}

        #Call super
        abstract_writer.__init__(self, **kwargs)

        #Set the linecode flag
        #If True, linecodes will be used when writing the lines
        #If False, linegeometries and wiredata will be used when writing the lines
        if 'linecodes_flag' in kwargs and isinstance(kwargs['linecodes_flag'], bool):
            self.linecodes_flag = kwargs['linecodes_flag']
        else:
            self.linecodes_flag = True

        self.logger.info('DiTTo--->OpenDSS writer successfuly instanciated.')

    def write(self, model, **kwargs):
        '''General writing function responsible for calling the sub-functions.

:param model: DiTTo model
:type model: DiTTo model
:param verbose: Set verbose mode. Optional. Default=False
:type verbose: bool
:param write_taps: Write the transformer taps if they are provided. (This can cause some problems). Optional. Default=False
:type write_taps: bool
:returns: 1 for success, -1 for failure
:rtype: int

'''
        self.files_to_redirect=[]
        #Verbose print the progress
        if 'verbose' in kwargs and isinstance(kwargs['verbose'], bool):
            self.verbose = kwargs['verbose']
        else:
            self.verbose = False

        if 'write_taps' in kwargs:
            self.write_taps = kwargs['write_taps']
        else:
            self.write_taps = False

        #Write the bus coordinates
        self.logger.info('Writing the bus coordinates...')
        if self.verbose: logger.debug('Writing the bus coordinates...')
        s = self.write_bus_coordinates(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the transformers
        self.logger.info('Writing the transformers...')
        if self.verbose: logger.debug('Writing the transformers...')
        s = self.write_transformers(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the regulators
        self.logger.info('Writing the regulators...')
        if self.verbose: logger.debug('Writing the regulators...')
        s = self.write_regulators(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the capacitors
        self.logger.info('Writing the capacitors...')
        if self.verbose: logger.debug('Writing the capacitors...')
        s = self.write_capacitors(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #write the timeseries
        self.logger.info('Writing the timeseries...')
        if self.verbose: logger.debug('Writing the timeseries...')
        s = self.write_timeseries(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #write the loads
        self.logger.info('Writing the loads...')
        if self.verbose: logger.debug('Writing the loads...')
        s = self.write_loads(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #If we decided to use linecodes, write the linecodes
        if self.linecodes_flag:
            self.logger.info('Writting the linecodes...')
            if self.verbose: logger.debug('Writting the linecodes...')
            s = self.write_linecodes(model)
            if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the WireData
        self.logger.info('Writting the WireData...')
        if self.verbose: logger.debug('Writting the WireData...')
        s = self.write_wiredata(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the lineGeometries
        self.logger.info('Writting the linegeometries...')
        if self.verbose: logger.debug('Writting the linegeometries...')
        s = self.write_linegeometry(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the lines
        self.logger.info('Writting the lines...')
        if self.verbose: logger.debug('Writting the lines...')
        s = self.write_lines(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the storage elements
        self.logger.info('Writting the storage devices...')
        if self.verbose: logger.debug('Writting the storage devices...')
        s = self.write_storages(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the PV
        self.logger.info('Writting the PVs...')
        if self.verbose: logger.debug('Writting the PVs...')
        s = self.write_PVs(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        #Write the Master file
        self.logger.info('Writting the master file...')
        if self.verbose: logger.debug('Writting the master file...')
        s = self.write_master_file(model)
        if self.verbose and s != -1: logger.debug('Succesful!')

        self.logger.info('Done.')
        if self.verbose: logger.debug('Writting done.')

        return 1

    def phase_mapping(self, phase):
        '''Maps the Ditto phases ('A','B','C') into OpenDSS phases (1,2,3).

**Phase mapping:**

+---------------+-------------+
| OpenDSS phase | DiTTo phase |
+===============+=============+
|    1 or '1'   |     'A'     |
+---------------+-------------+
|    2 or '2'   |     'B'     |
+---------------+-------------+
|    3 or '3'   |     'C'     |
+---------------+-------------+

:param phase: Phase in DiTTo format
:type phase: unicode
:returns: Phase in OpenDSS format
:rtype: int

.. note:: Returns None if phase is not in ['A','B','C']

'''
        if phase == u'A':
            return 1
        elif phase == u'B':
            return 2
        elif phase == 'C':
            return 3
        else:
            return None

    def mode_mapping(self, mode):
        '''
            TODO
        '''
        if mode.lower() == 'currentFlow':
            return 'current'
        elif mode.lower() == 'voltage':
            return 'voltage'
        elif mode.lower() == 'activepower':
            return 'PF'
        elif mode.lower() == 'reactivepower':
            return 'kvar'
        elif mode.lower() == 'admittance':
            return None
        elif mode.lower() == 'timescheduled':
            return 'time'
        else:
            return None

    def write_bus_coordinates(self, model):
        '''Write the bus coordinates to a CSV file ('buscoords.csv' by default), with the following format:

>>> bus_name,coordinate_X,coordinate_Y

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        fp = open(os.path.join(self.output_path, 'buscoords.dss'), 'w')

        #Loop over the DiTTo objects
        for i in model.models:
            #If we find a node
            if isinstance(i, Node):

                #Extract the name and the coordinates
                if ((hasattr(i, 'name') and i.name is not None) and (hasattr(i, 'positions') and i.positions is not None and len(i.positions) > 0)):
                    fp.write('{name} {X} {Y}\n'.format(name=i.name.lower(), X=i.positions[0].lat, Y=i.positions[0].long))

        return 1

    def write_transformers(self, model):
        '''Write the transformers to an OpenDSS file (Transformers.dss by default).

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

.. note::

    - Assume that within the transformer API everything is stored in windings.
    - Currently not modelling open winding connections (e.g. open-delta open-wye)

'''
        #Create and open the transformer DSS file
        fp = open(os.path.join(self.output_path, 'Transformers.dss'), 'w')
        self.files_to_redirect.append('Transformers.dss')

        #Loop over the DiTTo objects
        for i in model.models:
            #If we get a transformer object...
            if isinstance(i, PowerTransformer):
                #Write the data in the file
                #Name
                if hasattr(i, 'name') and i.name is not None:
                    fp.write('New Transformer.' + i.name)
                else:
                    #If we do not have a valid name, do not even try
                    #to write anything for this transformer....
                    continue

                #Number of phases and windings
                if hasattr(i, 'windings') and i.windings is not None:
                    N_phases = []
                    for winding in i.windings:
                        if hasattr(winding, 'phase_windings') and winding.phase_windings is not None:
                            N_phases.append(len(winding.phase_windings))
                    if len(np.unique(N_phases)) != 1:
                        self.logger.error('Did not find the same number of phases accross windings of transformer {name}'.format(name=i.name))

                    try:
                        fp.write(' phases={Np}'.format(Np=N_phases[0]))
                        fp.write(' windings={N}'.format(N=len(i.windings)))
                    except:
                        self.logger.error('Could not write the number of phases for transformer {name}'.format(name=i.name))

                #Connection
                if hasattr(i, 'from_element') and i.from_element is not None:
                    bus1 = i.from_element
                else:
                    bus1 = None
                if hasattr(i, 'to_element') and i.to_element is not None:
                    bus2 = i.to_element
                else:
                    bus2 = None

                if bus1 is not None and bus2 is not None:
                    buses = [bus1, bus2]
                else:
                    buses = None

                #Rated power
                #if hasattr(i, 'rated_power') and i.rated_power is not None:
                #    fp.write(' kva='+str(i.rated_power*10**-3)) #OpenDSS in kWatts

                #Emergency power
                #Emergency_power removed from powerTransformers and added to windings by Tarek
                #if hasattr(i, 'emergency_power') and i.emergency_power is not None:
                #    fp.write(' EmergHKVA='+str(i.emergency_power*10**-3)) #OpenDSS in kWatts

                #Loadloss
                if hasattr(i, 'loadloss') and i.loadloss is not None:
                    fp.write(' %loadloss=' + str(i.loadloss)) #OpenDSS in kWatts

                #install type (Not mapped)

                #noload_loss
                if hasattr(i, 'noload_loss') and i.noload_loss is not None:
                    fp.write(' %Noloadloss=' + str(i.noload_loss))

                #noload_loss
                if hasattr(i, 'normhkva') and i.normhkva is not None:
                    fp.write(' normhkva=' + str(i.normhkva))

                #phase shift (Not mapped)

                # Assume that we only have two or three windings. Three are used for center-tap transformers. Other single or three phase transformers use 2 windings
                # For banked 3-phase transformers, separate single phase transformers are used
                if hasattr(i, 'windings') and i.windings is not None:

                    if hasattr(winding, 'phase_windings') and winding.phase_windings is not None:

                        for phase_winding in winding.phase_windings:
                            if hasattr(phase_winding, 'compensator_r') and phase_winding.compensator_r is not None:
                                if not i.name in self.compensator:
                                    self.compensator[i.name] = {}
                                    self.compensator[i.name]['R'] = set([phase_winding.compensator_r])
                                elif 'R' in self.compensator[i.name]:
                                    self.compensator[i.name]['R'].add(phase_winding.compensator_r)
                                else:
                                    self.compensator[i.name]['R'] = set([phase_winding.compensator_r])

                            if hasattr(phase_winding, 'compensator_x') and phase_winding.compensator_x is not None:
                                if not i.name in self.compensator:
                                    self.compensator[i.name] = {}
                                    self.compensator[i.name]['X'] = set([phase_winding.compensator_x])
                                elif 'X' in self.compensator[i.name]:
                                    self.compensator[i.name]['X'].add(phase_winding.compensator_x)
                                else:
                                    self.compensator[i.name]['X'] = set([phase_winding.compensator_x])

                    if len(i.windings) == 2:

                        for cnt, winding in enumerate(i.windings):

                            fp.write(' wdg={N}'.format(N=cnt + 1))

                            #Connection type
                            if hasattr(winding, 'connection_type') and winding.connection_type is not None:
                                if winding.connection_type == 'Y':
                                    fp.write(' conn=wye')
                                elif winding.connection_type == 'D':
                                    fp.write(' conn=delta')
                                else:
                                    self.logger.error(
                                        'Unsupported type of connection {conn} for transformer {name}'.format(
                                            conn=winding.connection_type, name=i.name
                                        )
                                    )

                            #Voltage type (Not mapped)

                            #Nominal voltage
                            if hasattr(winding, 'nominal_voltage') and winding.nominal_voltage is not None:
                                fp.write(' Kv={kv}'.format(kv=winding.nominal_voltage * 10**-3)) #OpenDSS in kvolts

                            #rated power
                            if hasattr(winding, 'rated_power') and winding.rated_power is not None:
                                fp.write(' kva={kva}'.format(kva=winding.rated_power * 10**-3))

                            #emergency_power
                            #Was added to windings by Tarek
                            if hasattr(winding, 'emergency_power') and winding.emergency_power is not None:
                                fp.write(' EmergHKVA={}'.format(winding.emergency_power * 10**-3)) #OpenDSS in kWatts

                            #resistance
                            if hasattr(winding, 'resistance') and winding.resistance is not None:
                                fp.write(' %R={R}'.format(R=winding.resistance))

                            #Voltage limit (Not mapped)

                            #Reverse resistance (Not mapped)

                            #Phase windings
                            if hasattr(winding, 'phase_windings') and winding.phase_windings is not None:

                                if buses is not None:
                                    bus = buses[cnt]
                                    fp.write(' bus={bus}'.format(bus=str(bus)))

                                if len(winding.phase_windings) != 3:

                                    for j, phase_winding in enumerate(winding.phase_windings):

                                        #Connection
                                        if hasattr(phase_winding, 'phase') and phase_winding.phase is not None:
                                            fp.write('.' + str(self.phase_mapping(phase_winding.phase)))

                                    if winding.connection_type == 'D' and len(winding.phase_windings) == 1:
                                        if self.phase_mapping(phase_winding.phase) == 1:
                                            fp.write('.2')
                                        if self.phase_mapping(phase_winding.phase) == 2:
                                            fp.write('.3')
                                        if self.phase_mapping(phase_winding.phase) == 3:
                                            fp.write('.1')

                                #Tap position
                                #THIS CAN CAUSE PROBLEMS
                                #Use write_taps boolean to write this information or not
                                if self.write_taps and hasattr(winding.phase_windings[0], 'tap_position'
                                                               ) and winding.phase_windings[0].tap_position is not None:
                                    fp.write(' Tap={tap}'.format(tap=winding.phase_windings[0].tap_position))

                        if hasattr(i, 'reactances') and i.reactances is not None:
                            #Since we are in the case of 2 windings, we should only have one reactance
                            if isinstance(i.reactances, list):
                                if len(i.reactances) != 1:
                                    self.logger.error(
                                        'Number of reactances incorrect for transformer {name}. Expected 1, got {N}'.format(
                                            name=i.name, N=len(i.reactances)
                                        )
                                    )
                                else:
                                    fp.write(' XHL={reac}'.format(reac=i.reactances[0]))
                            #If it is not a list, maybe it was entered as a scalar, but should not be that way....
                            elif isinstance(i.reactances, (int, float)):
                                fp.write(' XHL={reac}'.format(reac=i.reactances))
                            else:
                                self.logger.error('Reactances not understood for transformer {name}.'.format(name=i.name))

                    # This is used to represent center-tap transformers
                    # As described in the documentation, if the R and X values are not known, the values described by default_r and default_x should be used
                    if len(i.windings) == 3:
                        default_r = [0.6, 1.2, 1.2]
                        default_x = [2.04, 2.04, 1.36]

                        for cnt, winding in enumerate(i.windings):

                            fp.write(' wdg={N}'.format(N=cnt + 1))

                            if hasattr(winding, 'connection_type') and winding.connection_type is not None:
                                if winding.connection_type == 'Y':
                                    fp.write(' conn=wye')
                                elif winding.connection_type == 'D':
                                    fp.write(' conn=delta')
                                else:
                                    self.logger.error(
                                        'Unsupported type of connection {conn} for transformer {name}'.format(
                                            conn=winding.connection_type, name=i.name
                                        )
                                    )

                            #Connection
                            if buses is not None:

                                if cnt == 0 or cnt == 1:
                                    fp.write(' bus={b}'.format(b=buses[cnt]))
                                elif cnt == 2:
                                    fp.write(' bus={b}'.format(b=buses[cnt - 1]))

                                # These are the configurations for center tap transformers
                                if cnt == 0:
                                    fp.write('.{}'.format(self.phase_mapping(winding.phase_windings[0].phase)))
                                if cnt == 1:
                                    fp.write('.1.0')
                                if cnt == 2:
                                    fp.write('.0.2')

                            #Voltage type (Not mapped)

                            #Nominal voltage
                            if hasattr(winding, 'nominal_voltage') and winding.nominal_voltage is not None:
                                fp.write(' Kv={kv}'.format(kv=winding.nominal_voltage * 10**-3)) #OpenDSS in kvolts

                            #rated power
                            if hasattr(winding, 'rated_power') and winding.rated_power is not None:
                                fp.write(' kva={kva}'.format(kva=winding.rated_power * 10**-3))

                            #emergency_power
                            #Was added to windings by Tarek
                            if hasattr(winding, 'emergency_power') and winding.emergency_power is not None:
                                fp.write(' EmergHKVA={}'.format(winding.emergency_power * 10**-3)) #OpenDSS in kWatts

                            #Tap position
                            if (self.write_taps and
                                hasattr(winding, 'phase_windings') and
                                winding.phase_windings is not None and
                                hasattr(winding.phase_windings[0], 'tap_position') and
                                winding.phase_windings[0].tap_position is not None):
                                fp.write(' Tap={tap}'.format(tap=winding.phase_windings[0].tap_position))

                            #Voltage limit (Not mapped)

                            #resistance
                            #if hasattr(winding, 'resistance') and winding.resistance is not None:
                            #    fp.write(' %R={R}'.format(R=winding.resistance))

                            #Reverse resistance (Not mapped)

                            if hasattr(winding, 'resistance') and winding.resistance is not None:
                                fp.write(' %r={R}'.format(R=winding.resistance))
                            else:
                                fp.write(' %r={R}'.format(R=default_r[cnt - 1]))

                        if hasattr(i, 'reactances') and i.reactances is not None:
                            #Here, we should have 3 reactances
                            if isinstance(i.reactances, list) and len(i.reactances) == 3:
                                fp.write(' XHL={XHL} XLT={XLT} XHT={XHT}'.format(XHL=i.reactances[0], XLT=i.reactances[1], XHT=i.reactances[2]))
                            else:
                                self.logger.error('Wrong number of reactances for transformer {name}'.format(name=i.name))
                        else:
                            fp.write(' XHL=%f XHT=%f XLT=%f' % (default_x[0], default_x[1], default_x[2]))

                fp.write('\n\n')

        return 1


    def write_storages(self, model):
        '''Write the storage devices stored in the model.

            .. note:: Pretty straightforward for now since the DiTTo storage model class was built from the OpenDSS documentation.
                      The core representation is succeptible to change when mapping with other formats.

            .. todo:: Develop the docstring a little bit more...

        '''
        with open(os.path.join(self.output_path,'Storages.dss'), 'w') as fp:
            self.files_to_redirect.append('Storages.dss')
            for i in model.models:
                if isinstance(i, Storage):
                    #Name
                    if hasattr(i, 'name') and i.name is not None:
                        fp.write('New Storage.{name}'.format(name=i.name))

                    #Phases
                    if hasattr(i, 'phase_storages') and i.phase_storages is not None:
                        fp.write(' phases={N_phases}'.format(N_phases=len(i.phase_storages)))

                        #kW (Need to sum over the phase_storage elements)
                        if sum([1 for phs in i.phase_storages if phs.p is None])==0:
                            p_tot=sum([phs.p for phs in i.phase_storages])
                            fp.write(' kW={kW}'.format(kW=p_tot*10**-3)) #DiTTo in watts

                            #Power factor
                            if sum([1 for phs in i.phase_storages if phs.q is None])==0:
                                q_tot=sum([phs.q for phs in i.phase_storages])
                                if q_tot !=0 and p_tot!=0:
                                    pf=float(p_tot)/math.sqrt(p_tot**2+q_tot**2)
                                    fp.write(' pf={pf}'.format(pf=pf))

                    #connecting_element
                    if hasattr(i, 'connecting_element') and i.connecting_element is not None:
                        fp.write(' Bus1={elt}'.format(elt=i.connecting_element))

                    #nominal_voltage
                    if hasattr(i, 'nominal_voltage') and i.nominal_voltage is not None:
                        fp.write(' kV={volt}'.format(volt=i.nominal_voltage*10**-3)) #DiTTo in volts

                    #rated_power
                    if hasattr(i, 'rated_power') and i.rated_power is not None:
                        fp.write(' kWRated={kW}'.format(kW=i.rated_power*10**-3)) #DiTTo in watts

                    #rated_kWh
                    if hasattr(i, 'rated_kWh') and i.rated_kWh is not None:
                        fp.write(' kWhRated={kWh}'.format(kWh=i.rated_kWh))

                    #stored_kWh
                    if hasattr(i, 'stored_kWh') and i.stored_kWh is not None:
                        fp.write(' kWhStored={stored}'.format(stored=i.stored_kWh))

                    #state
                    if hasattr(i, 'state') and i.state is not None:
                        fp.write(' State={state}'.format(state=i.state))
                    else:
                        fp.write(' State=IDLING') #Default value in OpenDSS

                    #reserve
                    if hasattr(i, 'reserve') and i.reserve is not None:
                        fp.write(' %reserve={reserve}'.format(reserve=i.reserve))

                    #discharge_rate
                    if hasattr(i, 'discharge_rate') and i.discharge_rate is not None:
                        fp.write(' %Discharge={discharge_rate}'.format(discharge_rate=i.discharge_rate))

                    #charge_rate
                    if hasattr(i, 'charge_rate') and i.charge_rate is not None:
                        fp.write(' %Charge={charge_rate}'.format(charge_rate=i.charge_rate))

                    #charging_efficiency
                    if hasattr(i, 'charging_efficiency') and i.charging_efficiency is not None:
                        fp.write(' %EffCharge={charge_eff}'.format(charge_eff=i.charging_efficiency))

                    #discharging_efficiency
                    if hasattr(i, 'discharging_efficiency') and i.discharging_efficiency is not None:
                        fp.write(' %EffDischarge={discharge_eff}'.format(discharge_eff=i.discharging_efficiency))

                    #resistance
                    if hasattr(i, 'resistance') and i.resistance is not None:
                        fp.write(' %R={resistance}'.format(resistance=i.resistance))

                    #reactance
                    if hasattr(i, 'reactance') and i.reactance is not None:
                        fp.write(' %X={reactance}'.format(reactance=i.reactance))

                    #model
                    if hasattr(i, 'model_') and i.model_ is not None:
                        fp.write(' model={model}'.format(model=i.model_))

                    #Yearly/Daily/Duty/Charge trigger/Discharge trigger
                    #
                    #TODO: See with Tarek and Elaine how we can support that

                    fp.write('\n')

    def write_PVs(self, model):
        '''Write the PVs.

        '''
        with open(os.path.join(self.output_path, 'PV_systems.dss'), 'w') as fp:
            self.files_to_redirect.append('PV_systems.dss')
            for i in model.models:
                if isinstance(i, PowerSource):
                    #If is_sourcebus is set to 1, then the object represents a source and not a PV system
                    if hasattr(i, 'is_sourcebus') and i.is_sourcebus==0:
                        #Name
                        if hasattr(i, 'name') and i.name is not None:
                            fp.write('New PVSystem.{name}'.format(name=i.name))

                        #Phases
                        if hasattr(i, 'phases') and i.phases is not None:
                            fp.write(' phases={n_phases}'.format(n_phases=len(i.phases)))

                        #connecting element
                        if hasattr(i, 'connecting_element') and i.connecting_element is not None:
                            fp.write(' bus1={connecting_elt}'.format(connecting_elt=i.connecting_element))

                        #nominal voltage
                        if hasattr(i, 'nominal_voltage') and i.nominal_voltage is not None:
                            fp.write(' kV={kV}'.format(kV=i.nominal_voltage*10**-3)) #DiTTo in volts

                        #rated power
                        if hasattr(i, 'rated_power') and i.rated_power is not None:
                            fp.write(' kVA={kVA}'.format(kVA=i.rated_power*10**-3)) #DiTTo in vars

                        #connection type
                        if hasattr(i, 'connection_type') and i.connection_type is not None:
                            mapps={'D':'delta', 'Y':'wye'}
                            if i.connection_type in mapps:
                                fp.write(' conn={conn}'.format(conn=mapps[i.connection_type]))
                            else:
                                raise NotImplementedError('Connection {conn} for PV systems is currently not supported.'.format(conn=i.connection_type))

                        #cutout_percent
                        if hasattr(i, 'cutout_percent') and i.cutout_percent is not None:
                            fp.write(' %Cutout={cutout}'.format(cutout=i.cutout_percent))

                        #cutin_percent
                        if hasattr(i, 'cutin_percent') and i.cutin_percent is not None:
                            fp.write(' %Cutin={cutin}'.format(cutin=i.cutin_percent))

                        #resistance
                        if hasattr(i, 'resistance') and i.resistance is not None:
                            fp.write(' %R={resistance}'.format(resistance=i.resistance))

                        #reactance
                        if hasattr(i, 'reactance') and i.reactance is not None:
                            fp.write(' %X={reactance}'.format(reactance=i.reactance))

                        #v_max_pu
                        if hasattr(i, 'v_max_pu') and i.v_max_pu is not None:
                            fp.write(' Vmaxpu={v_max_pu}'.format(v_max_pu=i.v_max_pu))

                        #v_min_pu
                        if hasattr(i, 'v_min_pu') and i.v_min_pu is not None:
                            fp.write(' Vminpu={v_min_pu}'.format(v_min_pu=i.v_min_pu))

                        #power_factor
                        if hasattr(i, 'power_factor') and i.power_factor is not None:
                            fp.write(' pf={power_factor}'.format(power_factor=i.power_factor))

                        fp.write('\n')







    def write_timeseries(self, model):
        '''Write all the unique timeseries objects to csv files if they are in memory.
           If the data is already on disk, no new data is created.
           Then create the Loadshapes.dss file containing the links to the loadshapes.
           Currently all loadshapes are assumed to be yearly
           TODO: Add daily profiles as well
        '''
        fp = open(os.path.join(self.output_path,  'Loadshapes.dss'), 'w')
        self.files_to_redirect.append('Loadshapes.dss')

        all_data = set()
        for i in model.models:
            if isinstance(i, Timeseries):
                if hasattr(i, 'data_location'
                           ) and i.data_location is not None and os.path.isfile(i.data_location) and (i.scale_factor is None or i.scale_factor == 1):
                    filename = i.data_location.split('/')[-1][:-4] # Assume all data files have a 3 letter suffix (e.g. .dss .csv .txt etc)
                    if i.data_location in self.timeseries_datasets:
                        continue
                    npoints = len(pd.read_csv(i.data_location))
                    if npoints == 24 or npoints == 24 * 60 or npoints == 24 * 60 * 60: # The cases of hourly, minute or second resolution data for exactly one day TODO: make this more precise
                        self.timeseries_format[filename] = 'daily'
                    else:
                        self.timeseries_format[filename] = 'yearly'
                    fp.write(
                        'New loadshape.{filename} npts= {npoints} interval=1 mult = (file={data_location})\n\n'.format(
                            filename=filename, npoints=npoints, data_location=i.data_location
                        )
                    )
                    self.timeseries_datasets[i.data_location] = filename

                elif hasattr(i, 'data_location') and i.data_location is not None and os.path.isfile(
                    i.data_location
                ) and i.scale_factor is not None and i.scale_factor != 1:
                    filename = i.data_location.split('/')[-1][:-4] + '_scaled' # Assume all data files have a 3 letter suffix (e.g. .dss .csv .txt etc)
                    scaled_data_location = i.data_location[:-4] + '__scaled%s' % (str(int((i.scale_factor) * 100)).zfill(3)) + i.data_location[-4:]
                    if i.data_location in self.timeseries_datasets:
                        continue
                    timeseries = pd.read_csv(i.data_location)
                    npoints = len(timeseries)
                    timeseries.iloc[:, [0]] = timeseries.iloc[:, [0]] * i.scale_factor
                    timeseries.to_csv(scaled_data_location, index=False)
                    if npoints == 24 or npoints == 24 * 60 or npoints == 24 * 60 * 60: # The cases of hourly, minute or second resolution data for exactly one day TODO: make this more precise
                        self.timeseries_format[filename] = 'daily'
                    else:
                        self.timeseries_format[filename] = 'yearly'
                    fp.write(
                        'New loadshape.{filename} npts= {npoints} interval=1 mult = (file={data_location})\n\n'.format(
                            filename=filename, npoints=npoints, data_location=scaled_data_location
                        )
                    )
                    self.timeseries_datasets[i.data_location] = filename

            # elif: In memory
            #     pass
                else:
                    pass #problem

                    #pass #TODO: write the timeseries data if it's in memory

    def write_loads(self, model):
        '''Write the loads to an OpenDSS file (Loads.dss by default).

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        fp = open(os.path.join(self.output_path, 'Loads.dss'), 'w')
        self.files_to_redirect.append('Loads.dss')

        for i in model.models:
            if isinstance(i, Load):

                #Name
                if hasattr(i, 'name') and i.name is not None:
                    fp.write('New Load.' + i.name)
                else:
                    continue

                #Connection type
                if hasattr(i, 'connection_type') and i.connection_type is not None:
                    if i.connection_type == 'Y':
                        fp.write(' conn=wye')
                    elif i.connection_type == 'D':
                        fp.write(' conn=delta')

                #Connecting element
                if hasattr(i, 'connecting_element') and i.connecting_element is not None:
                    fp.write(' bus1={bus}'.format(bus=i.connecting_element))
                    if hasattr(i, 'phase_loads') and i.phase_loads is not None:
                        for phase_load in i.phase_loads:
                            if hasattr(phase_load, 'phase') and phase_load.phase is not None:
                                fp.write('.{p}'.format(p=self.phase_mapping(phase_load.phase)))

                        if i.connection_type == 'D' and len(i.phase_loads) == 1:
                            if self.phase_mapping(i.phase_loads[0].phase) == 1:
                                fp.write('.2')
                            if self.phase_mapping(i.phase_loads[0].phase) == 2:
                                fp.write('.3')
                            if self.phase_mapping(i.phase_loads[0].phase) == 3:
                                fp.write('.1')

                #nominal voltage
                if hasattr(i, 'nominal_voltage') and i.nominal_voltage is not None:
                    fp.write(' kV={volt}'.format(volt=i.nominal_voltage * 10**-3))

                #Vmin
                if hasattr(i, 'vmin') and i.vmin is not None:
                    fp.write(' Vminpu={vmin}'.format(vmin=i.vmin))

                #Vmax
                if hasattr(i, 'vmax') and i.vmax is not None:
                    fp.write(' Vmaxpu={vmax}'.format(vmax=i.vmax))

                #positions (Not mapped)

                #KW
                total_P = 0
                if hasattr(i, 'phase_loads') and i.phase_loads is not None:

                    fp.write(' model={N}'.format(N=i.phase_loads[0].model))

                    for phase_load in i.phase_loads:
                        if hasattr(phase_load, 'p') and phase_load.p is not None:
                            total_P += phase_load.p
                    fp.write(' kW={P}'.format(P=total_P * 10**-3))

                #Kva
                total_Q = 0
                if hasattr(i, 'phase_loads') and i.phase_loads is not None:
                    for phase_load in i.phase_loads:
                        if hasattr(phase_load, 'q') and phase_load.q is not None:
                            total_Q += phase_load.q
                    fp.write(' kvar={Q}'.format(Q=total_Q * 10**-3))

                #phase_loads
                if hasattr(i, 'phase_loads') and i.phase_loads is not None:

                    #if i.connection_type=='Y':
                    fp.write(' Phases={N}'.format(N=len(i.phase_loads)))
                    #elif i.connection_type=='D' and len(i.phase_loads)==3:
                    #    fp.write(' Phases=3')
                    #elif i.connection_type=='D' and len(i.phase_loads)==2:
                    #    fp.write(' Phases=1')

                    for phase_load in i.phase_loads:

                        #P
                        #if hasattr(phase_load, 'p') and phase_load.p is not None:
                        #    fp.write(' kW={P}'.format(P=phase_load.p*10**-3))

                        #Q
                        #if hasattr(phase_load, 'q') and phase_load.q is not None:
                        #    fp.write(' kva={Q}'.format(Q=phase_load.q*10**-3))

                        #ZIP load model
                        if hasattr(phase_load, 'use_zip') and phase_load.use_zip is not None:
                            if phase_load.use_zip:

                                #Get the coefficients
                                if ((hasattr(i,'ppercentimpedance') and i.ppercentimpedance is not None) and
                                    (hasattr(i,'qpercentimpedance') and i.qpercentimpedance is not None) and
                                    (hasattr(i,'ppercentcurrent')   and i.ppercentcurrent   is not None) and
                                    (hasattr(i,'qpercentcurrent')   and i.qpercentcurrent   is not None) and
                                    (hasattr(i,'ppercentpower')     and i.ppercentpower     is not None) and
                                    (hasattr(i,'qpercentpower')     and i.qpercentpower     is not None)):

                                    fp.write(
                                        ' model=8 ZIPV=[%.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f]' % (
                                            i.ppercentimpedance, i.ppercentcurrent, i.ppercentpower, i.qpercentimpedance, i.qpercentcurrent,
                                            i.qpercentpower
                                        )
                                    )

                #fp.write(' model=1')

                # timeseries object
                if hasattr(i, 'timeseries') and i.timeseries is not None:
                    for ts in i.timeseries:
                        if hasattr(ts, 'data_location') and ts.data_location is not None and os.path.isfile(ts.data_location):
                            filename = self.timeseries_datasets[ts.data_location]
                            fp.write(' {ts_format}={filename}'.format(ts_format=self.timeseries_format[filename], filename=filename))
                        else:
                            pass
                            #TODO: manage the data correctly when it is only in memory

                fp.write('\n\n')

        return 1

    def write_regulators(self, model):
        '''Write the regulators to an OpenDSS file (Regulators.dss by default).

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        fp = open(os.path.join(self.output_path, 'Regulators.dss'), 'w')
        self.files_to_redirect.append('Regulators.dss')

        #It might be the case that we have to create new transformers from the regulators.
        #In this case, we build the strings and store them in a list.
        #At the end, we simply loop over the list to write all strings to transformers.dss
        transfo_creation_string_list = []

        for i in model.models:
            if isinstance(i, Regulator):

                if hasattr(i, 'name') and i.name is not None:
                    fp.write('New RegControl.{name}'.format(name=i.name))
                else:
                    continue

                #Connected transformer
                if hasattr(i, 'connected_transformer'):

                    #If we have a valid connected_transformer then job's easy...
                    if i.connected_transformer is not None:
                        fp.write(' transformer={trans}'.format(trans=i.connected_transformer))

                    #Otherwise, we have to create a new transformer and write it to the transformers file
                    else:

                        #Initialize the string:
                        transfo_creation_string = 'New Transformer.'

                        #Name:
                        transfo_name = 'trans_{}'.format(i.name) #Maybe not the best naming convention....
                        transfo_creation_string += transfo_name

                        #Number of Phases
                        if hasattr(i, 'windings') and i.windings is not None:
                            if hasattr(i.windings[0], 'phase_windings') and i.windings[0].phase_windings is not None:
                                try:
                                    transfo_creation_string += ' phases={}'.format(len(i.windings[0].phase_windings))
                                except:
                                    pass
                                phases = [self.phase_mapping(x.phase) for x in i.windings[0].phase_windings]
                                phase_string = reduce(lambda x, y: str(x) + '.' + str(y), phases)

                        #Number of windings
                        if hasattr(i, 'windings') and i.windings is not None:
                            try:
                                transfo_creation_string += ' windings={}'.format(len(i.windings))
                            except:
                                pass

                        #buses:
                        if (hasattr(i, 'from_element') and i.from_element is not None and hasattr(i, 'to_element') and i.to_element is not None):
                            transfo_creation_string += ' buses=({b1}.{p},{b2}.{p})'.format(b1=i.from_element, b2=i.to_element, p=phase_string)

                        #Conns
                        if hasattr(i, 'windings') and i.windings is not None:
                            conns = ' conns=('
                            for w, winding in enumerate(i.windings):
                                if hasattr(i.windings[w], 'connection_type') and i.windings[w].connection_type in ['Y', 'D', 'Z']:
                                    mapp = {'Y': 'Wye', 'D': 'Delta', 'Z': 'Zigzag'}
                                    conns += mapp[i.windings[w].connection_type] + ', '
                            conns = conns[:-2]
                            conns += ')'
                            transfo_creation_string += conns

                        #kvs
                        if hasattr(i, 'windings') and i.windings is not None:
                            kvs = ' kvs=('
                            for w, winding in enumerate(i.windings):
                                if hasattr(i.windings[w], 'nominal_voltage'):
                                    kvs += str(i.windings[w].nominal_voltage) + ', '
                            kvs = kvs[:-2]
                            kvs += ')'
                            transfo_creation_string += kvs

                        #kvas
                        if hasattr(i, 'windings') and i.windings is not None:
                            kvas = ' kvas=('
                            for w, winding in enumerate(i.windings):
                                if hasattr(i.windings[w], 'rated_power') and i.windings[w].rated_power is not None:
                                    kvas += str(i.windings[w].rated_power * 10**-3) + ', '
                            kvas = kvas[:-2]
                            kvas += ')'
                            transfo_creation_string += kvas

                        #emergency_power
                        if hasattr(i, 'windings') and i.windings is not None:
                            if hasattr(i.windings[0], 'emergency_power') and i.windings[0].emergency_power is not None:
                                transfo_creation_string += ' EmerghKVA={}'.format(i.windings[0].emergency_power)

                        #reactances:
                        if hasattr(i, 'reactances') and i.reactances is not None:
                            #XHL:
                            try:
                                if isinstance(i.reactances[0], (int, float)):
                                    transfo_creation_string += ' XHL={}'.format(i.reactances[0])
                            except:
                                self.logger.warning('Could not extract XHL from regulator {name}'.format(name=i.name))
                                pass
                            #XLT:
                            try:
                                if isinstance(i.reactances[1], (int, float)):
                                    transfo_creation_string += ' XLT={}'.format(i.reactances[1])
                            except:
                                self.logger.warning('Could not extract XLT from regulator {name}'.format(name=i.name))
                                pass
                            #XHT:
                            try:
                                if isinstance(i.reactances[2], (int, float)):
                                    transfo_creation_string += ' XHT={}'.format(i.reactances[2])
                            except:
                                self.logger.warning('Could not extract XHT from regulator {name}'.format(name=i.name))
                                pass

                        #Store the string in the list
                        transfo_creation_string_list.append(transfo_creation_string)

                        fp.write(' transformer={trans}'.format(trans=transfo_name))

                #Winding
                if hasattr(i, 'winding') and i.winding is not None:
                    fp.write(' winding={w}'.format(w=i.winding))

                #CTprim
                if hasattr(i, 'ct_prim') and i.ct_prim is not None:
                    fp.write(' CTprim={CT}'.format(CT=i.ct_prim))

                #noload_loss
                if hasattr(i, 'noload_loss') and i.noload_loss is not None:
                    fp.write(' %noLoadLoss={nL}'.format(NL=i.noload_loss))

                #Delay
                if hasattr(i, 'delay') and i.delay is not None:
                    fp.write(' delay={d}'.format(d=i.delay))

                #highstep
                if hasattr(i, 'highstep') and i.highstep is not None:
                    fp.write(' maxtapchange={high}'.format(high=i.highstep))

                #lowstep (Not mapped)

                #pt ratio
                if hasattr(i, 'pt_ratio') and i.pt_ratio is not None:
                    fp.write(' ptratio={PT}'.format(PT=i.pt_ratio))

                #ct_ratio (Not mapped)

                #phase shift (Not mapped)

                #ltc (Not mapped)

                #bandwidth
                if hasattr(i, 'bandwidth') and i.bandwidth is not None:
                    fp.write(' band={b}'.format(b=i.bandwidth))

                #band center
                if hasattr(i, 'bandcenter') and i.bandcenter is not None:
                    fp.write(' vreg={vreg}'.format(vreg=i.bandcenter))

                #Pt phase
                if hasattr(i, 'pt_phase') and i.pt_phase is not None:
                    fp.write(' Ptphase={PT}'.format(PT=self.phase_mapping(i.pt_phase)))

                #Voltage limit
                if hasattr(i, 'voltage_limit') and i.voltage_limit is not None:
                    fp.write(' vlimit={vlim}'.format(vlim=i.voltage_limit))

                #X (Store in the Phase Windings of the transformer)
                if i.name in self.compensator:
                    if 'X' in self.compensator[i.name]:
                        if len(self.compensator[i.name]['X']) == 1:
                            fp.write(' X={x}'.format(x=list(self.compensator[i.name]['X'])[0]))
                        else:
                            self.logger.warning(
                                '''Compensator_x not the same for all windings of transformer {name}.
                                                   Using the first value for regControl {name2}.'''
                                .format(name=i.connected_transformer, name2=i.name)
                            )
                            fp.write(' X={x}'.format(x=list(self.compensator[i.name]['X'])[0]))

                #R (Store in the Phase Windings of the transformer)
                if i.name in self.compensator:
                    if 'R' in self.compensator[i.name]:
                        if len(self.compensator[i.name]['R']) == 1:
                            fp.write(' R={r}'.format(r=list(self.compensator[i.name]['R'])[0]))
                        else:
                            self.logger.warning(
                                '''Compensator_r not the same for all windings of transformer {name}.
                                                   Using the first value for regControl {name2}.'''
                                .format(name=i.connected_transformer, name2=i.name)
                            )
                            fp.write(' R={r}'.format(r=list(self.compensator[i.name]['R'])[0]))

                fp.write('\n\n')

        #If we have new transformers to add...
        if len(transfo_creation_string_list) > 0:
            with open(os.path.join(self.output_path, 'Transformers.dss'), 'a') as f:
                for trans_string in transfo_creation_string_list:
                    f.write(trans_string)
                    f.write('\n\n')

        return 1

    def write_capacitors(self, model):
        '''Write the capacitors to an OpenDSS file (Capacitors.dss by default).

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        fp = open(os.path.join(self.output_path, 'Capacitors.dss'), 'w')
        self.files_to_redirect.append('Capacitors.dss')

        for i in model.models:

            if isinstance(i, Capacitor):

                #Name
                if hasattr(i, 'name') and i.name is not None:
                    fp.write('New Capacitor.{name}'.format(name=i.name))
                else:
                    continue

                #Connecting element
                if i.connecting_element is not None:
                    fp.write(' Bus1=' + i.connecting_element)

                    # For a 3-phase capbank we don't add any suffixes to the output.
                    if hasattr(i, 'phase_capacitors') and i.phase_capacitors is not None and len(i.phase_capacitors) != 3:
                        for phase_capacitor in i.phase_capacitors:

                            if hasattr(phase_capacitor, 'phase') and phase_capacitor.phase is not None:
                                if phase_capacitor.phase == 'A':
                                    fp.write('.1')
                                if phase_capacitor.phase == 'B':
                                    fp.write('.2')
                                if phase_capacitor.phase == 'C':
                                    fp.write('.3')

                #Phases
                if hasattr(i, 'phase_capacitors') and i.phase_capacitors is not None:
                    fp.write(' phases={N}'.format(N=len(i.phase_capacitors)))

                #nominal_voltage
                if hasattr(i, 'nominal_voltage') and i.nominal_voltage is not None:
                    fp.write(' Kv={volt}'.format(volt=i.nominal_voltage * 10**-3)) #OpenDSS in Kvolts

                #connection type
                if hasattr(i, 'connection_type') and i.connection_type is not None:
                    if i.connection_type == 'Y':
                        fp.write(' conn=Wye')
                    elif i.connection_type == 'D':
                        fp.write(' conn=delta')
                    else:
                        self.logger.error('Unknown connection type in capacitor {name}'.format(name=i.name))

                #Rated kvar
                #In DiTTo, this is splitted accross phase_capacitors
                #We thus have to sum them up
                total_var = 0
                if hasattr(i, 'phase_capacitors') and i.phase_capacitors is not None:
                    for phase_capacitor in i.phase_capacitors:
                        if hasattr(phase_capacitor, 'var') and phase_capacitor.var is not None:
                            try:
                                total_var += phase_capacitor.var
                            except:
                                self.logger.error('Cannot compute Var of capacitor {name}'.format(name=name))
                                pass
                    total_var *= 10**-3 #OpenDSS in Kvar
                    fp.write(' Kvar={kvar}'.format(kvar=total_var))

                #We create a CapControl if we have valid input
                #values that indicate that we should
                create_capcontrol = False
                if ((hasattr(i, 'name') and i.name is not None) and
                    ((hasattr(i, 'delay') and i.delay is not None) or
                     (hasattr(i, 'mode') and i.mode is not None) or
                     (hasattr(i, 'low') and i.low is not None) or
                     (hasattr(i, 'high') and i.high is not None) or
                     (hasattr(i, 'pt_ratio') and i.pt_ratio is not None) or
                     (hasattr(i, 'ct_ratio') and i.ct_ratio is not None) or
                     (hasattr(i, 'pt_phase') and i.pt_phase is not None)
                    )):
                    create_capcontrol = True

                #Create CapControl
                if create_capcontrol:
                    fp.write('\n\nNew CapControl.{name} Capacitor={name}'.format(name=i.name))

                    #Element (CONTROL)
                    if hasattr(i, 'measuring_element') and i.measuring_element is not None:
                        fp.write(' Element={elt}'.format(elt=i.measuring_element))

                    #Delay (CONTROL)
                    if hasattr(i, 'delay') and i.delay is not None:
                        fp.write(' delay={d}'.format(d=i.delay))

                    #mode (CONTROL)
                    if hasattr(i, 'mode') and i.mode is not None:
                        fp.write(' Type={m}'.format(m=self.mode_mapping(i.mode)))

                    #Low (CONTROL)
                    if hasattr(i, 'low') and i.low is not None:
                        fp.write(' Vmin={vmin}'.format(vmin=i.low))

                    #high (CONTROL)
                    if hasattr(i, 'high') and i.high is not None:
                        fp.write(' Vmax={vmax}'.format(vmax=i.high))

                    #Pt ratio (CONTROL)
                    if hasattr(i, 'pt_ratio') and i.pt_ratio is not None:
                        fp.write(' Ptratio={PT}'.format(PT=i.pt_ratio))

                    #Ct ratio (CONTROL)
                    if hasattr(i, 'ct_ratio') and i.ct_ratio is not None:
                        fp.write(' Ctratio={CT}'.format(CT=i.ct_ratio))

                    #Pt phase (CONTROL)
                    if hasattr(i, 'pt_phase') and i.pt_phase is not None:
                        fp.write(' PTPhase={PT}'.format(PT=self.phase_mapping(i.pt_phase)))

                fp.write('\n\n')

        return 1

    def write_lines(self, model):
        '''Write the lines to an OpenDSS file (Lines.dss by default).

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        fp = open(os.path.join(self.output_path, 'Lines.dss'), 'w')
        self.files_to_redirect.append('Lines.dss')

        for i in model.models:
            if isinstance(i, Line):

                #Name
                if hasattr(i, 'name') and i.name is not None:
                    fp.write('New Line.' + i.name)
                else:
                    continue

                #Set the units in miles for comparison (IEEE 13 nodes feeder)
                fp.write(' Units=mi')

                #Length
                if hasattr(i, 'length') and i.length is not None:
                    fp.write(' Length={length}'.format(length=self.convert_from_meters(np.real(i.length), u'mi')))

                #nominal_voltage (Not mapped)

                #line type (Not mapped)

                #from_element
                if hasattr(i, 'from_element') and i.from_element is not None:
                    fp.write(' bus1={from_el}'.format(from_el=i.from_element))
                    if hasattr(i, 'wires') and i.wires is not None:
                        for wire in i.wires:
                            if hasattr(wire, 'phase') and wire.phase is not None and wire.phase not in ['N', 'N1', 'N2']:
                                fp.write('.{p}'.format(p=self.phase_mapping(wire.phase)))

                #to_element
                if hasattr(i, 'to_element') and i.to_element is not None:
                    fp.write(' bus2={to_el}'.format(to_el=i.to_element))
                    if hasattr(i, 'wires') and i.wires is not None:
                        for wire in i.wires:
                            if hasattr(wire, 'phase') and wire.phase is not None and wire.phase not in ['N', 'N1', 'N2']:
                                fp.write('.{p}'.format(p=self.phase_mapping(wire.phase)))

                #Faulrate
                #Can also be defined through the linecodes (check linecodes_flag)
                if hasattr(i, 'faultrate') and i.faultrate is not None and not self.linecodes_flag:
                    fp.write(' Faultrate={fr}'.format(fr=i.faultrate))

                #Rmatrix, Xmatrix, and Cmatrix
                #Can also be defined through the linecodes (check linecodes_flag)
                if (((hasattr(i, 'impedance_matrix') and i.impedance_matrix is not None) or
                    (hasattr(i, 'capacitance_matrix') and i.capacitance_matrix is not None)) and not self.linecodes_flag):
                    fp.write(' ' + self.serialize_line(i))

                #is_fuse (Not mapped)

                #is_switch
                if hasattr(i, 'is_switch') and i.is_switch is not None:
                    if i.is_switch == 1:
                        fp.write(' switch=y')
                    else:
                        fp.write(' switch=n')

                #N_phases
                if hasattr(i, 'wires') and i.wires is not None:
                    fp.write(' phases=' + str(len(i.wires) - 1)) #Do not count the neutral

                #is_banked (Not mapped)

                #positions (Not mapped)

                if self.linecodes_flag:
                    ser = self.serialize_line(i)
                    fp.write(' Linecode=' + self.all_linecodes[ser])

                if not self.linecodes_flag and hasattr(i, 'wires') and i.wires is not None:
                    ser = self.serialize_line_geometry(i.wires)
                    fp.write(' geometry=' + self.all_geometries[ser])
                '''
                #TODO: write numbers based on phase (e.g. A/B/C = 1,2,3)
                if i.from_element is not None:
                    fp.write(' bus1='+i.from_element)
                    if i.wires is None:
                        for cnt in range(num_phases):
                            fp.write('.'+str(cnt))
                    else:
                        for wire in i.wires:
                            if wire.phase == 'A':
                                fp.write('.1')
                            if wire.phase == 'B':
                                fp.write('.2')
                            if wire.phase == 'C':
                                fp.write('.3')



                if i.to_element is not None:
                    fp.write(' bus2='+i.to_element)
                    if i.wires is None:
                        for cnt in rage(1,num_phases+1):
                            fp.write('.'+str(cnt))
                    else:
                        for cnt in range(1,len(i.wires)+1):
                            fp.write('.'.str(cnt))



                if not linecodes and i.wires is not None:
                    ser = self.serialize_line_geometry(i.wires)
                    fp.write(' geometry='+self.all_geometries[ser])

                if i.length is not None:
                    fp.write(' length='+str(i.length))

                if i.num_phases is not None:
                    fp.write(' phases='+str(i.num_phases))


                # These are already defined in LineCodes but are also allowed to be defined here.
    #            if i.resistance is not None:
    #                fp.write(' r1='+str(i.resistance))
    #
    #            if i.reactance is not None:
    #                fp.write(' x1='+str(i.reactance))
    #
    #            if i.resistance0 is not None:
    #                fp.write(' r0='+str(i.resistance0))
    #
    #            if i.reactance0 is not None:
    #                fp.write(' x0='+str(i.reactance0))
    #
    #            if i.ampacity is not None:
    #                fp.write(' normamps='+str(i.ampacity))
    #
    #            if i.emergency_ampacity is not None:
    #                fp.write(' emergamps='+str(i.emergency_ampacity))


                if i.is_switch is not None:
                    if i.is_switch == 1:
                        fp.write(' switch=y')
                    else:
                        fp.write(' switch=n')

                '''

                fp.write('\n\n')
        return 1

    def write_wiredata(self, model):
        '''Write the wire data to an OpenDSS file (WireData.dss by default).

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

'''
        cnt = 1
        for i in model.models:
            if isinstance(i, Wire):
                ser = self.serialize_wire(i)
                if not ser in self.all_wires:
                    self.all_wires[ser] = 'Code' + str(cnt)
                    cnt += 1

        fp = open(os.path.join(self.output_path, 'WireData.dss'), 'w')
        self.files_to_redirect.append('WireData.dss')
        for wire in self.all_wires:
            fp.write('New WireData.' + self.all_wires[wire] + wire + '\n')

        return 1

    def write_linegeometry(self, model):
        '''Write the Line geometries to an OpenDSS file (LineGeometry.dss by default).

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

.. warning:: This must be called after write_wiredata()

'''
        for i in model.models:
            if isinstance(i, Line):
                if hasattr(i, 'wires') and i.wires is not None:
                    ser = self.serialize_line_geometry(i.wires)
                    name = str(len(i.wires) - 1) + 'PH'
                    for wire in i.wires:
                        seri = self.serialize_wire(wire)
                        if seri != '':
                            name += '_' + self.all_wires[seri]
                    self.all_geometries[ser] = name

        fp = open(os.path.join(self.output_path, 'LineGeometry.dss'), 'w')
        self.files_to_redirect.append('LineGeometry.dss')
        for geometry in self.all_geometries:
            fp.write('New LineGeometry.' + self.all_geometries[geometry] + geometry + '\n')

        return 1

    def write_linecodes(self, model):
        '''Write the linecodes to an OpenDSS file (Linecodes.dss by default).

:param model: DiTTo model
:type model: DiTTo model
:returns: 1 for success, -1 for failure
:rtype: int

.. note::

    Since there is no linecode object equivalent in DiTTo, we have to re-construct them from the line objects.
    Therefore, when doing DSS--->DiTTo--->DSS for the same circuit, the new linecodes will have different names than the old ones.

'''
        cnt = 0
        for i in model.models:
            if isinstance(i, Line):

                ser = self.serialize_line(i)

                if not ser in self.all_linecodes:

                    nameclass = ''

                    if hasattr(i, 'wires') and i.wires is not None:
                        phase_wires = [w for w in i.wires if w.phase in ['A', 'B', 'C']]
                        nameclass += str(len(phase_wires)) + 'P_'

                    if hasattr(i, 'line_type') and i.line_type == 'overhead':
                        nameclass += 'OH_'

                    if hasattr(i, 'line_type') and i.line_type == 'underground':
                        nameclass += 'UG_'

                    self.all_linecodes[ser] = '{class_}Code{N}'.format(class_=nameclass, N=cnt)
                    cnt += 1

        fp = open(os.path.join(self.output_path, 'Linecodes.dss'), 'w')
        self.files_to_redirect.append('Linecodes.dss')
        for linecode, linecode_data in self.all_linecodes.items():
            fp.write('New Linecode.{linecode_data} {linecode}\n'.format(linecode=linecode, linecode_data=linecode_data))

        return 1

    def serialize_line(self, line):
        '''This function is used to associate lines to linecodes or linegeometry.
Multiple lines can share the same parameters (like length, resistance matrix,...), such that these lines will be be associated with the same linecode.

:param line: Line diTTo object
:type line: Line diTTo object
:returns: Line string
:rtype: str

'''
        result = ''

        if hasattr(line, 'units') and line.units is not None:
            uni = line.units
        else:
            uni = u'ft'

        #N_phases
        if hasattr(line, 'wires') and line.wires is not None and self.linecodes_flag:
            phase_wires = [w for w in line.wires if w.phase in ['A', 'B', 'C']]
            result += 'nphases={N} '.format(N=len(phase_wires))

        #faultrate
        if hasattr(line, 'faultrate') and line.faultrate is not None and self.linecodes_flag:
            result += 'Faultrate={f} '.format(f=line.faultrate)

        #If we have the impedance matrix, we need to extract both
        #the resistance and reactance matrices
        if hasattr(line, 'impedance_matrix') and line.impedance_matrix is not None:
            #Use numpy arrays since it is much easier for complex numbers
            try:
                Z = np.array(line.impedance_matrix)
                R = np.real(Z) #Resistance matrix
                X = np.imag(Z) #Reactance  matrix
            except:
                self.logger.error('Problem with impedance matrix in line {name}'.format(name=line.name))

            result += 'Rmatrix=('
            for row in R:
                for elt in row:
                    result += '{e} '.format(e=self.convert_from_meters(np.real(elt), uni, inverse=True))
                result += '| '
            result = result[:-2] #Remove the last "| " since we do not need it
            result += ') '

            result += 'Xmatrix=('
            for row in X:
                for elt in row:
                    result += '{e} '.format(e=self.convert_from_meters(np.real(elt), uni, inverse=True))
                result += '| '
            result = result[:-2] #Remove the last "| " since we do not need it
            result += ') '

        if hasattr(line, 'capacitance_matrix') and line.capacitance_matrix is not None and line.capacitance_matrix != []:
            C = np.array(line.capacitance_matrix)
            result += 'Cmatrix=('
            for row in C:
                for elt in row:
                    result += '{e} '.format(e=self.convert_from_meters(np.real(elt), uni, inverse=True))
                result += '| '
            result = result[:-2] #Remove the last "| " since we do not need it
            result += ') '

        #Ampacity
        if hasattr(line, 'wires') and line.wires is not None and len(line.wires) > 0 and hasattr(line.wires[0], 'ampacity'
                                                                                                 ) and line.wires[0].ampacity is not None:
            result += ' normamps={na}'.format(na=line.wires[0].ampacity)

        #Emergency ampacity
        if hasattr(line, 'wires') and line.wires is not None and len(line.wires) > 0 and hasattr(line.wires[0], 'ampacity_emergency'
                                                                                                 ) and line.wires[0].ampacity_emergency is not None:
            result += ' emergamps={emer}'.format(emer=line.wires[0].ampacity_emergency)

        result += ' units={}\n'.format(uni)
        return result

    def serialize_wire(self, wire):
        '''Takes a wire diTTo object as input and outputs the OpenDSS string.

:param wire: Wire diTTo object
:type wire: Wire diTTo object
:returns: Wire string
:rtype: str

'''
        result = ''

        #GMR
        if hasattr(wire, 'gmr') and wire.gmr is not None:
            result += ' GMRac={gmr}'.format(gmr=wire.gmr)
            result += ' GMRunits=m' #Let OpenDSS know we are in meters here

        #Diameter
        if hasattr(wire, 'diameter') and wire.diameter is not None:
            result += ' Diam={d}'.format(d=wire.diameter)
            result += ' Radunits=m' #Let OpenDSS know we are in meters here

        #Ampacity
        if hasattr(wire, 'ampacity') and wire.ampacity is not None:
            result += ' normamps={na}'.format(na=wire.ampacity)

        #Emergency ampacity
        if hasattr(wire, 'ampacity_emergency') and wire.ampacity_emergency is not None:
            result += ' emergamps={emer}'.format(emer=wire.ampacity_emergency)

        #Resistance
        if hasattr(wire, 'resistance') and wire.resistance is not None:
            result += ' Rac={rac}'.format(rac=wire.resistance)

        return result

    def serialize_line_geometry(self, wire_list):
        '''Takes a list of wires as input and outputs the lineGeometry string.

:param wire_list: List of Wire diTTo objects
:type wire_list: list
:returns: LineGeometry string
:rtype: str

.. note:: This model keeps the line neutrals in and doesn't reduce them out

'''
        result = ''

        result += ' nconds={N}'.format(N=len(wire_list))

        phase_wires = [w for w in wire_list if w.phase in ['A', 'B', 'C']]

        result += ' nphases={N}'.format(N=len(phase_wires))

        cond = 1

        for wire in wire_list:
            #serialize the wires
            ser = self.serialize_wire(wire)
            #It can happen that the wire exists, but all
            #fields handled by serialize_wires() are empty
            if ser != '':
                wire_name = self.all_wires[ser]
                result += ' cond={N}'.format(N=cond)
                cond += 1
                result += ' wire={name}'.format(name=wire_name)

            if hasattr(wire, 'X') and wire.X is not None:
                result += ' x={x}'.format(x=wire.X)

            if hasattr(wire, 'Y') and wire.Y is not None:
                result += ' h={h}'.format(h=wire.Y)

        result += ' reduce=n'

        return result


    def write_master_file(self,model):
        '''Write the master.dss file.
        '''
        with open(os.path.join(self.output_path,'master.dss'), 'w') as fp:
            fp.write('Clear\n\nNew Circuit.Name ')
            for obj in model.models:
                if isinstance(obj,PowerSource) and obj.is_sourcebus==1:
                    fp.write('bus1={name} pu=1.0'.format(name=obj.name))

                    if hasattr(obj,'nominal_voltage') and obj.nominal_voltage is not None:
                        fp.write(' basekV={volt}'.format(volt=obj.nominal_voltage*10**-3)) #DiTTo in volts

                    if hasattr(obj, 'positive_sequence_impedance') and obj.positive_sequence_impedance is not None:
                        R1=obj.positive_sequence_impedance.real
                        X1=obj.positive_sequence_impedance.imag
                        fp.write(' R1={R1} X1={X1}'.format(R1=R1,X1=X1))

                    if hasattr(obj, 'zero_sequence_impedance') and obj.zero_sequence_impedance is not None:
                        R0=obj.zero_sequence_impedance.real
                        X0=obj.zero_sequence_impedance.imag
                        fp.write(' R0={R0} X0={X0}'.format(R0=R0,X0=X0))

            fp.write('\n\n')
            for file in self.files_to_redirect:
                fp.write('Redirect {file}\n'.format(file=file))

            fp.write('\nCalcvoltagebases\n\n')
            fp.write('Buscoords buscoords.dss')



