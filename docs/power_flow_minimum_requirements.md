# Power Flow Minimum Requirements

This document provides a list of the smallest possible set of DiTTo attributes required during a conversion if a snapshot power flow needs to be run on the output.

## Node

| Attribute | Comments |
| --------- | -------- |
| `name`    |          |
| `phases`  |          |

## Line

| Attribute          | Comments                                                     |
| ------------------ | ------------------------------------------------------------ |
| `name`             |                                                              |
| `length`           | Needed since some parameters are specified in per-unit length. |
| `line_type`        | Equations are different for overhead and underground lines.  |
| `from_element`     | Connectivity is required.                                    |
| `to_element`       | Connectivity is required.                                    |
| `wires`            | Wires are needed even if only the phase will be defined for each wire (see `Wire` section). |
| `impedance_matrix` |                                                              |

**Note**: If switching equipments, fuses and so on need to be also modeled, then use the flag attributes (ex: `is_switch`).

## Wire

| Attribute  | Comments                                                     |
| ---------- | ------------------------------------------------------------ |
| `phase`    |                                                              |
| `ampacity` | Not sure about this one, might not be absolutely required for power flow |

**Note**: This is assuming the impedance matrix of the line has been provided. Otherwise, wire parameters like `resistance`, `gmr`, and so on need to be defined here.

## PowerTransformer

| Attribute      | Comments                                                     |
| -------------- | ------------------------------------------------------------ |
| `name`         |                                                              |
| `from_element` | Connectivity is required.                                    |
| `to_element`   | Connectivity is required.                                    |
| `reactances`   |                                                              |
| `windings`     | Need to provide some `Winding` information (see `Winding` section). |
| `loadloss`     | Less sure about this one.                                    |

## Winding

| Attribute         | Comments                                                     |
| ----------------- | ------------------------------------------------------------ |
| `connection_type` |                                                              |
| `nominal_voltage` |                                                              |
| `phase_windings`  | Need to provide some `PhaseWinding` information (see `PhaseWinding` section). |
| `rated_power`     | This is supposed to move to `PowerTransformer` one day as this is confusing... |

## PhaseWinding

| Attribute | Comments |
| --------- | -------- |
| `phase`   |          |

## Regulator

| Attribute      | Comments                                                     |
| -------------- | ------------------------------------------------------------ |
| `name`         |                                                              |
| `bandcenter`   |                                                              |
| `bandwidth`    |                                                              |
| `from_element` | Connectivity is required.                                    |
| `to_element`   | Connectivity is required.                                    |
| `windings`     | Need to provide some `Winding` information (see `Winding` section). |
| `setpoint`     | This is a recent addition from Tarek, not sure how this is used. |

## Capacitor

| Attribute            | Comments                                                     |
| -------------------- | ------------------------------------------------------------ |
| `name`               |                                                              |
| `nominal_voltage`    |                                                              |
| `connection_type`    |                                                              |
| `mode`               |                                                              |
| `low`                |                                                              |
| `high`               |                                                              |
| `connecting_element` | Connectivity is required.                                    |
| `phase_capacitors`   | Need to provide some `PhaseCapacitor` information (see `PhaseCapacitor` section). |
| `measuring_element`  |                                                              |

## PhaseCapacitor

| Attribute | Comments |
| --------- | -------- |
| `phase`   |          |
| `var`     |          |

## Load

| Attribute            | Comments                                                     |
| -------------------- | ------------------------------------------------------------ |
| `name`               |                                                              |
| `nominal_voltage`    |                                                              |
| `connection_type`    |                                                              |
| `phase_loads`        | Need to provide some `PhaseLoad` information (see `PhaseLoad` section). |
| `connecting_element` | Connectivity is required.                                    |

## PhaseLoad

| Attribute | Comments |
| --------- | -------- |
| `phase`   |          |
| `p`       |          |
| `q`       |          |
| `model`   |          |

## PowerSource

| Attribute            | Comments                  |
| -------------------- | ------------------------- |
| `name`               |                           |
| `nominal_voltage`    |                           |
| `phases`             |                           |
| `is_sourcebus`       |                           |
| `rated_power`        |                           |
| `connecting_element` | Connectivity is required. |

Note: You need to define a power source at the feeder head.