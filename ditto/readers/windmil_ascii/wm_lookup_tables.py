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

std_file_headings = {
    'Line' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number', 'X Coordinate',
              'Y Coordinate','User Tag','Conductor Phase A','Conductor Phase B','Conductor Phase C','Conductor neutral',
              'Impedance Length','Construction Description','Load Mix Description','Load Zone Description',
              'Load Location', 'Load Growth','Billing Reference','Allocated kW, Ph A','Allocated kW, Ph B',
              'Allocated kW, Ph C', 'Allocated kvar, Ph A', 'Allocated kvar, Ph B', 'Allocated kvar, Ph C',
              'Allocated Consumers, Phase A', 'Allocated Consumers, Phase B', 'Allocated Consumers, Phase C',
              'Load Interruptible Type' ,'Failure Rate','Repair Time','Upline X Coordinate','Upline Y Coordinate',
              'Number of Neutrals','Conductor Graphical Length','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
              'GUID','pGUID','Unused','mGUID','Phase A Energized','Phase B Energized','Phase C Energized','X2','Y2',
              'Rotation Angle','Circuit Level','Substation GUID','Substation Name','Feeder GUID','Feeder Name'],

    'Capacitor' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                   'X Coordinate','Y Coordinate','User Tag','kvar, Phase A','kvar, Phase B','kvar, Phase C',
                   'Voltage Rating','Switch Type Code','Switch Status Code','Switch On Setting','Switch Off Setting',
                   'Control Element','Connection','Unit Size kvar','Control Phase','Failure Rate','Repair Time',
                   'Bypass Time','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                   '-','-','-','-','-','GUID','pGUID','Unused','mGUID','Phase A Energized','Phase B Energized',
                   'Phase C Energized','X2','Y2','Rotation Angle','Circuit Level','Substation GUID','Substation Name',
                   'Feeder GUID','Feeder Name'],

    'Regulator' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                   'X Coordinate', 'Y Coordinate','User Tag', 'Regulator Type','Controlling Phase',
                   'Regulator Winding Connection', 'Regulator Description, Phase A','Regulator Description, Phase B',
                   'Regulator Description, Phase C','Output Voltage, Phase A','Output Voltage, Phase B',
                   'Output Voltage, Phase C','LDC R Setting, Phase A','LDC R Setting, Phase B','LDC R Setting, Phase C',
                   'LDC X Setting, Phase A','LDC X Setting, Phase B','LDC X Setting, Phase C','House High Protector, Ph A',
                   '1st House High Protector, Ph B','1st House High Protector, Ph C','1st House Low Protector, Ph A',
                   '1st House Low Protector, Ph B','1st House Low Protector, Ph C','Failure Rate','Repair Time',
                   'Bypass Time','Regulator Bypass A','Regulator Bypass B','Regulator Bypass C','All Phases Same',
                   'Control Element','-','-','-','-','-','-','-','-','-','-','-','ceGUID','GUID','pGUID','Unused',
                   'mGUID','Phase A Energized','Phase B Energized','Phase C Energized','X5','Y5','Rotation Angle',
                   'Circuit Level','Substation GUID','Substation Name','Feeder GUID','Feeder Name'],

    'Transformer' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                     'X Coordinate', 'Y Coordinate','User Tag','Transformer Winding Connection','UNUSED',
                     'Rated Input Voltage (Src Side)','UNUSED','UNUSED','Rated Output Voltage (Load Side)',
                     'APCNF (Source Side Config)','Rated Tertiary Output Voltage','Tertiary Child Identifier',
                     'Nominal Output Voltage In kV.','Nominal Output Voltage of Tertiary In kV.','Tran kVA A',
                     'Tran kVA B','Tran kVA C','Failure Rate','Repair Time','Xfmr Cond Desc. Ph A','Xfmr Cond Desc. Ph B',
                     'Xfmr Cond Desc. Ph C','Is Center Tap','Transformer Mounting','-','-','-','-','-','-','-','-','-',
                     '-','-','-','-','-','-','-','-','-','-','-','GUID','pGUID','Unused','mGUID','Phase A Energized',
                     'Phase B Energized','Phase C Energized','X5','Y5','Rotation Angle','Circuit Level',
                     'Substation GUID','Substation Name','Feeder GUID','Feeder Name'],

    'Switch' :   ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                  'X Coordinate', 'Y Coordinate','User Tag','Switch Status','Switch ID','Partner Identifier',
                  'Failure Rate','Repair Time','Bypass Time In Hours','Close Time In Hours','Open Time In Hours',
                  'Element Specific','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                  '-', '-', '-', '-', '-', '-', '-', '-', '-', '-','-','ptnrGUID','GUID','pGUID','Unused','mGUID',
                  'Phase A Energized','Phase B Energized','Phase C Energized','X5','Y5','Rotation Angle','Circuit Level',
                  'Substation GUID','Substation Name','Feeder GUID','Feeder Name'],

    'Node' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number','X Coordinate',
              'Y Coordinate','User Tag','Feeder Number','Load Allocation Control Point','Load Mix Description',
              'Load Zone Description','Load Location','Load Growth','Billing Reference','Allocated kW, Phase A',
              'Allocated kW, Phase B','Allocated kW, Phase C','Allocated kvar, Phase A','Allocated kvar, Phase B',
              'Allocated kvar, Phase C','Allocated Consumers, Ph A','Allocated Consumers, Ph B',
              'Allocated Consumers, Ph C','Node Is Mandatory','Circuit Level', 'Load Interruptible Type','A Phase Parent',
              'B Phase Parent','C Phase Parent','IsMultiParent','Consumer Type','Feeder Color','A Phase Parent GUID',
              'B Phase Parent GUID','C Phase Parent GUID','-','-','-','-','-','-','-','-','-','-','-','-','-','GUID',
              'pGUID','Unused','mGUID','Phase A Energized','Phase B Energized','Phase C Energized','X8','Y8',
              'Rotation Angle','Circuit Level','Substation GUID','Substation Name','Feeder GUID','Feeder Name'],

    'Source' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                'X Coordinate', 'Y Coordinate','User Tag','Zsm Impedance Desc Minimum','Zsm Impedance Desc Maximum',
                'Substation Number','Bus Voltage','OH Ground Ohms for Min Fault','UG Ground Ohms for Min Fault',
                'Nominal Voltage','Load Allocation Control Point','Wye or Delta Connection Code','Regulation Code',
                'Failure Rate','Repair Time','Close Time','Open Time','Feeder Color 0x00RRGGBB','-','-','-','-','-','-',
                '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','GUID','pGUID','Unused',
                'mGUID','Phase A Energized','Phase B Energized','Phase C Energized','X9','Y9','Rotation Angle',
                'Circuit Level','Substation GUID','Substation Name','Feeder GUID','Feeder Name'],

    'Overcurrent Device' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                          'X Coordinate', 'Y Coordinate','User Tag','Description, Ph A','Description, Ph B',
                          'Description, Ph C','Is Closed, Phase A','Is Closed, Phase B','Is Closed, Phase C',
                          'Close All Phases Same as First Existing Phase','Load Allocation Control Point',
                          'Is Feeder Bay','Feeder Number','Feeder Color','Feeder Name','Failure Rate','Repair Time',
                          'Bypass Time','Close Time','Open Time','Coordination Failure Rate Failures/Yr',
                          'Fuse Coordination Method','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                          '-','-','-','-','-','GUID','pGUID','Unused','mGUID','Phase A Energized','Phase B Energized',
                          'Phase C Energized','X10','Y10','Rotation Angle','Circuit Level','Substation GUID',
                          'Substation Name','Feeder GUID','Feeder Name'],

    'Motor' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                'X Coordinate', 'Y Coordinate','User Tag', 'Steady State Cond. Description','Transient Cond. Description',
               'Sub Transident Cond. Desc.','Rated Voltage','Load Mix Description','Load Zone Description',
               'Load Location','Load Growth',"Allocated kW, Phase A","Allocated kW, Phase B","Allocated kW, Phase C",
               "Allocated kvar, Phase A","Allocated kvar, Phase B","Allocated kvar, Phase C",
               "Allocated Consumers, Phase A","Allocated Consumers, Phase B","Allocated Consumers, Phase C",
               'Model','Motor Status','Horse Power','Running Power Factor','% Efficiency','Rated LG kV','Drop Out Limit',
               'NEMA Type','Motor Start Limit','Motor Start Limited By','Soft Start Type','Soft Start Impedance',
               'Soft Start Impedance','Soft Start Tap','Soft Start Winding','Locked Rotor Power',
               'Locked Rotor Multiplier','Failure Rate','Repair Time','Using advanced model',
               'Advanced conductor equipment','Advanced input power','Percent Utilization','-','GUID','pGUID','Unused',
               'mGUID','Phase A Energized','Phase B Energized','Phase C Energized','X11','Y11','Rotation Angle',
               'Circuit Level','Substation GUID','Substation Name','Feeder GUID','Feeder Name'],

    'Generator' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                  'X Coordinate', 'Y Coordinate','User Tag','Steady State Cond. Description','Transient Cond. Description',
                   'Sub Transident Cond. Desc.','Rated Voltage','Load Mix Description','Load Zone Description',
                   'Load Location','Load Growth',"Allocated kW, Phase A","Allocated kW, Phase B","Allocated kW, Phase C",
                   "Allocated kvar, Phase A","Allocated kvar, Phase B","Allocated kvar, Phase C",
                   "Allocated Consumers, Phase A","Allocated Consumers, Phase B","Allocated Consumers, Phase C",'Model',
                   'Voltage to Hold','Voltage to Hold','Section to Hold Voltage At','kW Out','Maximum kW Out',
                   'Maximum kvar Lead Output','Maximum kvar Lagg Output','Rated Voltage for Gen. as Source',
                   'Wye or Delta Connection','Failure Rate','Repair Time','-','-','-','-','-','-','-','-','-','-','-','-',
                   'GUID','pGUID','Unused','mGUID','Phase A Energized','Phase B Energized','Phase C Energized','X12',
                   'Y12','Rotation Angle','Circuit Level','Substation GUID','Substation Name','Feeder GUID','Feeder Name'],

    'Consumer' : ['Element Name', 'Element Type', 'Phase Configuration', 'Parent Element Name', 'Map Number',
                  'X Coordinate', 'Y Coordinate','User Tag','Load Mix Description','Load Zone Description','Load Growth',
                  'Billing Code','Allocated kW (Ph A)','Allocated kW (Ph B)','Allocated kW (Ph C)','Allocated kvar (Ph A)',
                  'Allocated kvar (Ph B)','Allocated kvar (Ph C)','Allocated Consumers (Ph A)','Allocated Consumers (Ph B)',
                  'Allocated Consumers (Ph C)','Load Interruptible Type',"Is Consumer Active 0=Inactive, 1=Active",
                  'Consumer Type','Meter Number','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                  '-','-','-','-','-','-','GUID','pGUID','Unused','mGUID','Phase A Energized','Phase B Energized',
                  'Phase C Energized','X13','Y13','Rotation Angle','Circuit Level','Substation GUID','Substation Name',
                  'Feeder GUID','Feeder Name'],

}

seq_file_headings = {
    'Overhead Conductor' : ['Equipment Identifier','Equipment Type','Material','Carrying Capacity','Resistance @ 25',
                            'Resistance @ 50','Geometric Mean Radius','Preferred Neutral Description','Diameter',
                            'Named Equipment Category','Preferred Neutral Identifier','-','-','-','-','-','-','-','-',
                            '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                            '-','-','-','-','-','-','-','oGID'],

    'Underground Conductor' : ['Equipment Identifier','Equipment Type','Cable Type','Carrying Capacity In Amps',
                               'Phase Conductor Resistance Ohms/Mile','Geometric Mean Radius In Feet',
                               'Concentric Neutral Resist Ohms/Mile','# of Individual Strands in Neutral Default=0',
                               'OD of Cable Insulation In Feet','OD of Cable Including Neutral In Fee','Note Used',
                               'Dielectric Constant of Insulation Under Neutral ','Diameter Under Neutral In Feet',
                               'Not Used','kV Depreciated','Type Neutral Depreciated','GMR (Neutral) In Feed',
                               'Diameter of Conductor In Feet','Distance to CN In Feet','Named Equipment Category','-',
                               '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                               '-','-','-','-','-','-','oGID'],

    'Zsm Conductor' : ['Equipment Identifier','Equipment Type','Carrying Capacity','Types of Units (for display)',
                       'Base kVA','Base kV','Units (for display)','Self Impedance- R','Self Impedance- +jX',
                       'Self Impedance- +jB','Mutual Impedance- R','Mutual Impedance- +jX','Mutual Impedance- +jB',
                       'Positive Sequence- R','Positive Sequence- jX','Zero Sequence- R','Zero Sequence- jX',
                       'Mutual Reverse- R','Mutual Reverse- jX','Negative Sequence- R','Negative Sequence- jX',
                       'Named Equipment Category','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                       '-','-','-','-','-','-','-','-','-','-','oGID'],

    'Zabc Conductor' : ['Equipment Identifier','Equipment Type','Carrying Capacity','Types of Units (for display)',
                        'Base kVA','Base kV','Units','Impedance R-AA','Impedance jX-AA','Impedance R-AB',
                        'Impedance jX-AB','Impedance R-AC','Impedance jX-AC','Impedance R-BA','Impedance jX-BA',
                        'Impedance R-BB','Impedance jX-BB','Impedance R-BC','Impedance jX-BC','Impedance R-CA',
                        'Impedance jX-CA','Impedance R-CB','Impedance jX-CB','Impedance R-CC','Impedance jX-CC',
                        'Named Equipment Category','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                        '-','-','-','-','-','-','oGID'],


    'Transformer' : ['Equipment Identifier','Equipment Type','Ampacity','Type of Transformer Cond',
                     'Percent Impedance- Zps','Percent Impedance- Zpt','Percent Impedance- Zst','X/R Ratio- Phase A',
                     'X/R Ratio- Phase B','X/R Ratio- Phase C','Single Phase Base kVA- Zps','Single Phase Base kVA- Zpt',
                     'Single Phase Base kVA- Zst','Zgp- R Value','Zgs- R Value','Zg- R Value','Zgp- X Value',
                     'Zgs- X Value','Zg- X Value','K Factor','No-Load Loss- Zps','No-Load Loss- Zpt','No-Load Loss- Zst',
                     'Named Equipment Category','Single Phase Rated kVA- Zps','Single Phase Rated kVA- Zpt',
                     'Single Phase Rated kVA- Zst','Is Pad Mounted Transformer','-','-','-','-','-','-','-','-','-','-',
                     '-','-','-','-','-','-','-','-','-','-','-','oGID'],

    'Regulator' : ['Equipment Identifier','Equipment Type','Ampacity','CT Rating','% Boost','% Buck','Step Size',
                   'Bandwidth','Named Equipment Category','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                   '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                   'oGID'],

    'Load Mix' : ['Equipment Identifier','Equipment Type','Constant kVA','Constant IMP','Constant Current',
                  'Connection Code','Named Equipment Category','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                  '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                  '-','-','-','oGID'],

    'Construction Code' : ['Equipment Identifier','Equipment Type','OH Single Phase GMDP','OH V-Phase GMDP',
                           'OH 3-Phase GMPD','OH Single Phase GMDPN','OH V-Phase GMDPN','OH 3-Phase GMDPN','UG GMDP',
                           'Height Above Ground','Height Unit','Distance Between OD','Distance Unit','Spacing',
                           'Maximum Operating Voltage','Assume Full Transposition','Position of Single Phase',
                           'Position of First Phase','Position of Second Phase','Vertical Height Position- Phase A',
                           'Vertical Height Position- Phase B','Vertical Height Position- Phase C',
                           'Vertical Height Position- Neutral','Horizontal Distance Position- Phase A',
                           'Horizontal Distance Position- Phase B','Horizontal Distance Position- Phase C',
                           'Horizontal Distance Position- Neutral','Named Equipment Category','UG GMDPN','-','-','-',
                           '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','oGID'],

    'Load Zone' : ['Equipment Identifier','Equipment Type','Growth Rate','Named Equipment Category','-','-','-','-','-',
                   '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                   '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','oGID'],

    'Device' : ['Equipment Identifier','Equipment Type','Group','Current Rating','Max Symmetrical Fault',
                'Max Asymmetrical Fault','Minimum Pickup Ground','Nominal Voltage','Number of Fast Trip Phase',
                'Number of Slow Trip Phase','Electronic or Hydraulic','Use LightTable','LightTable Device Control',
                'LightTable Operating Device','Single Phase Operation','Named Equipment Category','Minimum Pickup Phase',
                'Has Phase Trip','Has Ground Trip','Number of Fast Trip Ground','Number of Slow Trip Ground','-','-','-',
                '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                'oGID'],

    'Protected Device' : ['Equipment Identifier','Equipment Type','Protected Device Desc.','Coordination Point 1',
                          'Coordination Point 2','Protected Device kV','Device kV','Transformation Multiplier',
                          'Type of Fault','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                          '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','oGID'],

    'Assemblies' : ['Equipment Identifier','Equipment Type','Named Equipment Category','Assembly Type',
                    'Associated Element Type','Assembly Description','-','-','-','-','-','-','-','-','-','-','-','-',
                    '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
                    '-','-','-','-','-','-','-','oGID'],

    'Switchgear' : ['Equipment Identifier','Equipment Type','Switchgear Type','Cabinet Count','Cabinet 1 Number',
                    'Cabinet 1 Type','Cabinet 1 Eq Phase A NAME','Cabinet 1 Eq Phase B NAME','Cabinet 1 Eq Phase C NAME',
                    'Cabinet 2 Number','Cabinet 2 Type','Cabinet 2 Eq Phase A NAME','Cabinet 2 Eq Phase B NAME',
                    'Cabinet 2 Eq Phase C NAME','Cabinet 3 Number','Cabinet 3 Type','Cabinet 3 Eq Phase A NAME',
                    'Cabinet 3 Eq Phase B NAME','Cabinet 3 Eq Phase C NAME','Cabinet 4 Number','Cabinet 4 Type',
                    'Cabinet 4 Eq Phase A NAME','Cabinet 4 Eq Phase B NAME','Cabinet 4 Eq Phase C NAME',
                    'Cabinet 5 Number','Cabinet 5 Type','Cabinet 5 Eq Phase A NAME','Cabinet 5 Eq Phase B NAME',
                    'Cabinet 5 Eq Phase C NAME','Cabinet 6 Number','Cabinet 6 Type','Cabinet 6 Eq Phase A NAME',
                    'Cabinet 6 Eq Phase B NAME','Cabinet 6 Eq Phase C NAME','Cabinet 7 Number','Cabinet 7 Type',
                    'Cabinet 7 Eq Phase A NAME','Cabinet 7 Eq Phase B NAME','Cabinet 7 Eq Phase C NAME',
                    'Cabinet 8 Number','Cabinet 8 Type','Cabinet 8 Eq Phase A NAME','Cabinet 8 Eq Phase B NAME',
                    'Cabinet 8 Eq Phase C NAME','Cabinet 9 Number','Cabinet 9 Type','Cabinet 9 Eq Phase A NAME',
                    'Cabinet 9 Eq Phase B NAME','Cabinet 9 Eq Phase C NAME','oGID'],

}
