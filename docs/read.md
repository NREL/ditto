# To see whether an attribute is tested or not

## Line
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| nominal_voltage     | yes     |
| line_type           | no      |
| length              | yes     |
| from_element        | yes     |
| to_element          | yes     |
| is_fuse             | no      |
| is_switch           | no      |
| is_banked           | no      |
| faultrate           | no      |
| wires               | yes     |
| positions           | no      |
| impedance_matrix    | yes     |
| capacitance_matrix  | yes     |
| substation_name     | no      |
| feeder_name         | yes     |
| is_recloser         | no      |
| is_breaker          | no      |
| is_sectionalizer    | no      |
| nameclass           | yes     |
| is_substation       | no      |
| is_network_protector| no      |


## Wire
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| phase               | yes     |
| nameclass           | yes     |
| X                   | yes     |
| Y                   | yes     |
| diameter            | yes     |
| gmr                 | yes     |
| ampacity            | yes     |
| emergency_ampacity  | yes     |
| resistance          | yes     |
| insulation_thickness| no      |
| is_fuse             | no      |
| is_switch           | no      |
| is_open             | no      |
| interrupting_rating | no      |
| concentric_neutral_gmr | no      |
| concentric_neutral_resistance | no      |
| concentric_neutral_diameter   | no      |
| concentric_outside_diameter   | no      |
| concentric_neutral_nstrand    | no      |
| drop                | no      |
| is_recloser         | no      |
| is_breaker          | no      |
| is_network_protector| no      |
| is_sectionalizer    | no      |

## Capacitor
| Attribute           | Tested  |
| :------------------:|:-------:|
| nominal_voltage     | yes     |
| connection_type     | yes     |
| delay               | no      |
| mode                | no      |
| low                 | no      |
| high                | no      |
| resistance          | no      |
| resistance0         | no      |
| reactance           | no      |
| reactance0          | no      |
| susceptance         | no      |
| susceptance0        | no      |
| conductance         | no      |
| conductance0        | no      |
| pt_ratio            | no      |
| ct_ratio            | no      |
| pt_phase            | no      |
| connecting_element  | no      |
| positions           | no      |
| measuring_element   | no      |
| substation_name     | no      |
| feeder_name         | no      |
| is_substation       | no      |

## Phase Capacitor
| Attribute           | Tested  |
| :------------------:|:-------:|
| phase               | yes     |
| var                 | no      |
| switch              | no      |
| sections            | no      |
| normalsections      | no      |

## Transformer
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | no      |
| install_type        | no      |
| noload_loss         | no      |
| phase_shift         | no      |
| from_element        | yes     |
| to_element          | yes     |
| reactances          | yes     |
| windings            | yes     |
| positions           | no      |
| loadloss            | no      |
| normhkva            | no      |
| is_center_tap       | no      |
| is_substation       | no      |
| substation_name     | no      |
| feeder_name         | yes     |

## Winding
| Attribute           | Tested  |
| :------------------:|:-------:|
| connection_type     | yes     |
| voltage_type        | no      |
| nominal_voltage     | yes     |
| voltage_limit       | no      |
| resistance          | yes     |
| reverse_resistance  | no      |
| phase_windings      | yes     |
| rated_power         | yes     |
| emergency_power     | no      |


## Phase Winding
| Attribute           | Tested  |
| :------------------:|:-------:|
| tap_position        | no      |
| phase               | yes     |
| compensator_r       | no      |
| compensator_x       | no      |

## Regulator
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | no      |
| delay               | yes     |
| highstep            | no      |
| lowstep             | no      |
| pt_ratio            | yes     |
| ct_ratio            | no      |
| phase_shift         | no      |
| ltc                 | no      |
| bandwidth           | yes     |
| bandcenter          | yes     |
| voltage_limit       | no      |
| from_element        | yes     |
| to_element          | yes     |
|connected_transformer| yes     |
| pt_phase            | no      |
| reactances          | yes     |
| windings            | no      |
| positions           | no      |
| winding             | yes     |
| ct_prim             | no      |
| noload_loss         | no      |
| substation_name     | no      |
| feeder_name         | yes     |
| setpoint            | no      |
| is_substation       | no      |

## Load
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | no      |
| connection_type     | no      |
| nominal_voltage     | yes     |
| vmin                | yes     |
| vmax                | yes     |
| phase_loads         | yes     |
| positions           | no      |
| timeseries          | no      |
| connecting_element  | yes     |
| rooftop_area        | no      |
| peak_p              | no      |
| peak_q              | no      |
| peak_coincident_p  | no      |
| peak_coincident_q  | no      |
| yearly_energy       | no      |
| num_levels          | no      |
| num_users           | no      |
| substation_name     | no      |
| feeder_name         | yes     |
| upstream_transformer_name  | no      |
| transformer_connected_kva  | no      |
| is_substation       | no      |
| is_center_tap       | no      |
| center_tap_perct_1_N| no      |
| center_tap_perct_N_2| no      |
| center_tap_perct_1_2| no      |

## PhaseLoad
| Attribute           | Tested  |
| :------------------:|:-------:|
| phase               | no      |
| p                   | no      |
| q                   | no      |
| model               | no      |
| use_zip             | no      |
| drop                | no      |
| ppercentcurrent     | no      |
| qpercentcurrent     | no      |
| ppercentpower       | no      |
| qpercentpower       | no      |
| ppercentimpedance   | no      |
| qpercentimpedance   | no      |
