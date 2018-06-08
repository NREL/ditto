__author__ = "Aadil Latif"
__version__ = "1.0.0"
__maintainer__ = "Aadil Latif"
__email__ = "aadil.latif@nrel.gov"


customer_types = {
    0   :	'Residential',
    1	:	'Small_Commercial',
    2	:	'Large_Commercial',
    3   :	'Large_Power',
    4   :	'Motor_Load',
    5	:	'Irrigation',
    6	:	'Oil_and_Gas',
    7	:	'Traffic_Lights',
    8	:	'Security_and_Street_Lights',
    9	:	'Flat_Rate_Load',
    10  :	'Primary',
}

load_mix = {
    0   :	'Constant kVA  PU, Default=1',
    1   :	'Constant IMP  In PU, Default=0',
    2   :	'Constant Current  In PU, Default=0',
    3   :	'Connection Code  W=Wye, D=Delta, Default=W',
    4   :	'Named Equipment Category',
}



conductor_material = {
    1	:	'Anaconda',
    2	:	'ACSR',
    3	:	'Alum',
    4	:	'AAC',
    5	:	'Copper',
    6	:	'CW',
    7	:	'CWC',
    8	:	'HdAlum',
    9	:	'HD Copper',
    10	:	'HHHC',
    11	:	'Steel',
    12	:	'User-Defined',
}

xfmr_mounting = {
    0  :	'Unknown',
    1  :	'Bus Mounted',
    2  :	'Pole Mounted',
    3  :	'Pad Mounted',
    4  :	'Vault Mounted',
    5  :	'Substation',
    6  :	'Other',
}


device_group = {
    0	:	'None',
    1	:	'Source',
    2	:	'Bay',
    3	:	'OCR',
    4	:	'Recloser',
    5	:	'Fuse',
    6	:	'Sectionalizer',
    7	:	'Circuit_Breaker',
}

height_units = {
    0	:	'Total',
    1	:	'mi',
    2	:	'km',
    3	:	'mft',
    4	:	'ft',
    5	:	'm',
    6	:	'in',
    7	:	'cm',
}

impedance_units = {
    0	:	'Ohms',
    1	:	'Percent',
    2	:	'Per Unit',
    3	:	'Total',
}

xfmr_types = {
    0	:	'Single Phase Balanced',
    1	:	'Single Phase Unbalanced',
    2	:	'3 Phase',
    3	:	'3 Winding',
}

ugCable_type = {
    0	:	'Concentric',
    1	:	'Tape Shield',
    2	:	'No Concentric',
}

unit_field_values = {
    0	:	'Total',
    1	:	'Mile',
    2	:	'Kilometer',
    3	:	'Mft',
    4	:	'Feet',
    5	:	'Meter',
}

capacitor_conn = {
    0	:	'Y',
    1	:	'D',
    2	:	'Shunt Same as Parent',
    3	:	'Series',
}

capacitor_state = {
    0	:	'Disconnected',
    1	:	'On',
    2	:	'Off',
}

capacitor_control_type = {
    0	:	'none',
    1	:	'voltage',
    2	:	'currentFlow',
    3	:	'reactivePower',
    4	:	'timeScheduled',
    5	:	'temperature',
}

circuit_level = {
    0	:	'None',
    1	:	'Feeder',
    2	:	'Substation Low Side Bus',
    3	:	'Substation High Side Bus',
    4	:	'Spot Load',
    5	:	'Consumer',
    6	:	'Active Consumer',
    7	:	'Inactive Consumer',
}

generator_conn = {
    'W'	:	'Y',
    'D'	:	'D',
}

soft_start_types = {
    0	:	'None',
    1	:	'Impedance',
    2	:	'Auto Transformer',
    3	:	'Capacitive',
    4	:	'Partial Winding',
    5	:	'Wye Delta',
}

motor_status = {
    0	:	'Disconnected',
    1	:	'Off',
    2	:	'Locked Rotor',
    3	:	'Soft Start',
    4	:	'Running',
}

xfmr_conn = {
    1	:	['Y', 'Y'],#'(Y,Y Ground)',  # Any valid configuration. (Default)
    2	:	['D', 'Y'],#'(D-Y Ground)', # See the Transformer Phasing Note 1 section.
    3	:	['Y', 'D'],#'(Y-D Ground)', # See the Transformer Phasing Note 1 section.
    4	:	'(Ungrounded Y-D)',# See the Transformer Phasing Note 1 section.
    5	:	'(Y-D Open)', #Transformer must be ABC. Upline element can be ABC, AB, or AC.
    6	:	'(D-D)', #See the Transformer Phasing Note 1 section.
    7	:	'(Y-Y with Grounded Impedance)', #Any valid configuration.
    8	:	'(Y-Y with Three-Phase Transformer Core)', #Any valid configuration.
    9	:	'(D-D One)', #See the Transformer Phasing Note 2 section.
    10	:	'(D-D Open)', #See the Transformer Phasing Note 1 section.
    11	:	'(Y-Y-D Ground)', #See the Transformer Phasing Note 1 section.
    12	:	'(Y-D One)', #See the Transformer Phasing Note 3 section.
    13	:	'(D-Y Open)', #See the Transformer Phasing Note 1 section.
    14	:	'(D-Y One)', #See the Transformer Phasing Note 4 section.
    15	:	'(Ungrounded D-Y)',
    16	:	'(Y-Y-Y Ground)',
    17	:	'(D-Y-D)',
    18	:	'(D-D-D)',
}

generator_model = {
    0  :	'Negative Load',
    1  :	'Swing Unlimited',
    2  :	'Swing kVA',
    3  :	'Swing kvar',
}

fault_coord_type = {
    0	:	'Not Required',
    1	:	'Fuse save for all flt',
    2	:	'Fuse save for 3-ph flt',
    3	:	'Fuse save for 2-ph flt',
    4	:	'Fuse save for 1-ph flt',
    5	:	'Fuse blow for all flt',
    6	:	'Fuse blow for 3-ph flt',
    7	:	'Fuse blow for 2-ph flt',
    8	:	'Fuse blow for 1-ph flt',
    9	:	'Coordinate for all flt',
    10	:	'Coordinate for 3-phase flt',
    11	:	'Coordinate for 2-phase flt',
    12	:	'Coordinate for 1-phase flt',
    13	:	'Sequentially coordinate for transformer multiplier 1.0',
    14	:	'Sequentially coordinate for 3-phase fault',
    15	:	'Sequentially coordinate for 2-phase fault',
    16	:	'Sequentially coordinate for 1-phase fault',
    17	:	'Recl has no curves',
    18	:	'Recl has no fast curves',
    19	:	'Recl has no slow curves',
    20	:	'Fuse is too small',
    21	:	'Fuse is too large',
    22	:	'2 and 3 Phs Flt',
    23	:	'1-phase fault with upline delta transformer',
    24	:	'2- or 3-phase fault with upline ground return',
    25	:	'Recloser has no phase curves',
    26	:	'Fuse is too small for multi phase',
    27	:	'Fuse is too small for single phase',
    28	:	'Coordinate for all faults (initially slower)',
    29	:	'Coordinate for 3-phase faults (initially slower)',
    30	:	'Coordinate for 2-phase faults (initially slower)',
    31	:	'Coordinate for 1-phase faults (initially slower)',
    32	:	'Coordinate for 2&3-phase faults (initially slower)',
    33	:	'Invalid device coordination type',
}



