# To see whether an attribute is tested or not

## Line
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| nominal_voltage     | yes     |
| line_type           | yes     |
| length              | yes     |
| from_element        | yes     |
| to_element          | yes     |
| is_fuse             | yes     |
| is_switch           | yes     |
| is_banked           | no      | # Not now
| faultrate           | yes     |
| wires               | yes     |
| positions           | no      | # Not now
| impedance_matrix    | yes     |
| capacitance_matrix  | yes     | # Tarek needs to send this
| substation_name     | no      | # Not implemented
| feeder_name         | yes     | # Document it
| is_recloser         | no      | # Document that its in the name
| is_breaker          | no      | # Document that its in the name
| is_sectionalizer    | no      | # Not now
| nameclass           | yes     |
| is_substation       | no      | # Not now
| is_network_protector| no      | # Not now


## Wire
| Attribute           | Tested  |
| :------------------:|:-------:|
| phase               | yes     |
| nameclass           | yes     |
| X                   | yes     |
| Y                   | yes     |
| diameter            | yes     |
| gmr                 | yes     |
| ampacity            | yes     |
| emergency_ampacity  | yes     |
| resistance          | yes     |
| insulation_thickness| no      | # Needs to be implemented
| is_fuse             | no      | # needs to be deprecated
| is_switch           | no      | # needs to be deprecated
| is_open             | yes     |
| interrupting_rating | no      | # Not for now
| concentric_neutral_gmr | no      |  # Needs to be implemented
| concentric_neutral_resistance | no      | # Needs to be implemented
| concentric_neutral_diameter   | no      | # Needs to be implemented
| concentric_outside_diameter   | no      | # Needs to be implemented
| concentric_neutral_nstrand    | no      | # Needs to be implemented
| drop                | no      | # doesn't need testing, possible deprecation
| is_recloser         | no      | # needs to be deprecated
| is_breaker          | no      | # needs to be deprecated
| is_network_protector| no      | # doesn't need testing, needs to be deprecated
| is_sectionalizer    | no      | # needs to be deprecated

## Capacitor
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| nominal_voltage     | yes     |
| connection_type     | yes     |
| delay               | yes     |
| mode                | yes     |
| low                 | no      | # Create issue
| high                | no      | # Create issue
| resistance          | no      | # Create issue
| resistance0         | no      | # Not implemented
| reactance           | no      | # Create issue
| reactance0          | no      | # Not implemented
| susceptance         | no      | # Include in the same issues as conductance
| susceptance0        | no      | # Not implemented
| conductance         | no      | # cmatrix is used to represent, create issue if opendss gives defaults or we set the values
| conductance0        | no      | # Not implemented
| pt_ratio            | yes     |
| ct_ratio            | no      | # Create issue
| pt_phase            | yes     |
| connecting_element  | yes     | # Bhavya to Check if it is bus ; Confirmed
| positions           | no      | # implement from BusCoords.dss ; implement later
| measuring_element   | yes     | # Double check if it is in controller ; Confirmed
| substation_name     | no      | # Not implemented
| feeder_name         | yes     |
| is_substation       | no      | # Not implemented

## Phase Capacitor
| Attribute           | Tested  |
| :------------------:|:-------:|
| phase               | yes     |
| var                 | no      | # kvar, sum of each var = kvar ; bhavya to check ; Confirmed
| switch              | no      | # Create issue to see if it is included in opendss
| sections            | no      | # Create issue to see if it is included in opendss
| normalsections      | no      | # Create issue to see if it is included in opendss

## Transformer
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| install_type        | no      | #not needed
| noload_loss         | yes     |
| phase_shift         | no      | # Tarek to check if this exists in opendss and set it
| from_element        | yes     |
| to_element          | yes     |
| reactances          | yes     |
| windings            | yes     |
| positions           | no      | # Not needed
| loadloss            | yes     |
| normhkva            | yes     |
| is_center_tap       | yes     |
| is_substation       | no      | # Not needed
| substation_name     | no      | # Not needed
| feeder_name         | yes     | # mention that the feeder name is set from the circuit rather than the feeder

## Winding
| Attribute           | Tested  |
| :------------------:|:-------:|
| connection_type     | yes     |
| voltage_type        | no      | # Needs to be implemented , raise issue
| nominal_voltage     | yes     |
| voltage_limit       | no      | # Tarek to create a test case with a voltage regulator included, raise issue
| resistance          | yes     |
| reverse_resistance  | no      | # Needs to be implemented , raise issue
| phase_windings      | yes     |
| rated_power         | yes     |
| emergency_power     | yes     |


## Phase Winding
| Attribute           | Tested  |
| :------------------:|:-------:|
| tap_position        | no      | # Tarek looks into this
| phase               | yes     |
| compensator_r       | yes     |
| compensator_x       | yes     |

## Regulator
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes      |
| delay               | yes     |
| highstep            | yes     |
| lowstep             | no      |  # needs to be implemented ( equal to highstep), raise an issue
| pt_ratio            | yes     |
| ct_ratio            | no      | # Tarek to look at this
| phase_shift         | no      | # Tarek to check if this exists in opendss and set it
| ltc                 | no      | # not implemented
| bandwidth           | yes     |
| bandcenter          | yes     |
| voltage_limit       | no      | # Tarek to create a test case with a voltage regulator included, raise issue
| from_element        | yes     |
| to_element          | yes     |
|connected_transformer| yes     |
| pt_phase            | yes     |
| reactances          | yes     |
| windings            | no      | # Deprecate but a big api change
| positions           | no      | # Not now
| winding             | yes     | # Change name to pt_winding, check all the readers and writers
| ct_prim             | no      | # Tarek to set for an example
| noload_loss         | no      |# Deprecate along with windings but a big api change
| substation_name     | no      |# Not needed
| feeder_name         | yes     |
| setpoint            | no      | #Needs to be implemented, Raise an issue, read it from vreg
| is_substation       | no      |# Not needed

## Load
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| connection_type     | no      | # Tarek to create an example
| nominal_voltage     | yes     |
| vmin                | yes     |
| vmax                | yes     |
| phase_loads         | yes     |
| positions           | no      | # Not now
| timeseries          | no      | # Test later
| connecting_element  | yes     |
| rooftop_area        | no      | # Not implemented
| peak_p              | no      | # Deprecate
| peak_q              | no      | # Deprecate
| peak_coincident_p   | no      | # Might Replace with peak coincident factor
| peak_coincident_q   | no      | # Might Replace with peak coincident factor
| yearly_energy       | no      | # Not implemented
| num_levels          | no      |# Not implemented
| num_users           | no      |# Not implemented
| substation_name     | no      |# not needed
| feeder_name         | yes     |
| upstream_transformer_name  | no      | # Not implemented
| transformer_connected_kva  | no      | # Not implemented
| is_substation       | no      |# Not implemented
| is_center_tap       | no      |# Not implemented
| center_tap_perct_N_2| no      |# Not implemented
| center_tap_perct_1_N| no      |# Not implemented
| center_tap_perct_1_2| no      |# Not implemented

## PhaseLoad
| Attribute           | Tested  |
| :------------------:|:-------:|
| phase               | yes     |
| p                   | yes     |
| q                   | yes     |
| model               | yes     |
| use_zip             | yes     |
| drop                | no      | # Not tested
| ppercentcurrent     | yes     |
| qpercentcurrent     | yes     |
| ppercentpower       | yes     |
| qpercentpower       | yes     |
| ppercentimpedance   | yes     |
| qpercentimpedance   | yes     |

## PowerSource
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| nominal_voltage     | yes     |
| per_unit            | yes     |
| phases              | no      |  # CHeck
| positions           | no      | # Create buscoords.dss and test;
| is_sourcebus        | yes     |
| rated_power         | no      |  # Create issue
| emergency_power     | no      | # Create issue
| connection_type     | no      | #  Needs to be deprecated
| cutout_percent      | no      | # Needs to be deprecated
| cutin_percent       | no      | # Needs to be deprecated
| resistance          | no      | # Needs to be deprecated
| reactance           | no      |# Needs to be deprecated
| v_max_pu            | no      |# Needs to be deprecated
| v_min_pu            | no      |# Needs to be deprecated
| power_factor        | no      |# Needs to be deprecated
| connecting_element  | yes     |
| phase_angle         | no      | # Needs to be deprecated
| positive_sequence_impedance  | yes     |
| zero_sequence_impedance      | yes     |

## Nodes
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| nominal_voltage     | no      | # Double check , create issue
| phases              | yes     |
| positions           | yes     | # Create buscoords.dss and test; loads and capacitors - later
| substation_name     | no      | #not implemented
| feeder_name         | yes     |
| is_substation       | no      | # not implemented
| is_substation_connection  | no      | # not implemented
