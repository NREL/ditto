import os

#from __future__ import absolute_import, division, print_function
#from builtins import super, range, zip, round, map

import math
import logging

import numpy as np
#import pandas as pd

from functools import reduce

# DiTTo imports
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
from ditto.models.photovoltaic import Photovoltaic

from ditto.writers.abstract_writer import AbstractWriter
#
logger = logging.getLogger(__name__)

class Writer(AbstractWriter):
    network = {}
    
    def __init__(self, **kwargs):
        """Constructor for the OD&O writer."""
#        self.timeseries_datasets = {}
#        self.timeseries_format = {}
#        self.all_linecodes = {}
#        self.all_wires = {}
#        self.all_geometries = {}
#        self.compensator = {}
#        self.all_cables = {}
#
#        self.files_to_redirect = []
#
#        self.write_taps = False
#        self.separate_feeders = False
#        self.separate_substations = False
        self.verbose = False

        self.output_filenames = {
            "network": "network.json"
        }

        # Call super
        super(Writer, self).__init__(**kwargs)

        self._baseKV_ = set()

        self.baseMVA = kwargs['baseMVA']
        self.basekV = kwargs['basekV']

        logger.info("DiTTo--->OpenDSS writer successfuly instanciated.")

    def write(self, model, **kwargs):
        """General writing function responsible for calling the sub-functions.
        """
        # Verbose print the progress
        if "verbose" in kwargs and isinstance(kwargs["verbose"], bool):
            self.verbose = kwargs["verbose"]
        else:
            self.verbose = False

        # Calling Write_Buses()
        self.network['bus'] = self.write_buses(model)
        
        # Calling Write_loads()
        self.network['load'] = self.write_loads(model)
        
        # Calling Write_generators()
        self.network['generator'] = self.write_generators(model)

        # Write branches
        logger.info("Writing the branches...")
        if self.verbose:
            logger.debug("Writing the branches...")
        self.network['branch'] = self.write_branches(model)
        
        # Write shunts
        logger.info("Writing the shunts...")
        if self.verbose:
            logger.debug("Writing the shunts...")
        self.network['shunt'] = self.write_shunt(model)
        
        # Write storage
        logger.info("Writing the storage...")
        if self.verbose:
            logger.debug("Writing the storage...")
        self.network['storage'] = self.write_storage(model)

#        self.network = s
#        s = self.write_buses(model)
        
#        if self.verbose and s != -1:
#            logger.debug("Successful!")
            
        return self.network

    #
    def write_branches(self, model):
        
        branch_data = {}
        index = 0
        m_info = model.models
        m_idx = 0
        l_count = 0
        xfmr_count = 0
        baseMVA = self.baseMVA
                
        for i in model.models:
            
#            if index == 15:
#                print(index)
                    
            if isinstance(i, Line) or isinstance(i, PowerTransformer):
        
                index += 1
#                if index == 16:
#                    print(index)
                               
                if isinstance(i, Line):
                    l_count += 1                   
                    nominal_voltage = i.nominal_voltage
                    basekV = nominal_voltage/1000.0
                    baseZ = basekV**2/baseMVA
                    baseY = 1/baseZ
                    baseA = baseMVA/(np.sqrt(3)*basekV)*1000.0
                    bus_data = self.network['bus']
                    name = i.name
                    
                    f_bus0 = i.from_element
                    t_bus0 = i.to_element
                    ## Finding the Indexes of the buses to which the branch is connected
                    for j in bus_data:
                        if bus_data[j]["name"] == f_bus0:
                            f_bus = bus_data[j]["index"]
                            break
                    
                    for j in bus_data:
                        if bus_data[j]["name"] == t_bus0:
                            t_bus = bus_data[j]["index"]
                            break
                    
                    length = i.length
                    
                    # Default assumed values, near zero conductance = very high impedance
                    g_fr = [0.0, 0.0, 0.0]
                    g_to = [0.0, 0.0, 0.0]
                    b_fr = [0.0, 0.0, 0.0]
                    b_to = [0.0, 0.0, 0.0]
                    br_r = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).reshape((3, 3))
                    br_x = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).reshape((3, 3))
                    I_rating = [0.0, 0.0, 0.0]

                    if hasattr(i, "wires") and i.wires is not None:
                        nphases = len(i.wires)
                    
#                    if name == '684652':
#                        print(name)
                        
                    # For 3-ph lines
                    if nphases == 3:
                        
                        # total branch impedance in p.u.
                        br_zmatrix = np.array(i.impedance_matrix)*length / baseZ
                        br_cmatrix = np.array(i.capacitance_matrix)*length
                        br_cdiag = np.diagonal(br_cmatrix)
    #                    br_z = np.mean(np.diagonal(br_zmatrix))  # if only positive seq. is considered              
                        br_r = np.real(br_zmatrix)
                        br_x = np.imag(br_zmatrix)
    #                    br_c = np.real(np.mean(np.diagonal(br_cmatrix)))
        
#                        if index == 15:
#                            print("a")
                        
                        br_b = 2*np.pi*60*np.abs(br_cdiag)*(10**-9) / baseY
                        br_b_half = br_b[0]/2.0
                        
                        b_fr = [br_b_half, br_b_half, br_b_half]
                        b_to = [br_b_half, br_b_half, br_b_half]
                    
                        for wire in i.wires:
                            if (
                                hasattr(wire, "phase")
                                and wire.phase is not None
                                and wire.phase not in ["N", "N1", "N2"]
                            ):
                                ph = wire.phase
                                    
                                if ph.lower() == 'a':
                                    I_rating[0] = wire.ampacity / baseA
                                elif ph.lower() == 'b':
                                    I_rating[1] = wire.ampacity / baseA
                                elif ph.lower() == 'c':
                                    I_rating[2] = wire.ampacity / baseA
                                                                        
                    # For 1-ph lines
                    elif nphases == 1:
                        
                        for wire in i.wires:
                            if (
                                hasattr(wire, "phase")
                                and wire.phase is not None
                                and wire.phase not in ["N", "N1", "N2"]
                            ):
                                ph = wire.phase
                                    
                                if ph.lower() == 'a':
                                    ph_num = 0
                                elif ph.lower() == 'b':
                                    ph_num = 1
                                elif ph.lower() == 'c':
                                    ph_num = 2
                                    
                                # total branch impedance in p.u.
                                br_zmatrix = np.array(i.impedance_matrix)*length / baseZ
                                br_cmatrix = np.array(i.capacitance_matrix)*length
                                br_cdiag = np.diagonal(br_cmatrix)
                #                    br_z = np.mean(np.diagonal(br_zmatrix))  # if only positive seq. is considered              
                                br_r[ph_num,ph_num] = np.real(br_zmatrix)
                                br_x[ph_num,ph_num] = np.imag(br_zmatrix)
                #                    br_c = np.real(np.mean(np.diagonal(br_cmatrix)))
                                
#                                if index == 8:
#                                    print("a")
                                        
                                br_b = 2*np.pi*60*np.abs(br_cdiag)*(10**-9) / baseY
                                    
                                b_fr[ph_num] = br_b[0]/2.0
                                b_to[ph_num] = br_b[0]/2.0
                                
                                I_rating[ph_num] = wire.ampacity / baseA
                                
                    # For 2-ph lines
                    elif nphases == 2:
                        
                        count = 0
                        ph_num = []
                        for wire in i.wires:
                            if (
                                hasattr(wire, "phase")
                                and wire.phase is not None
                                and wire.phase not in ["N", "N1", "N2"]
                            ):
                                ph = wire.phase
                                count += 1
                                    
                                if ph.lower() == 'a':
                                    ph_num.append(0)
                                elif ph.lower() == 'b':
                                    ph_num.append(1)
                                elif ph.lower() == 'c':
                                    ph_num.append(2)
                                
                                if count == 2:
                                    # total branch impedance in p.u.
                                    br_zmatrix = np.array(i.impedance_matrix)*length / baseZ
                                    br_cmatrix = np.array(i.capacitance_matrix)*length
                                    br_cdiag = np.diagonal(br_cmatrix)
                                    
                                    br_r[ph_num[0], ph_num[0]] = np.real(br_zmatrix)[0,0]
                                    br_r[ph_num[0], ph_num[1]] = np.real(br_zmatrix)[0,1]
                                    br_r[ph_num[1], ph_num[0]] = np.real(br_zmatrix)[1,0]
                                    br_r[ph_num[1], ph_num[1]] = np.real(br_zmatrix)[1,1]
                                    
                                    br_x[ph_num[0], ph_num[0]] = np.imag(br_zmatrix)[0,0]
                                    br_x[ph_num[0], ph_num[1]] = np.imag(br_zmatrix)[0,1]
                                    br_x[ph_num[1], ph_num[0]] = np.imag(br_zmatrix)[1,0]
                                    br_x[ph_num[1], ph_num[1]] = np.imag(br_zmatrix)[1,1]
                                    
#                                    if index == 8:
#                                        print("a")
                                    
                                    br_b = 2*np.pi*60*np.abs(br_cdiag)*(10**-9) / baseY
                                        
                                    b_fr[ph_num[0]] = br_b[0]/2.0
                                    b_fr[ph_num[1]] = br_b[1]/2.0
                                    b_to[ph_num[0]] = br_b[0]/2.0
                                    b_to[ph_num[1]] = br_b[1]/2.0
                                    
                                I_rating[ph_num[count-1]] = wire.ampacity / baseA
                                
                    current_rating_a0 = I_rating[0]
                    current_rating_b0 = I_rating[1]
                    current_rating_c0 = I_rating[2]
                    current_rating_a = [current_rating_a0,current_rating_b0,current_rating_c0]
                    
                    # 60 degrees = 1.0472 radians
                    angmin = [-1.0472, -1.0472, -1.0472]
                    angmax = [1.0472, 1.0472, 1.0472]
                    shift = [0.0, 0.0, 0.0]
                    tap = [1.0, 1.0, 1.0]
                    transformer = 'false'
                    status = 1
                    
#                    if index == 8:
#                        print("a")
                    
                    #Converting the arrays to lists for writing to json in a correct way
                    br_r = br_r.tolist()
                    br_x = br_x.tolist()                    
                    b_fr = list(b_fr)
                    b_to = list(b_to)
                    g_fr = list(g_fr)
                    g_to = list(g_to)
                    
#                    if index == 8:
#                        print("a")
                    
                    data = dict(index=index,name=name,length=length,nominal_voltage=nominal_voltage,f_bus=f_bus,t_bus=t_bus,br_r=br_r,br_x=br_x,g_fr=g_fr,g_to=g_to,b_fr=b_fr,b_to=b_to,current_rating_a=current_rating_a,angmin=angmin,angmax=angmax,shift=shift,tap=tap,transformer=transformer,status=status,has_switch=1,switch_status=1)
                    branch_data[str(index)] = data
                
                elif isinstance(i, PowerTransformer):
                    
                    """ Assumptions: Transformers are assumed to be 3ph in computing winding current rating """
                    
                    xfmr_count += 1
                    name = i.name
                    length = 0   
                    bus_data = self.network['bus']
                    f_bus0 = i.from_element
                    t_bus0 = i.to_element
                    
#                    if name == 'xfm1':
#                        print("a")
#                        
#                    if name in ['reg1','reg2','reg3']:
#                        print(index)
                    
                    ## Finding the Indexes of the buses to which the branch is connected
                    for j in bus_data:
                        if bus_data[j]["name"] == f_bus0:
                            f_bus = bus_data[j]["index"]
                            break
                    
                    for j in bus_data:
                        if bus_data[j]["name"] == t_bus0:
                            t_bus = bus_data[j]["index"]
                            break
                    
                    nominal_voltages = []
                    # 60 degrees = 1.0472 radians
                    angmin = [-1.0472, -1.0472, -1.0472]
                    angmax = [1.0472, 1.0472, 1.0472]               
                    shift = [0.0, 0.0, 0.0]
                    tap = [1.0, 1.0, 1.0]
                    transformer = 'true'
                    status = 1
                    
                    # Default assumed values, near zero conductance = very high impedance
                    g_fr = [0.0, 0.0, 0.0]
                    g_to = [0.0, 0.0, 0.0]
                    b_fr = [0.001, 0.001, 0.001]
                    b_to = [0.001, 0.001, 0.001]

                    I_rating1 = [0.0, 0.0, 0.0]
                    I_rating2 = [0.0, 0.0, 0.0]
                    br_r = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).reshape((3, 3))
                    br_x = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]).reshape((3, 3))
                   
                    
                    if name not in ['reg1','reg2','reg3']:
                                                
                        # Winding reactance
                        if hasattr(i, "reactances") and i.reactances is not None:
                            # Since we are in the case of 2 windings, we should only have one reactance
                            wdg_X = i.reactances
                        
                        if (
                            hasattr(i, "windings")
                            and i.windings is not None
                        ):
                            # Two winding transformer is assumed
                            wdg_num = 0
                            wdg_R = []
                                
                            for winding in i.windings:
                                
                                wdg_num += 1
                                
                                # Number of phases
                                if (
                                    hasattr(winding, "phase_windings")
                                    and winding.phase_windings is not None
                                ):
                                    nphases=len(winding.phase_windings)
                                    
                                # Nominal voltage
                                if (
                                    hasattr(winding, "nominal_voltage")
                                    and winding.nominal_voltage is not None
                                ):
                                    kv=winding.nominal_voltage * 10 ** -3  # OpenDSS in kV
                                                                        
                                # Rated power
                                if (
                                    hasattr(winding, "rated_power")
                                    and winding.rated_power is not None
                                ):
                                    kva = winding.rated_power * 10 ** -3                           
                                
                                nominal_voltages.append(kv)
                                basekV = kv
                                baseZ = basekV**2/baseMVA
                                baseY = 1/baseZ
                                baseA = baseMVA/(np.sqrt(3)*basekV)*1000.0
                                    
                                # Winding resistance
                                # resistance
                                if (
                                    hasattr(winding, "resistance")
                                    and winding.resistance is not None
                                ):
                                    wdg_R.append(winding.resistance)
                                    
        #                            br_r = i.windings[0].resistance + i.windings[1].resistance
        #                            br_x = i.reactances[0]
                                        
                                for phase_winding in winding.phase_windings:
                                   
                                    ph = phase_winding.phase
                                   
                                    if ph.lower() == 'a':
                                        if wdg_num == 1:
                                            I_rating1[0] = kva / np.sqrt(3) / kv / baseA
                                        elif wdg_num == 2:
                                            I_rating2[0] = kva / np.sqrt(3) / kv / baseA                                            
                                    elif ph.lower() == 'b':
                                        if wdg_num == 1:
                                            I_rating1[1] = kva / np.sqrt(3) / kv / baseA
                                        elif wdg_num == 2:
                                            I_rating2[1] = kva / np.sqrt(3) / kv / baseA
                                    elif ph.lower() == 'c':
                                        if wdg_num == 1:
                                            I_rating1[2] = kva / np.sqrt(3) / kv / baseA
                                        elif wdg_num == 2:
                                            I_rating2[2] = kva / np.sqrt(3) / kv / baseA
                                                      
                            np.fill_diagonal(br_r,np.sum(wdg_R))
                            np.fill_diagonal(br_x,wdg_X)
                            
                            br_r = br_r/100.0*baseMVA/(kva/1000.0)
                            br_x = br_x/100.0*baseMVA/(kva/1000.0)
                            
                            # Currently set at minimum current rating of the two windings
                            # Values should be same for both the windings
                            current_rating_a0 = min(I_rating1[0], I_rating2[0])
                            current_rating_b0 = min(I_rating1[1], I_rating2[1])
                            current_rating_c0 = min(I_rating1[2], I_rating2[2])
                            current_rating_a = [current_rating_a0,current_rating_b0,current_rating_c0]
                                                        
                                        
                    elif name in ['reg1']:
                        
                        # Winding reactance
                        if hasattr(i, "reactances") and i.reactances is not None:
                            # Since we are in the case of 2 windings, we should only have one reactance
                            wdg_X = i.reactances
                        
                        if (
                            hasattr(i, "windings")
                            and i.windings is not None
                        ):
                            # Two winding transformer is assumed
                            wdg_num = 0
                            wdg_R = []
                                
                            for winding in i.windings:
                                
                                wdg_num += 1
                                
                                # Number of phases
                                if (
                                    hasattr(winding, "phase_windings")
                                    and winding.phase_windings is not None
                                ):
                                    nphases=len(winding.phase_windings)
                                    
                                # Nominal voltage
                                if (
                                    hasattr(winding, "nominal_voltage")
                                    and winding.nominal_voltage is not None
                                ):
                                    kv=winding.nominal_voltage * 10 ** -3  # OpenDSS in kV
                                                                        
                                # Rated power
                                if (
                                    hasattr(winding, "rated_power")
                                    and winding.rated_power is not None
                                ):
                                    kva = 3 * winding.rated_power * 10 ** -3                           
                                
                                nominal_voltages.append(kv)
                                basekV = kv
                                baseZ = basekV**2/baseMVA
                                baseY = 1/baseZ
                                baseA = baseMVA/(np.sqrt(3)*basekV)*1000.0
                                    
                                # Winding resistance
                                # resistance
                                if (
                                    hasattr(winding, "resistance")
                                    and winding.resistance is not None
                                ):
                                    wdg_R.append(winding.resistance)
                                    
        #                            br_r = i.windings[0].resistance + i.windings[1].resistance
        #                            br_x = i.reactances[0]
                                        
                                for phase_winding in winding.phase_windings:
                                   
                                    ph = phase_winding.phase
                                   
                                    if ph.lower() == 'a':
                                        if wdg_num == 1:
                                            I_rating1[0] = kva / kv / baseA
                                        elif wdg_num == 2:
                                            I_rating2[0] = kva / kv / baseA
#                                    elif ph.lower() == 'b':
#                                        if wdg_num == 1:
#                                            I_rating1[1] = kva / kv / baseA
#                                        elif wdg_num == 2:
#                                            I_rating2[1] = kva / kv / baseA
#                                    elif ph.lower() == 'c':
#                                        if wdg_num == 1:
#                                            I_rating1[2] = kva / kv / baseA
#                                        elif wdg_num == 2:
#                                            I_rating2[2] = kva / kv / baseA                                        

                            np.fill_diagonal(br_r,np.sum(wdg_R))
                            np.fill_diagonal(br_x,wdg_X)
                            
                            br_r = br_r/100.0*baseMVA/(kva/1000.0)
                            br_x = br_x/100.0*baseMVA/(kva/1000.0)
                            
                            # Currently set at minimum current rating of the two windings
                            # Values should be same for both the windings
                            current_rating_a0 = min(I_rating1[0], I_rating2[0])
#                            current_rating_b = current_rating_a
#                            current_rating_c = current_rating_a
                            current_rating_a = [current_rating_a0,current_rating_a0,current_rating_a0]
                    
                    
                    #Converting the arrays to lists for writing to json in a correct way
                    br_r = br_r.tolist()
                    br_x = br_x.tolist()
                    g_fr = list(g_fr)
                    g_to = list(g_to)
                    b_fr = list(b_fr)
                    
                    if name not in ['reg2','reg3']:
                        data = dict(index=index,name=name,nominal_voltages=nominal_voltages,length=length,f_bus=f_bus,t_bus=t_bus,br_r=br_r,br_x=br_x,g_fr=g_fr,g_to=g_to,b_fr=b_fr,b_to=b_to,current_rating_a=current_rating_a,angmin=angmin,angmax=angmax,shift=shift,tap=tap,transformer=transformer,status=status,microgrid_id=1)
                        branch_data[str(index)] = data
                    elif name in ['reg2','reg3']:
                        index -= 1
                
            m_idx += 1
                
        return branch_data	

    def write_buses(self, model):
        
        ###############################################
        ##Defining the per unit values temporarily 
        ###############################################
        basekV = self.basekV
        baseMVA = self.baseMVA
        baseZ = basekV**2/baseMVA
        ###############################################
        
        
        bus_data = {}
        node_index = 0
        for i in model.models:

            if isinstance(i, Node):  # If the node is a Swing/System bus
            
                temp_bus_data = dict(            
                    name = i.name,             # Bus name
                    nominal_voltage = basekV,  # Nominal voltage at bus (phase-phase)
                    index = node_index+1,      # Unique Node index
                    bus_type = 1,              # The only valid values are 1, 2, 3, 4. 1 = PQ, 2 = PV, 3 = ref, 4 = isolated
                    vm = [1, 1, 1],                    # Node Voltage Magnitude in p.u.
                    va = [0, 0, 0],                    # Node Voltage Angle in radians
                    vmin = [0.9,0.9,0.9] ,               # Minimum voltage magnitude (per unit)
                    vmax = [1.1, 1.1, 1.1],               # Maximum voltage magnitude (per unit)
                    status = 1,                 # 1 if the bus is active, 0 if the bus is inactive
                    microgrid_id = 1
                    )                

                # The only valid values are 1, 2, 3, 4. 1 = PQ, 2 = PV, 3 = ref, 4 = isolated
                if i.name == 'sourcebus':
                    temp_bus_data["bus_type"] = 3  # Swing bus ==> Type = 3
                
                # Node Voltage Magnitude in p.u.
                if hasattr(i,"vm") and i.vm is not None:
                    vm = i.vm
                
                # Node Voltage Angle in radians
                if hasattr(i,"va") and i.va is not None:                                        
                    va = i.va
                
                # Minimum voltage magnitude (per unit)
                if hasattr(i,"vmin") and i.vmin is not None:                                        
                    vmin = i.vmin
                
                # Maximum voltage magnitude (per unit)
                if hasattr(i,"vmax") and i.vmax is not None:                    
                    vmax = i.vmax


                ## Not used by OD&O - For Book-keeping only
                if hasattr(i, "nominal_voltage") and i.nominal_voltage is not None:
                    temp_bus_data["nominal_voltage"] = i.nominal_voltage

                bus_data[str(node_index+1)] = temp_bus_data
                
                node_index = node_index + 1     
                
            
        return bus_data


    def write_loads(self, model):
        
        ###############################################
        ##Defining the per unit values temporarily 
        ###############################################
        basekV = self.basekV
        baseMVA = self.baseMVA
        baseZ = basekV**2/baseMVA
        ###############################################
        
        load_data = {}
        load_index = 0

        # Mapping the phase_indices to the corresponding strings  
        phase_map = {"a":0,"b":1,"c":2}

        for i in model.models:
            if isinstance(i, Load):
                
                ## Finding the Index of the bus to which the given load is connected
                bus_data = self.network['bus']

                for j in bus_data:
                    if bus_data[j]["name"] == i.connecting_element:
                        connecting_bus = bus_data[j]["index"]
                        break
                
                # Check if the given Bus entry exists in load_data
                bus_exists_flag = 0

                if load_data != {}: 
                    for entry in load_data:
                        if load_data[entry]["load_bus"] == connecting_bus:
                            bus_exists_flag = 1
                            break
                
                
                ## If the bus doesn't exist, initialize the load instance with default values
                if bus_exists_flag == 0:
                    temp_load_data = dict(name = i.name,                        # Name of the load
                                        pd = [0, 0, 0],                         # Real power demand in per unit (one value per phase) - at a snapshot definded in the original model
                                        qd = [0, 0, 0],                         # Reactive power demand in per unit (one value per phase) - at a snapshot definded in the original model
                                        index = load_index + 1,                 # Unique load index
                                        status = 1,                             # Load status; = 1 if connected
                                        load_bus = connecting_bus,               # Index of the Bus to which the given load is connected
                                        microgrid_id = 1,
                                        critical = 1    
                                        )
                else: # get the instance from load_data
                    temp_load_data = load_data[entry]
                
                # Update the per phase P, Q depending on the values for the given instance
                for k in range(len(i.phase_loads)):
                    # Identify which phase is the given single phase load connected to
                    given_phase = i.phase_loads[k].phase.lower()

                    # Determine the phase index using "given_phase" and "phase_map"
                    for phase_str, phase_index in phase_map.items():
                        if phase_str == given_phase: # Load is connected to this phase
                            break;

                    # Updating the p, q values for the corresponding phase of the given load
                    temp_load_data["pd"][phase_index] = round(i.phase_loads[k].p)/(baseMVA*10**6)
                    temp_load_data["qd"][phase_index] = round(i.phase_loads[k].q,-3)/(baseMVA*10**6)

                # Add/update the load_instance to the load_data
                if bus_exists_flag == 0:
                    load_data[str(load_index+1)] = temp_load_data
                    # Increment the load_index for the new entry
                    load_index += 1

                else:
                    load_data[entry] = temp_load_data


        return load_data

    def write_generators(self, model):
        
        ###############################################
        ##Defining the per unit values temporarily 
        ###############################################
        basekV = self.basekV
        baseMVA = self.baseMVA
        baseZ = basekV**2/baseMVA
        ###############################################
        
        gen_data = {}
        gen_index = 0

        # Mapping the phase_indices to the corresponding strings  
        phase_map = {"a":0,"b":1,"c":2}

        bus_data = self.network['bus']
        
        for i in model.models:
            if isinstance(i, Photovoltaic) or isinstance(i, PowerSource): # If the instance is a Generator or Source forming gen (Slack)
    
                ## Finding the Index of the bus to which the given generator (DER) is connected
                for j in bus_data:
                    if bus_data[j]["name"] == i.connecting_element:
                        connecting_bus = bus_data[j]["index"]
                        break
                
                # Check if the given Bus entry exists in load_data
                bus_exists_flag = 0

                if gen_data != {}: 
                    for entry in gen_data:
                        if gen_data[entry]["gen_bus"] == connecting_bus:
                            bus_exists_flag = 1
                            break

                ## If the bus doesn't exist, initialize the generator instance with default values
                empty_3ph_arr = [0, 0, 0]
                if bus_exists_flag == 0:
                    temp_gen_data = dict(
                        name = i.name,              # Name of the generator
                        nominal_voltage = basekV,   # Nominal voltage at bus (phase-phase)
                        gen_bus = connecting_bus,   # Bus number
                        index = gen_index + 1,      # Unique generator index
                        pg = empty_3ph_arr,         # Real power output in pu - used for dispatchable loads
                        qg = empty_3ph_arr,         # Reactive power output in pu - used for dispatchable loads
                        qmin = empty_3ph_arr,       # Minimum reactive power output in pu
                        qmax = empty_3ph_arr,       # Maximum reactive power output in pu
                        pmin = empty_3ph_arr,       # Minimum real power output in pu
                        pmax = empty_3ph_arr,       # Maximum real power output in pu
                        model = 2,                  # Generator cost model, 1 = piecewise linear, 2 = polynomial
                        ncost = 3,                  # i.e 3 co-efficients for the polynomial
                        cost = [0.0, 0.0, 0.0],     # "Parameters defining total cost function f(p) begin in this column,
                                                        # units of f(p) are $/hr and MW (or MVAr), respectively:
                                                        # (MODEL = 1) => p0, f0, p1, f1,..., pn, fn
                                                        # where p0 < p1 < ... < pn and the cost f(p) is defined by the coordinates (p0, f0), (p1, f1), . . . , (pn, fn) of the end/break-points of the piecewise linear cost. 
                                                        # (MODEL = 2) => cn, ... , c1, c0
                                                        # n + 1 coefficients of n-th order polynomial cost, starting with
                                                        # highest order, where cost is f(p) = c_n*p^n + ... + c1*p + c0"
                        status = 1,                 # 0 = Inactive, 1 = Active
                        microgrid_id = 1

                    )
                        
                else: # get the instance from gen_data
                    temp_gen_data = gen_data[entry]
                
                #############################################################
                # Set to defaults based on system data (as per the schematic)
                #############################################################

                index = gen_index + 1                       # Unique Generator Index
                gen_bus = i.connecting_element      # Bus number the given generator is connected to     

                # Name of the generator
                if hasattr(i, "name") and i.name is not None:
                    name = i.name                       
                else:
                    name = 'Gen_' + str(gen_index+1)                                  

                # Real power output in pu - used for dispatchable loads (Default = 0)
                if hasattr(i, "pg") and i.pg is not None:
                    pg = i  .active_rating/baseMVA            
                else:
                    pg = 0                                  
                    
                # Reactive power output in pu - used for dispatchable loads (Default = 0)
                if hasattr(i, "qg") and i.qg is not None:
                    qg = i.reactive_rating/baseMVA          
                else:
                    qg = 0                                  


                # Minimum real power output in pu (Default = 0)                
                if hasattr(i, "pmin") and i.pmin is not None:
                    pmin = i.pmin/baseMVA                  
                else: 
                    pmin = 0                                
                    
                # Maximum real power output in pu (Default = pg)                
                if hasattr(i, "pmax") and i.pmax is not None:
                    pmax = i.pmax/baseMVA                   
                else: 
                    pmax = pg                               
                    
                # Minimum reactive power output in pu                
                if hasattr(i, "qmin") and i.qmin is not None:
                    qmin = i.qmin/baseMVA                   
                else: 
                    qmin = -qg
                    
                # Maximum reactive power output in pu
                if hasattr(i, "qmax") and i.qmax is not None:
                    qmax = i.qmax/baseMVA                                   
                else: 
                    qmax = qg                        
                    

                ######################################################                                                    
                # Set to default constants predefined in the schematic
                ######################################################                                                    
                model = 2                                   # Generator cost model, 1 = piecewise linear, 2 = polynomial
                ncost = 3                                   # i.e 3 co-efficients for the polynomial
                cost = [0.0,0.0,0.0]                        # "Parameters defining total cost function f(p) begin in this column,
                                                                ## units of f(p) are $/hr and MW (or MVAr), respectively:
                                                                ## (MODEL = 1) => p0, f0, p1, f1,..., pn, fn
                                                                ## where p0 < p1 < ... < pn and the cost f(p) is defined by the coordinates (p0, f0), (p1, f1), . . . , (pn, fn) of the end/break-points of the piecewise linear cost. 
                                                                ## (MODEL = 2) => cn, ... , c1, c0
                                                                ## n + 1 coefficients of n-th order polynomial cost, starting with
                                                                ## highest order, where cost is f(p) = c_n*p^n + ... + c1*p + c0"

                status = 1                                  # 0 = Inactive, 1 = Active (set to default)

                # Not used by OD&O Tool
                nominal_voltage = i.nominal_voltage # Nominal voltage at bus (phase-phase)

                # Aggregating the Parameters for the respective generator in one entry              
                gen_data[str(index)] = temp_gen_data
                
                gen_index += 1 


        return gen_data


    def write_shunt(self, model):
        shunt_data = {}
        index = 0
        m_info = model.models
        m_idx = 0
        shunt_count = 0
        baseMVA = self.baseMVA
        bus_data = self.network['bus']
                
        for i in model.models:
            
            if isinstance(i, Capacitor):
        
                index += 1
                
                name = i.name
                status = 1
#                kvar = i.
                             
                shunt_bus0 = i.connecting_element
                
                ## Finding the Indexes of the buses to which the branch is connected
                for j in bus_data:
                    if bus_data[j]["name"] == shunt_bus0:
                        shunt_bus = bus_data[j]["index"]
                        break				  
                
                # gs is assumed as 0.0 pu (no resistive loss)
                gs = [0.0, 0.0, 0.0]
                bs = [0.0, 0.0, 0.0]
                
#                # For a 3-phase capbank
                if (
                    hasattr(i, "phase_capacitors")
                    and i.phase_capacitors is not None
                    and len(i.phase_capacitors) == 3
                ):
                    nominal_voltage = i.nominal_voltage
                    basekV = nominal_voltage/1000.0                
                    baseZ = basekV**2/baseMVA
                    baseY = 1/baseZ
                    baseA = baseMVA/(np.sqrt(3)*basekV)*1000.0
                    
                    for phase_capacitor in i.phase_capacitors:
                    
                        ph = phase_capacitor.phase
                    
                        if ph.lower() == 'a':
                            Mvar_rating = phase_capacitor.var/1000000.0
                            bs0 = Mvar_rating/((basekV/np.sqrt(3))**2)
                            bs[0] = bs0/baseY
                            
                        elif ph.lower() == 'b':
                            Mvar_rating = phase_capacitor.var/1000000.0
                            bs0 = Mvar_rating/((basekV/np.sqrt(3))**2)
                            bs[1] = bs0/baseY
                            
                        elif ph.lower() == 'c':
                            Mvar_rating = phase_capacitor.var/1000000.0
                            bs0 = Mvar_rating/((basekV/np.sqrt(3))**2)
                            bs[2] = bs0/baseY        
                                                        
                # For a 1-phase capbank                                
                elif (
                    hasattr(i, "phase_capacitors")
                    and i.phase_capacitors is not None
                    and len(i.phase_capacitors) != 3
                ):
                    
                    nominal_voltage = i.nominal_voltage
                    basekV = nominal_voltage*np.sqrt(3)/1000.0                
                    baseZ = basekV**2/baseMVA
                    baseY = 1/baseZ
                    baseA = baseMVA/(np.sqrt(3)*basekV)*1000.0
                    
                    for phase_capacitor in i.phase_capacitors:
                        if (
                            hasattr(phase_capacitor, "phase")
                            and phase_capacitor.phase is not None
                        ):
                            ph = phase_capacitor.phase
                            
                            if ph.lower() == 'a':
                                Mvar_rating = phase_capacitor.var/1000000.0
                                bs0 = Mvar_rating/((basekV/np.sqrt(3))**2)
                                bs[0] = bs0/baseY
                                
                            elif ph.lower() == 'b':
                                Mvar_rating = phase_capacitor.var/1000000.0
                                bs0 = Mvar_rating/((basekV/np.sqrt(3))**2)
                                bs[1] = bs0/baseY
                                
                            elif ph.lower() == 'c':
                                Mvar_rating = phase_capacitor.var/1000000.0
                                bs0 = Mvar_rating/((basekV/np.sqrt(3))**2)
                                bs[2] = bs0/baseY                        
                                                               
                data = dict(index=index,shunt_bus=shunt_bus,name=name,gs=gs,bs=bs,status=status,microgrid_id=1)
                shunt_data[str(index)] = data
                
            m_idx += 1    
                
        return shunt_data
    
    def write_storage(self, model):
        
        storage_data = {}
        index = 0
        m_info = model.models
        m_idx = 0
        baseMVA = self.baseMVA
        bus_data = self.network['bus']
        
        for i in model.models:
            
            if isinstance(i, Storage):
        
                index += 1
                name = i.name																	  
                storage_bus0 = i.connecting_element
                shunt_bus0 = i.connecting_element
                
                ## Finding the Indexes of the buses to which the branch is connected
                for j in bus_data:
                    if bus_data[j]["name"] == shunt_bus0:
                        shunt_bus = bus_data[j]["index"]
                        break				  
                # Default values
                status = 1
                qmin = -50.0
                qmax = 70.0
                discharge_rating = 50.0
                charge_rating = 70.0
                charge_efficiency = 1.0
                discharge_efficiency = 1.0
                r = [0.1, 0.1, 0.1]
                x = [0.0, 0.0, 0.0]
                standby_loss = 0.0
                nominal_voltage = i.nominal_voltage            
                basekV = nominal_voltage/1000.0                
                baseZ = basekV**2/baseMVA
                baseY = 1/baseZ
                baseA = baseMVA/(np.sqrt(3)*basekV)*1000.0
                
                if (
                    hasattr(i, "resistance")
                ):
                    R = i.resistance / baseZ
                    r = [R, R, R]
                if (
                    hasattr(i, "reactance")
                ):
                    X = i.reactance / baseZ
                    x = [X, X, X]
                
                if (
                    hasattr(i, "rated_kWh")
                ):
                    energy_rating = i.rated_kWh
                 
                if (
                    hasattr(i, "stored_kWh")
                ):
                    energy = i.stored_kWh
					 
                if (
                    hasattr(i, "discharge_rate")
                ):
                    discharge_rating = i.discharge_rate    
                    
                if (
                    hasattr(i, "charge_rate")
                ):
                    charge_rating = i.charge_rate
                
                if (
                    hasattr(i, "charging_efficiency")
                ):
                    charge_efficiency = i.charging_efficiency
                    
                if (
                    hasattr(i, "discharging_efficiency")
                ):
                    discharge_efficiency = i.discharging_efficiency
                
                if (
                    hasattr(i, "standby_loss")
                ):
                    standby_loss = i.standby_loss
                                                             
                data = dict(index=index,storage_bus=storage_bus,name=name,qmin=qmin,qmax=qmax,discharge_rating=discharge_rating,charge_rating=charge_rating,charge_efficiency=charge_efficiency,discharge_efficiency=discharge_efficiency,r=r,x=x,standby_loss=standby_loss,status=status)
                storage_data[str(index)] = data

            m_idx += 1    
                

        return storage_data