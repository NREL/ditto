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
| impedance_matrix    | no      |
| capacitance_matrix  | no      |
| substation_name     | no      |
| feeder_name         | no      |
| is_recloser         | no      |
| is_breaker          | no      |
| is_sectionalizer    | no      |
| nameclass           | no      |
| is_substation       | no      |
| is_network_protector| no      |


## Wire
| Attribute           | Tested  |
| :------------------:|:-------:|
| name                | yes     |
| phase               | yes     |
| nameclass           | no      |
| X                   | no      |
| Y                   | no      |
| diameter            | no      |
| gmr                 | no      |
| ampacity            | no      |
| emergency_ampacity  | no      |
| resistance          | no      |
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
| nominal_voltage                | yes     |
| connection_type               | yes     |
| delay           | no      |
| mode                   | no      |
| low                   | no      |
| high            | no      |
| resistance                 | no      |
| resistance0            | no      |
| reactance  | no      |
| reactance0          | no      |
| susceptance | no      |
| susceptance0             | no      |
| conductance           | no      |
| conductance0             | no      |
| pt_ratio | no      |
| ct_ratio | no      |
| pt_phase | no      |
| connecting_element | no      |
| positions | no      |
| measuring_element | no      |
| substation_name | no      |
| feeder_name | no      |
| is_substation | no      |

## Phase Capacitor
| Attribute           | Tested  |
| :------------------:|:-------:|
| phase               | yes     |
| var                 | no      |
| switch              | no      |
| sections            | no      |
| normalsections      | no      |
